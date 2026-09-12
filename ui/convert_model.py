import tensorflow as tf

model = tf.keras.models.load_model(
    "disease/models/tomato_disease_model.keras"
)

converter = tf.lite.TFLiteConverter.from_keras_model(model)

tflite_model = converter.convert()

with open(
    "disease/models/tomato_disease_model.tflite",
    "wb"
) as f:
    f.write(tflite_model)

print("DONE")