# test.py

import os
import numpy as np

from cuda_bootstrap import configure_conda_cuda_dlls

configure_conda_cuda_dlls()

import tensorflow as tf

import settings
from env import Env
from agent import PPOAgent


############################
# TEST AYARLARI
############################

TEST_EPISODES = 5
STEP_PRINT_EVERY = 50

# True ise policy mean kullanilir: a = tanh(mu)
# False ise train.py'deki stochastic sampling mantigi kullanilir
DETERMINISTIC_POLICY = True


############################
# MODEL YUKLEME
############################

def load_test_checkpoint(agent):
    """
    Test icin models klasorundeki en son modeli otomatik yukler.
    """
    update_id = settings.latest_index(
        os.path.join(settings.MODELS_DIR, f"{settings.MODEL_PREFIX}_up*.keras")
    )

    if update_id is None:
        raise FileNotFoundError(
            f"'{settings.MODELS_DIR}' icinde test edilecek model bulunamadi."
        )

    model_fp = settings.model_path(update_id)
    state_fp = settings.state_path(update_id)

    if not os.path.exists(model_fp):
        raise FileNotFoundError(f"Model dosyasi bulunamadi: {model_fp}")

    print(f"[TEST] Model yukleniyor -> Update {update_id}")
    agent.model = tf.keras.models.load_model(model_fp, compile=False)

    if os.path.exists(state_fp):
        settings.load_agent_state(agent, state_fp)
        print(f"[TEST] Agent state yuklendi -> {state_fp}")
    else:
        print(f"[TEST] Uyari: state dosyasi yok, sadece model yuklendi -> {state_fp}")

    return update_id


############################
# ACTION URETIMI
############################

def select_action(agent, state, deterministic=True):
    """
    deterministic=True:
        action = tanh(mu)
    deterministic=False:
        train.py'deki stochastic sampling mantigi kullanilir
    """
    if deterministic:
        s = tf.convert_to_tensor(state[None, :], dtype=tf.float32)
        thrust_mu, direction_logits, v = agent.model(s)

        thrust_mu = tf.squeeze(thrust_mu, axis=0)
        v = float(tf.squeeze(v, axis=0).numpy()[0])

        thrust_action = float(tf.tanh(thrust_mu).numpy()[0])
        direction_id = float(tf.argmax(direction_logits[0]).numpy())
        action = np.asarray([thrust_action, direction_id], dtype=np.float32)
        return action, v

    action, _, v = agent.act(state)
    return action, v


############################
# TEST MAIN
############################

if __name__ == "__main__":
    settings.setup_gpu()
    settings.ensure_model_dir()

    env = Env(settings.IP, settings.PORT)
    agent = PPOAgent()

    loaded_update = load_test_checkpoint(agent)

    total_returns = []
    total_lengths = []
    success_count = 0

    try:
        for ep in range(1, TEST_EPISODES + 1):
            raw_state, vector_state, state, start_info = env.reset()
            episode_id = env.episode_id

            ep_return = 0.0
            ep_len = 0
            done = False
            final_info = None

            print("=" * 80)
            print(
                f"[TEST EP {ep}/{TEST_EPISODES}] "
                f"episode_id={episode_id} | "
                f"model_update={loaded_update}"
            )
            print(
                f"[RESET] Target Pos=({start_info['reset_px']:.2f}, "
                f"{start_info['reset_py']:.2f}, {start_info['reset_pz']:.2f}) | "
                f"Rot=({start_info['reset_ry']:.2f}, {start_info['reset_rz']:.2f}) | "
                f"HeadingOffset={start_info['reset_heading_offset']:.2f}"
            )

            while not done:
                action, value = select_action(
                    agent=agent,
                    state=state,
                    deterministic=DETERMINISTIC_POLICY
                )

                next_state, reward, done, info = env.step(action)

                ep_return += reward
                ep_len += 1
                final_info = info

                if info["step_id"] % STEP_PRINT_EVERY == 0:
                    print(
                        f"[EP {episode_id:<4} | ST {info['step_id']:<4}] "
                        f"Dst={info['distance']:.2f} | "
                        f"Theta={info['theta_deg']:.2f}deg | "
                        f"Alpha={info['alpha_deg']:.2f}deg | "
                        f"Beta={info['beta_deg']:.2f}deg | "
                        f"Cls={info['closing_speed']:.2f} | "
                        f"AGL={info['agl']:.2f} | "
                        f"AltE={info['alt_error']:.2f} | "
                        f"R={reward:.3f} | "
                        f"V={value:.3f} | "
                        f"Dir={info.get('turn_direction_name', 'n/a')}#{info.get('turn_direction_id', '')} | "
                        f"Act=[{info['thrust']:.2f}, {info['clock_12_cmd']:.2f}, {info['clock_6_cmd']:.2f}, "
                        f"{info['clock_3_cmd']:.2f}, {info['clock_9_cmd']:.2f}]"
                    )

                state = next_state

            done_reason = final_info["done_reason"] if final_info is not None else "unknown"

            if done_reason == "success":
                success_count += 1

            total_returns.append(ep_return)
            total_lengths.append(ep_len)

            print("-" * 80)
            print(
                f"[EPISODE END] "
                f"episode_id={episode_id} | "
                f"done_reason={done_reason} | "
                f"return={ep_return:.3f} | "
                f"len={ep_len} | "
                f"final_distance={final_info['distance']:.2f} | "
                f"final_agl={final_info['agl']:.2f} | "
                f"final_theta={final_info.get('theta_deg', 0.0):.2f} | "
                f"final_alpha={final_info.get('alpha_deg', 0.0):.2f} | "
                f"final_beta={final_info.get('beta_deg', 0.0):.2f} | "
                f"final_alignment={final_info.get('alignment', 0.0):.2f}"
            )

        print("=" * 80)
        print("[TEST SUMMARY]")
        print(f"Model Update       : {loaded_update}")
        print(f"Episode Count      : {TEST_EPISODES}")
        print(f"Deterministic Mode : {DETERMINISTIC_POLICY}")
        print(f"Success Count      : {success_count}")
        print(f"Success Rate       : {100.0 * success_count / TEST_EPISODES:.2f}%")
        print(f"Mean Return        : {np.mean(total_returns):.3f}")
        print(f"Std Return         : {np.std(total_returns):.3f}")
        print(f"Mean Episode Len   : {np.mean(total_lengths):.2f}")
        print(f"Min Return         : {np.min(total_returns):.3f}")
        print(f"Max Return         : {np.max(total_returns):.3f}")

    finally:
        env.close()
