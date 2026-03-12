import re
import os
import glob
import gzip
import pickle
import warnings
import numpy as np
import tensorflow as tf

warnings.filterwarnings("ignore")

IP = "127.0.0.1"
PORT = 5050

ROLLOUT_LEN = 512
TOTAL_UPDATES = 10
SAVE_EVERY_UPDATES = 5

MODELS_DIR = "models"
MODEL_PREFIX = "ppo_model"
STATE_PREFIX = "ppo_state"

def as_float32(x):
    return np.asarray(x, dtype=np.float32)

def setup_gpu():

    gpus = tf.config.experimental.list_physical_devices("GPU")

    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"-- {len(gpus)} GPU Bulundu ve yapılandırıldı.")
            return True
        except RuntimeError as e:
            print(f"GPU yapılandırma uyarısı: {e}")
            return True
        
    else:
        print("GPU Bulunamadı, CPU Kullanılacak.")
        return False
    

def ensure_model_dir():
    os.makedirs(MODELS_DIR, exist_ok=True)

def model_path(update_id):
    return os.path.join(MODELS_DIR, f"{MODEL_PREFIX}_up{update_id}.keras")

def state_path(update_id):
    return os.path.join(MODELS_DIR, f"{STATE_PREFIX}_up{update_id}.pkl.gz")

def save_agent_state(agent, path, extra = None):
    state = {
        "log_std": agent.log_std.numpy().tolist()
    }

    if extra is not None:
        state.update(extra)
    
    tmp_path = path + ".tmp"

    with gzip.open(tmp_path, "wb") as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    os.replace(tmp_path, path)

def load_agent_state(agent, path):
    if not os.path.exists(path):
        return {}
    
    with gzip.open(path, "rb") as f:
        state = pickle.load(f)
    
    if "log_std" in state:
        agent.log_std.assign(np.array(state["log_std"], dtype=np.float32))
    
    return state
 
def latest_index(pattern, regex=r"_up(\d+)\.keras$"):
    files = glob.glob(pattern)

    if not files:
        return None
    
    nums = []

    for p in files:
        match = re.search(regex, os.path.basename(p))
        if match:
            nums.append(int(match.group(1)))
        
    return max(nums) if nums else None

def load_checkpoint(agent):
    start_update = 0
    last_up = latest_index(os.path.join(MODELS_DIR, f"{MODEL_PREFIX}_up*.keras"))

    if last_up is not None:
        print(f"Kayıtlı model bulundu: Update {last_up}. Yükleniyor...")
        try:
            agent.model = tf.keras.models.load_model(
                model_path(last_up),
                compile=False
            )
            load_agent_state(agent, state_path(last_up))
            start_update = last_up + 1
            print(f">>> Başarılı! Update {start_update} seviyesinden devam ediliyor")
        except Exception as e:
            print(f"HATA: Model Yüklenemedi. Sıfırdan başlanıyor. {e}")
            start_update = 0

    return start_update

def save_checkpoint(agent, update_id):
    agent.model.save(model_path(update_id))
    save_agent_state(
        agent,
        state_path(update_id),
        extra={"update": update_id}
    )