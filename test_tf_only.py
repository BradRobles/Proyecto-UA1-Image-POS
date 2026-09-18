import tensorflow as tf
from tensorflow.keras.models import load_model
model = load_model('modelo_ia/keras_model.h5', compile=False)
print("SUCCESS")
