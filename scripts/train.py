# Train

#################  IMPORTS  ##################

import numpy as np
import tensorflow as tf

import log
import settings

from env import Env
from agent import PPOAgent

#################  MAIN RUNTIME  #############

if __name__ == "__main__":

    #################   AYARLAR  #################

    # GPU
    settings.setup_gpu()

    # Model
    settings.ensure_model_dir()

    # Log
    log.ensure_log_files()

    ################  OBJECTS  #####################

    # Enviroment
    env = Env(settings.IP, settings.PORT)

    # Agent
    agent = PPOAgent()


    ###############  CHECKPOINT  ###################

    start_update = settings.load_checkpoint(agent)

    ###############  LOOP COUNTERS & FIRST RESET ################

    episode_id = 0
    episode_return = 0.0
    episode_len = 0
    
    raw_state, vector_state, state, start_info = env.reset()
    episode_id = env.episode_id

    log.print_reset_console(episode_id, start_info)

    #############  UPDATE LOOP & ROLLOUT BUFFERS  ##############

    for update_id in range(start_update, settings.TOTAL_UPDATES):

        states = np.zeros((settings.ROLLOUT_LEN, agent.state_size), dtype=np.float32)
        actions = np.zeros((settings.ROLLOUT_LEN, agent.action_size), dtype=np.float32)
        old_logps = np.zeros((settings.ROLLOUT_LEN,), dtype=np.float32)
        rewards = np.zeros((settings.ROLLOUT_LEN,), dtype=np.float32)
        dones = np.zeros((settings.ROLLOUT_LEN,), dtype=np.float32)
        values = np.zeros((settings.ROLLOUT_LEN,), dtype=np.float32)
    

        ###############  ROLLOUT & STEP LOOP  #######################

        for t in range(settings.ROLLOUT_LEN):

            action, logp, value = agent.act(state)
            next_state, reward, done, info = env.step(action)

            states[t] = state
            actions[t] = action
            old_logps[t] = logp
            rewards[t] = reward
            dones[t] = 1.0 if done else 0.0
            values[t] = value

            episode_return += reward
            episode_len += 1

            log.append_step_csv(update_id+1, info)

            if info["step_id"] % log.STEP_PRINT_EVERY == 0:
                log.print_step_console(update_id + 1, info)
            
            if done:
                log.append_episode_csv(
                    update_id + 1,
                    episode_id,
                    episode_return,
                    episode_len,
                    info["done_reason"],
                    start_info,
                    info
                )

                log.print_episode_console(
                    episode_id,
                    episode_return,
                    episode_len,
                    info["done_reason"],
                    start_info,
                    info
                )

                episode_return = 0.0
                episode_len = 0
                
                
                raw_state, vector_state, state, start_info = env.reset()
                episode_id = env.episode_id

                log.print_reset_console(episode_id, start_info)
            
            else:
                state = next_state
        
        ###############  TRAINING MODEL  ################

        if done:
            last_value = 0.0
        else:
            s_tf = tf.convert_to_tensor(state[None,:], dtype=tf.float32)
            _, v_tf = agent.model(s_tf)
            last_value = float(tf.squeeze(v_tf, axis=0).numpy()[0])

        logs = agent.train(
            states,
            actions,
            old_logps,
            rewards,
            dones,
            values,
            last_value
        )

        #################  MODEL SAVE  ###################
        log.append_update_csv(update_id+1, logs, agent.gamma, agent.gae_lambda, agent.lr)
        log.print_update_console(update_id+1, logs)
        
        if (update_id+ 1) % settings.SAVE_EVERY_UPDATES == 0:
            print(f"[SAVE] Update {update_id+1}: Model Kaydediliyor...")
            settings.save_checkpoint(agent, update_id+1)
    
    ###############  FINISH TRAINING  #####################
    print("[FINAL SAVE] Eğitim tamamlandı. Son model kaydediliyor...")
    settings.save_checkpoint(agent, settings.TOTAL_UPDATES)

    env.close()



