import os

import numpy as np

from cuda_bootstrap import configure_conda_cuda_dlls

configure_conda_cuda_dlls()

import tensorflow as tf
from tensorflow.keras import Model  # type: ignore
from tensorflow.keras.layers import Dense, Input  # type: ignore
from tensorflow.keras.optimizers import Adam  # type: ignore

from env import ACTION_KEYS, STATE_KEYS, TURN_DIRECTION_COUNT

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
LOG_2PI = np.log(2.0 * np.pi).astype(np.float32)


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


class PPOAgent:
    def __init__(self):
        self.state_size = len(STATE_KEYS)
        self.action_size = len(ACTION_KEYS)
        self.direction_count = TURN_DIRECTION_COUNT
        self.lr = 2.5e-5
        self.gamma = 0.997
        self.gae_lambda = 0.97
        self.clip_eps = 0.08
        self.vf_coef = 0.5
        self.ent_coef = 0.006
        self.epochs = 4
        self.batch_size = 256
        self.max_grad_norm = 0.5
        self.target_kl = 0.006

        self.model = self.buildModel()
        self.log_std = tf.Variable(
            tf.zeros((1,), dtype=tf.float32),
            trainable=True,
            name="thrust_log_std",
        )
        self.opt = Adam(learning_rate=self.lr)
        self.model(tf.zeros((1, self.state_size), tf.float32))

    def buildModel(self):
        inp = Input(shape=(self.state_size,), dtype=tf.float32)
        x = Dense(512, activation="tanh")(inp)
        x = Dense(512, activation="tanh")(x)
        x = Dense(512, activation="tanh")(x)

        thrust_mu = Dense(1, activation=None, name="thrust_mu")(x)
        direction_logits = Dense(self.direction_count, activation=None, name="direction_logits")(x)
        v = Dense(1, activation=None, name="v")(x)

        return Model(inp, [thrust_mu, direction_logits, v])

    def value(self, state):
        s = tf.convert_to_tensor(state[None, :], tf.float32)
        _, _, v = self.model(s)
        return float(tf.squeeze(v, axis=0).numpy()[0])

    def act(self, state):
        s = tf.convert_to_tensor(state[None, :], tf.float32)
        thrust_mu, direction_logits, v = self.model(s)
        thrust_mu = tf.squeeze(thrust_mu, axis=0)
        v = float(tf.squeeze(v, axis=0).numpy()[0])

        std = tf.exp(self.log_std)
        eps = tf.random.normal((1,))
        pre_tanh = thrust_mu + std * eps
        thrust_action = tf.tanh(pre_tanh)

        direction_id = tf.random.categorical(direction_logits, 1)[0, 0]
        direction_logp_all = tf.nn.log_softmax(direction_logits, axis=-1)
        direction_logp = tf.gather(direction_logp_all[0], direction_id)

        thrust_logp_gauss = gaussian_log_prob(pre_tanh[None, :], thrust_mu[None, :], self.log_std[None, :])[0]
        thrust_correction = tf.reduce_sum(tf.math.log(1.0 - thrust_action * thrust_action + 1e-6))
        logp = float((thrust_logp_gauss - thrust_correction + direction_logp).numpy())

        action = np.asarray(
            [float(thrust_action.numpy()[0]), float(direction_id.numpy())],
            dtype=np.float32,
        )
        return action, logp, v

    def calculateGAE(self, rewards, dones, values, last_value):
        T = len(rewards)
        adv = np.zeros(T, dtype=np.float32)
        last_gae = 0.0

        for t in reversed(range(T)):
            nonterm = 1.0 - dones[t]
            v_next = last_value if t == T - 1 else values[t + 1]
            delta = rewards[t] + self.gamma * v_next * nonterm - values[t]
            last_gae = delta + self.gamma * self.gae_lambda * nonterm * last_gae
            adv[t] = last_gae

        ret = adv + values
        return adv, ret

    def train_step(self, obs, act, old_logp, adv, ret):
        thrust_act = act[:, 0:1]
        direction_ids = tf.cast(
            tf.clip_by_value(tf.round(act[:, 1]), 0.0, float(self.direction_count - 1)),
            tf.int32,
        )

        with tf.GradientTape() as tape:
            thrust_mu, direction_logits, v = self.model(obs)
            v = tf.squeeze(v, axis=-1)

            pre_tanh = atanh(thrust_act)
            thrust_logp_gauss = gaussian_log_prob(pre_tanh, thrust_mu, self.log_std[None, :])
            thrust_correction = tf.reduce_sum(
                tf.math.log(1.0 - thrust_act * thrust_act + 1e-6),
                axis=-1,
            )
            thrust_logp = thrust_logp_gauss - thrust_correction

            direction_logp_all = tf.nn.log_softmax(direction_logits, axis=-1)
            direction_logp = tf.gather(direction_logp_all, direction_ids, batch_dims=1)
            logp = thrust_logp + direction_logp

            ratio = tf.exp(logp - old_logp)
            surr1 = ratio * adv
            surr2 = tf.clip_by_value(ratio, 1.0 - self.clip_eps, 1.0 + self.clip_eps) * adv
            policy_loss = -tf.reduce_mean(tf.minimum(surr1, surr2))

            value_loss = 0.5 * tf.reduce_mean(tf.square(ret - v))

            direction_probs = tf.nn.softmax(direction_logits, axis=-1)
            direction_entropy = -tf.reduce_sum(direction_probs * direction_logp_all, axis=-1)
            thrust_entropy = gaussian_entropy(self.log_std[None, :])
            ent = tf.reduce_mean(direction_entropy + thrust_entropy)

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

        logs = {
            "loss": 0.0,
            "policy_loss": 0.0,
            "value_loss": 0.0,
            "entropy": 0.0,
            "kl": 0.0,
            "clip_frac": 0.0,
        }
        steps = 0

        for _ in range(self.epochs):
            np.random.shuffle(idx)
            epoch_kl = 0.0
            epoch_steps = 0

            for start in range(0, n, self.batch_size):
                mb = idx[start:start + self.batch_size]
                loss, pl, vl, ent, kl, cf = self.train_step(
                    tf.gather(obs, mb),
                    tf.gather(act, mb),
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
                epoch_kl += float(kl.numpy())
                epoch_steps += 1

            if self.target_kl and epoch_steps > 0:
                mean_epoch_kl = epoch_kl / epoch_steps
                if mean_epoch_kl > self.target_kl:
                    break

        for k in logs:
            logs[k] /= max(1, steps)
        return logs
