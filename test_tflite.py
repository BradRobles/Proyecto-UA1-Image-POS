import tensorflow as tf
interpreter = tf.lite.Interpreter(model_path="modelo_ia/model_unquant.tflite")
interpreter.allocate_tensors()
print("TFLITE SUCCESS")
