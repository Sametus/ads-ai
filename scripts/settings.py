import os
import warnings

import numpy as np

from cuda_bootstrap import configure_conda_cuda_dlls

# TensorFlow import edilmeden once CUDA/cuDNN DLL yollarini ekliyoruz.
# Bu satir olmazsa rl_codes ortaminda DLL'ler mevcut olsa bile GPU gorunmeyebilir.
configure_conda_cuda_dlls()

import tensorflow as tf

warnings.filterwarnings("ignore")

IP = "127.0.0.1"
PORT = 5005

MODELS_DIR = "models"

# V15 aktif egitim hatti sadece SAC'tir.
# Eski egitim hatlarina ait checkpoint isimleri bilincli olarak bu surumden cikarildi.
SAC_MODEL_PREFIX = "sac_v15_1_2_guidance_accel_launch_guard_target500_y100"
SAC_TOTAL_STEPS = 250000
SAC_BATCH_SIZE = 64
SAC_REPLAY_SIZE = 200000
SAC_START_TRAINING_STEPS = 8000
SAC_TRAIN_EVERY_STEPS = 32
SAC_UPDATES_PER_STEP = 1
SAC_SAVE_EVERY_STEPS = 5000
SAC_LOG_EVERY_STEPS = 500
SAC_GAMMA = 0.995
SAC_TAU = 0.005
SAC_ACTOR_LR = 3.0e-5
SAC_CRITIC_LR = 1.0e-4
SAC_ALPHA_LR = 3.0e-5
SAC_INITIAL_ALPHA = 0.25
SAC_REWARD_SCALE = 0.02
SAC_HIDDEN_UNITS = 96


def as_float32(x):
    """Sayisal veriyi TensorFlow/Numpy icin standart float32 formuna cevirir."""
    return np.asarray(x, dtype=np.float32)


def setup_gpu():
    """GPU varsa memory growth acar; yoksa CPU ile devam eder."""
    gpus = tf.config.experimental.list_physical_devices("GPU")

    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"-- {len(gpus)} GPU bulundu ve yapilandirildi.")
            return True
        except RuntimeError as e:
            print(f"GPU yapilandirma uyarisi: {e}")
            return True

    print("GPU bulunamadi, CPU kullanilacak.")
    return False


def ensure_model_dir():
    """SAC checkpoint klasorunu olusturur."""
    os.makedirs(MODELS_DIR, exist_ok=True)
