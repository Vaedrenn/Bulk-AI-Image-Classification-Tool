from __future__ import annotations

import os

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
