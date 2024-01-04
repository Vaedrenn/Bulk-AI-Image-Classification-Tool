from __future__ import annotations

import os

import deepdanbooru as dd
import numpy as np
import PIL.Image
import tensorflow as tf

model_path = r'models/deepdanbooru-v3-20211112-sgd-e28/'


# loads the model from /models/
def load_model(model_path) -> tf.keras.Model:
    path = os.path.join(model_path, "model-resnet_custom_v3.h5")
    try:
        model = tf.keras.models.load_model(path)
    except FileNotFoundError as file_not_found_error:
        print("Model file not found:", file_not_found_error)
        return None
    except (IOError, OSError) as io_os_error:
        print("Error loading model:", io_os_error)
        return None
    return model


# read tags
def load_labels(model_path) -> list[str]:
    path = os.path.join(model_path, "tags.txt")
    try:
        with open(path) as f:
            labels = [line.strip() for line in f.readlines()]
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return []
    return labels


def predict(model, labels, image: PIL.Image.Image, score_threshold: float
            ) -> tuple[dict[str, float], dict[str, float], str]:
    _, height, width, _ = model.input_shape
    image = np.asarray(image)
    image = tf.image.resize(image,
                            size=(height, width),
                            method=tf.image.ResizeMethod.AREA,
                            preserve_aspect_ratio=True)
    image = image.numpy()
    image = dd.image.transform_and_pad_image(image, width, height)
    image = image / 255.
    probs = model.predict(image[None, ...])[0]
    probs = probs.astype(float)

    indices = np.argsort(probs)[::-1]
    result_all = dict()
    result_threshold = dict()
    for index in indices:
        label = labels[index]
        prob = probs[index]
        result_all[label] = prob
        if prob < score_threshold:
            break
        result_threshold[label] = prob
    result_text = ', '.join(result_all.keys())
    return result_threshold, result_all, result_text
