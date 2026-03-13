import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras import Model

print("TF version:", tf.__version__)

inp = Input(shape=(20,), dtype=tf.float32)
x = Dense(256, activation="tanh")(inp)
x = Dense(256, activation="tanh")(x)
out = Dense(3)(x)

model = Model(inp, out)

print("Model kuruldu.")
model.summary()