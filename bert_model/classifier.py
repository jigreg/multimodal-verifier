import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text  # noqa
import numpy as np

model = tf.keras.models.load_model("foreign_company_classifier_v2.h5")
bert_preprocess = hub.load("https://tfhub.dev/tensorflow/bert_multi_cased_preprocess/3")
bert_encoder = hub.load("https://tfhub.dev/tensorflow/bert_multi_cased_L-12_H-768_A-12/4")

def predict_label(company="", ceo="", address=""):
    combined_text = " ".join([company, ceo, address]).strip()
    if not combined_text:
        return None, 0.0
    inputs = bert_preprocess(tf.constant([combined_text]))
    embedding = bert_encoder(inputs)["pooled_output"]
    prob = float(model.predict(embedding)[0][0])
    label = "의심" if prob >= 0.5 else "안심"
    return label, prob