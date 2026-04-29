import glob
import gzip
import os
import pickle
import re

import numpy as np

from cuda_bootstrap import configure_conda_cuda_dlls

# TensorFlow yuklenmeden once env icindeki CUDA/cuDNN DLL yolunu ekler.
configure_conda_cuda_dlls()

import tensorflow as tf
from tensorflow.keras import Model  # type: ignore
from tensorflow.keras.initializers import Constant  # type: ignore
from tensorflow.keras.layers import Concatenate, Dense, Input  # type: ignore
from tensorflow.keras.optimizers import Adam  # type: ignore

import settings
from env import ACTION_KEYS, STATE_KEYS

LOG_2PI = np.log(2.0 * np.pi).astype(np.float32)
EPS = 1e-6


class ReplayBuffer:
    """SAC icin gecmis deneyleri saklayan sade replay buffer."""

    def __init__(self, state_size, action_size, capacity):
        self.capacity = int(capacity)
        self.ptr = 0
        self.size = 0

        self.states = np.zeros((self.capacity, state_size), dtype=np.float32)
        self.actions = np.zeros((self.capacity, action_size), dtype=np.float32)
        self.rewards = np.zeros((self.capacity, 1), dtype=np.float32)
        self.next_states = np.zeros((self.capacity, state_size), dtype=np.float32)
        self.dones = np.zeros((self.capacity, 1), dtype=np.float32)

    def add(self, state, action, reward, next_state, done):
        """Tek transition ekler; kapasite dolunca en eski verinin ustune yazar."""
        self.states[self.ptr] = np.asarray(state, dtype=np.float32)
        self.actions[self.ptr] = np.asarray(action, dtype=np.float32)
        self.rewards[self.ptr, 0] = float(reward)
        self.next_states[self.ptr] = np.asarray(next_state, dtype=np.float32)
        self.dones[self.ptr, 0] = 1.0 if done else 0.0

        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size):
        """Replay buffer'dan rastgele mini-batch secer."""
        idx = np.random.randint(0, self.size, size=int(batch_size))
        return {
            "states": self.states[idx],
            "actions": self.actions[idx],
            "rewards": self.rewards[idx],
            "next_states": self.next_states[idx],
            "dones": self.dones[idx],
        }


class SACAgent:
    """
    Soft Actor-Critic ajan.

    Bu surum sifirdan baslar: hazir veri veya eski checkpoint kullanmaz.
    Replay buffer sayesinde gecmis adimlar tekrar kullanilir ve actor/critic birlikte ogrenir.
    """

    def __init__(self):
        self.state_size = len(STATE_KEYS)
        self.action_size = len(ACTION_KEYS)

        self.gamma = float(settings.SAC_GAMMA)
        self.tau = float(settings.SAC_TAU)
        self.reward_scale = float(settings.SAC_REWARD_SCALE)
        self.target_entropy = -float(self.action_size)
        self.loaded_checkpoint = False

        self.actor = self.build_actor()
        self.q1 = self.build_critic("q1")
        self.q2 = self.build_critic("q2")
        self.target_q1 = self.build_critic("target_q1")
        self.target_q2 = self.build_critic("target_q2")

        self.actor_opt = Adam(learning_rate=float(settings.SAC_ACTOR_LR))
        self.q1_opt = Adam(learning_rate=float(settings.SAC_CRITIC_LR))
        self.q2_opt = Adam(learning_rate=float(settings.SAC_CRITIC_LR))
        self.alpha_opt = Adam(learning_rate=float(settings.SAC_ALPHA_LR))

        self.log_alpha = tf.Variable(
            np.log(float(settings.SAC_INITIAL_ALPHA)).astype(np.float32),
            trainable=True,
            name="log_alpha",
        )

        dummy_state = tf.zeros((1, self.state_size), tf.float32)
        dummy_action = tf.zeros((1, self.action_size), tf.float32)
        self.actor(dummy_state)
        self.q1([dummy_state, dummy_action])
        self.q2([dummy_state, dummy_action])
        self.target_q1([dummy_state, dummy_action])
        self.target_q2([dummy_state, dummy_action])
        self.hard_update_targets()

    @property
    def alpha(self):
        """Entropy katsayisi; buyukse daha fazla kesif, kucukse daha kararli action."""
        return tf.exp(self.log_alpha)

    def build_actor(self):
        """State -> action dagilimi ureten actor agi."""
        inp = Input(shape=(self.state_size,), dtype=tf.float32)
        hidden = int(settings.SAC_HIDDEN_UNITS)
        x = Dense(hidden, activation="relu")(inp)
        x = Dense(hidden, activation="relu")(x)
        x = Dense(hidden, activation="relu")(x)

        mu = Dense(self.action_size, activation=None, name="action_mu")(x)
        log_std = Dense(
            self.action_size,
            activation=None,
            bias_initializer=Constant(-1.0),
            name="action_log_std",
        )(x)

        return Model(inp, [mu, log_std], name="sac_actor")

    def build_critic(self, name):
        """Q agi: state ve action birlikte verilir, beklenen getiriyi tahmin eder."""
        state_in = Input(shape=(self.state_size,), dtype=tf.float32, name=f"{name}_state")
        action_in = Input(shape=(self.action_size,), dtype=tf.float32, name=f"{name}_action")
        hidden = int(settings.SAC_HIDDEN_UNITS)
        x = Concatenate()([state_in, action_in])
        x = Dense(hidden, activation="relu")(x)
        x = Dense(hidden, activation="relu")(x)
        x = Dense(hidden, activation="relu")(x)
        q = Dense(1, activation=None, name=f"{name}_q")(x)
        return Model([state_in, action_in], q, name=name)

    def sample_action_tensor(self, states, deterministic=False):
        """Squashed Gaussian action uretir; tanh sonucu action [-1, 1] araliginda kalir."""
        mu, log_std = self.actor(states)
        log_std = tf.clip_by_value(log_std, -5.0, 1.0)

        if deterministic:
            pre_tanh = mu
        else:
            std = tf.exp(log_std)
            pre_tanh = mu + std * tf.random.normal(tf.shape(mu))

        action = tf.tanh(pre_tanh)
        gaussian_logp = -0.5 * (
            ((pre_tanh - mu) / (tf.exp(log_std) + EPS)) ** 2
            + 2.0 * log_std
            + LOG_2PI
        )
        gaussian_logp = tf.reduce_sum(gaussian_logp, axis=-1, keepdims=True)
        tanh_correction = tf.reduce_sum(
            tf.math.log(1.0 - tf.square(action) + EPS),
            axis=-1,
            keepdims=True,
        )
        logp = gaussian_logp - tanh_correction
        return action, logp

    def act(self, state, deterministic=False):
        """Numpy state alir, Unity'ye gonderilecek normalized action dondurur."""
        states = tf.convert_to_tensor(state[None, :], tf.float32)
        action, logp = self.sample_action_tensor(states, deterministic=deterministic)
        return action.numpy()[0].astype(np.float32), float(logp.numpy()[0, 0])

    def train_step(self, replay_buffer, batch_size):
        """Bir SAC mini-batch update'i yapar."""
        batch = replay_buffer.sample(batch_size)
        states = tf.convert_to_tensor(batch["states"], tf.float32)
        actions = tf.convert_to_tensor(batch["actions"], tf.float32)
        rewards = tf.convert_to_tensor(batch["rewards"], tf.float32) * self.reward_scale
        next_states = tf.convert_to_tensor(batch["next_states"], tf.float32)
        dones = tf.convert_to_tensor(batch["dones"], tf.float32)

        next_actions, next_logp = self.sample_action_tensor(next_states)
        target_q = tf.minimum(
            self.target_q1([next_states, next_actions]),
            self.target_q2([next_states, next_actions]),
        )
        target_value = target_q - self.alpha * next_logp
        backup = rewards + self.gamma * (1.0 - dones) * target_value
        backup = tf.stop_gradient(backup)

        with tf.GradientTape() as tape_q1:
            q1_pred = self.q1([states, actions])
            q1_loss = tf.reduce_mean(tf.square(q1_pred - backup))
        q1_grads = tape_q1.gradient(q1_loss, self.q1.trainable_variables)
        self.q1_opt.apply_gradients(zip(q1_grads, self.q1.trainable_variables))

        with tf.GradientTape() as tape_q2:
            q2_pred = self.q2([states, actions])
            q2_loss = tf.reduce_mean(tf.square(q2_pred - backup))
        q2_grads = tape_q2.gradient(q2_loss, self.q2.trainable_variables)
        self.q2_opt.apply_gradients(zip(q2_grads, self.q2.trainable_variables))

        with tf.GradientTape() as tape_actor:
            new_actions, logp = self.sample_action_tensor(states)
            q_new = tf.minimum(
                self.q1([states, new_actions]),
                self.q2([states, new_actions]),
            )
            actor_loss = tf.reduce_mean(self.alpha * logp - q_new)
        actor_grads = tape_actor.gradient(actor_loss, self.actor.trainable_variables)
        self.actor_opt.apply_gradients(zip(actor_grads, self.actor.trainable_variables))

        with tf.GradientTape() as tape_alpha:
            _, logp_for_alpha = self.sample_action_tensor(states)
            alpha_loss = -tf.reduce_mean(
                self.log_alpha * tf.stop_gradient(logp_for_alpha + self.target_entropy)
            )
        alpha_grads = tape_alpha.gradient(alpha_loss, [self.log_alpha])
        self.alpha_opt.apply_gradients(zip(alpha_grads, [self.log_alpha]))

        self.soft_update_targets()

        entropy = -tf.reduce_mean(logp)
        total_loss = q1_loss + q2_loss + actor_loss + alpha_loss
        return {
            "loss": float(total_loss.numpy()),
            "policy_loss": float(actor_loss.numpy()),
            "value_loss": float((q1_loss + q2_loss).numpy()),
            "entropy": float(entropy.numpy()),
            "kl": float(alpha_loss.numpy()),
            "clip_frac": float(self.alpha.numpy()),
            "q1_loss": float(q1_loss.numpy()),
            "q2_loss": float(q2_loss.numpy()),
            "alpha": float(self.alpha.numpy()),
        }

    def hard_update_targets(self):
        """Target critic'leri ana critic'lerle ayni yapar."""
        self.target_q1.set_weights(self.q1.get_weights())
        self.target_q2.set_weights(self.q2.get_weights())

    def soft_update_targets(self):
        """Target critic'leri yavasca gunceller; SAC stabilitesinin ana parcasi."""
        for target_var, source_var in zip(self.target_q1.variables, self.q1.variables):
            target_var.assign((1.0 - self.tau) * target_var + self.tau * source_var)
        for target_var, source_var in zip(self.target_q2.variables, self.q2.variables):
            target_var.assign((1.0 - self.tau) * target_var + self.tau * source_var)

    def actor_path(self, step_id):
        return os.path.join(settings.MODELS_DIR, f"{settings.SAC_MODEL_PREFIX}_actor_step{step_id}.keras")

    def q1_path(self, step_id):
        return os.path.join(settings.MODELS_DIR, f"{settings.SAC_MODEL_PREFIX}_q1_step{step_id}.keras")

    def q2_path(self, step_id):
        return os.path.join(settings.MODELS_DIR, f"{settings.SAC_MODEL_PREFIX}_q2_step{step_id}.keras")

    def state_path(self, step_id):
        return os.path.join(settings.MODELS_DIR, f"{settings.SAC_MODEL_PREFIX}_state_step{step_id}.pkl.gz")

    def latest_checkpoint_step(self):
        """Aktif SAC prefix'i ile kaydedilmis en son checkpoint step'ini bulur."""
        pattern = os.path.join(settings.MODELS_DIR, f"{settings.SAC_MODEL_PREFIX}_actor_step*.keras")
        steps = []
        for path in glob.glob(pattern):
            match = re.search(r"_step(\d+)\.keras$", os.path.basename(path))
            if match:
                steps.append(int(match.group(1)))
        return max(steps) if steps else None

    def save_checkpoint(self, step_id):
        """Actor, critic ve alpha durumunu SAC checkpoint olarak kaydeder."""
        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        self.actor.save(self.actor_path(step_id))
        self.q1.save(self.q1_path(step_id))
        self.q2.save(self.q2_path(step_id))

        tmp_path = self.state_path(step_id) + ".tmp"
        with gzip.open(tmp_path, "wb") as f:
            pickle.dump({"step": int(step_id), "log_alpha": float(self.log_alpha.numpy())}, f)
        os.replace(tmp_path, self.state_path(step_id))

    def load_checkpoint(self):
        """Son SAC checkpoint varsa yukler; yoksa sifirdan baslar."""
        step_id = self.latest_checkpoint_step()
        if step_id is None:
            self.loaded_checkpoint = False
            return 0

        print(f"[SAC] Kayitli checkpoint bulundu: step {step_id}. Yukleniyor...")
        self.actor = tf.keras.models.load_model(self.actor_path(step_id), compile=False)
        self.q1 = tf.keras.models.load_model(self.q1_path(step_id), compile=False)
        self.q2 = tf.keras.models.load_model(self.q2_path(step_id), compile=False)
        self.hard_update_targets()

        state_path = self.state_path(step_id)
        if os.path.exists(state_path):
            with gzip.open(state_path, "rb") as f:
                state = pickle.load(f)
            if "log_alpha" in state:
                self.log_alpha.assign(np.float32(state["log_alpha"]))

        print(f"[SAC] step {step_id} seviyesinden devam edilecek.")
        self.loaded_checkpoint = True
        return int(step_id)
