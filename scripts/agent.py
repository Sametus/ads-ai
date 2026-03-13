# Imports
import numpy as np
import os

from tensorflow.keras.layers import Dense, Input # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras import Model # type: ignore
import tensorflow as tf
# Yapılandırma ve Sabitler

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
LOG_2PI = np.log(2.0 * np.pi).astype(np.float32)

# Yarcımı Fonksiyonlar

def atanh(x):
    eps = 1e-6
    x = tf.clip_by_value(x, -1.0 + eps, 1.0 - eps)
    return 0.5 * tf.math.log((1.0 + x) / (1.0 - x))

def gaussian_log_prob(x, mu, log_std):
    var = tf.exp(2.0 * log_std)
    logp = -0.5 * (((x - mu) ** 2) / (var + 1e-8) + 2.0 * log_std + LOG_2PI)
    return tf.reduce_sum(logp, axis=-1)

def gaussian_entropy(log_std):
    return tf.reduce_sum(log_std + 0.5 * (LOG_2PI + 1.0), axis=-1)

# Agent Class

class PPOAgent:
    def __init__(self):
        self.state_size = 20
        self.action_size = 3
        self.lr = 1e-4
        self.gamma = 0.99
        self.gae_lambda = 0.95
        self.clip_eps = 0.1
        self.vf_coef = 0.5
        self.ent_coef = 0.02
        self.epochs = 4
        self.batch_size = 256
        self.max_grad_norm = 0.5

        self.model = self.buildModel()

        self.log_std = tf.Variable(0.0*tf.ones((self.action_size), dtype=tf.float32),
                                   trainable=True,
                                   name="log_std",)
        self.opt = Adam(learning_rate = self.lr)

        tmp = self.model(tf.zeros((1,self.state_size), tf.float32))

    def buildModel(self):
        inp = Input(shape=(self.state_size,), dtype = tf.float32)
        x = Dense(256, activation = "tanh")(inp)
        x = Dense(512, activation="tanh")(x)
        x = Dense(256, activation="tanh")(x)

        mu = Dense(self.action_size, activation=None, name = "mu")(x)
        v = Dense(1, activation=None, name = "v")(x)

        return Model(inp,[mu,v])

    def act(self,state):
        s = tf.convert_to_tensor(state[None,:], tf.float32)
        mu, v = self.model(s)
        mu = tf.squeeze(mu,0)
        v = float(tf.squeeze(v,0).numpy())

        std = tf.exp(self.log_std)
        eps = tf.random.normal((self.action_size,))
        pre_tanh = mu + std * eps
        a = tf.tanh(pre_tanh)

        logp_gauss = gaussian_log_prob(pre_tanh[None, :], mu[None, :], self.log_std[None,:])[0]
        correction = tf.reduce_sum(tf.math.log(1.0 - a*a+1e-6))
        logp = float((logp_gauss - correction).numpy())

        return a.numpy().astype(np.float32), logp, v


    def calculateGAE(self, rewards, dones, values, last_value):
        T = len(rewards)
        adv = np.zeros(T, dtype=np.float32)
        last_gae = 0.0

        for t in reversed(range(T)):
            nonterm = 1.0 - dones[t]
            v_next = last_value if t == T -1 else values[t+1]
            delta = rewards[t] + self.gamma * v_next * nonterm - values[t]
            last_gae = delta + self.gamma * self.gae_lambda * nonterm * last_gae
            adv[t] = last_gae

        ret = adv + values
        return adv, ret

    def train_step(self, obs, act_tanh, old_logp, adv, ret):
        with tf.GradientTape() as tape:
            mu, v = self.model(obs)
            v = tf.squeeze(v,axis=-1)

            pre_tanh = atanh(act_tanh)
            logp_gauss = gaussian_log_prob(pre_tanh, mu, self.log_std[None,:])
            correction = tf.reduce_sum(tf.math.log(1.0 - act_tanh * act_tanh + 1e-6), axis=-1)
            logp = logp_gauss - correction

            ratio = tf.exp(logp - old_logp)
            surr1 = ratio * adv
            surr2 = tf.clip_by_value(ratio, 1.0 - self.clip_eps, 1.0 + self.clip_eps) * adv
            policy_loss = -tf.reduce_mean(tf.minimum(surr1,surr2))

            value_loss = 0.5 * tf.reduce_mean(tf.square(ret - v))

            ent = tf.reduce_mean(gaussian_entropy(self.log_std[None,:]))

            loss = policy_loss + self.vf_coef * value_loss - self.ent_coef * ent

        vars_ = self.model.trainable_variables + [self.log_std]
        grads = tape.gradient(loss, vars_)

        if self.max_grad_norm and self.max_grad_norm > 0:
            grads, _ = tf.clip_by_global_norm(grads, self.max_grad_norm)
        self.opt.apply_gradients(zip(grads, vars_))
        
        approx_kl = tf.reduce_mean(old_logp - logp)
        clip_frac = tf.reduce_mean(tf.cast(tf.abs(ratio - 1.0) > self.clip_eps, tf.float32))

        return loss, policy_loss, value_loss, ent, approx_kl, clip_frac
    
        

    def train(self, states, actions, old_logps, rewards, dones, values, last_value):
        adv, ret = self.calculateGAE(rewards, dones, values, last_value)

        adv = (adv - adv.mean()) / (adv.std() + 1e-8)

        obs = tf.convert_to_tensor(states, tf.float32)
        act = tf.convert_to_tensor(actions, tf.float32)
        old_lp = tf.convert_to_tensor(old_logps, tf.float32)
        adv_t = tf.convert_to_tensor(adv, tf.float32)
        ret_t = tf.convert_to_tensor(ret, tf.float32)

        n = states.shape[0]
        idx = np.arange(n)

        logs = {"loss":0.0,"policy_loss":0.0,"value_loss":0.0, "entropy":0.0,"kl":0.0,"clip_frac":0.0}
        steps = 0

        for _ in range(self.epochs):
            np.random.shuffle(idx)
            for start in range(0,n,self.batch_size):
                mb = idx[start:start+self.batch_size]
                loss, pl, vl, ent, kl, cf = self.train_step(
                    tf.gather(obs, mb),
                    tf.gather(act,mb),
                    tf.gather(old_lp, mb),
                    tf.gather(adv_t, mb),
                    tf.gather(ret_t, mb),
                )
                logs["loss"] += float(loss.numpy())
                logs["policy_loss"] += float(pl.numpy())
                logs["value_loss"] += float(vl.numpy())
                logs["entropy"] += float(ent.numpy())
                logs["kl"] += float(kl.numpy())
                logs["clip_frac"] += float(cf.numpy())
                steps += 1
        
        for k in logs:
            logs[k] /= max(1,steps)
        return logs

