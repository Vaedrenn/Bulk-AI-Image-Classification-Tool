from __future__ import annotations
import tensorflow as tf


# loads the model from /models/
def load_model() -> tf.keras.Model:
    path = r'models/deepdanbooru-v3-20211112-sgd-e28/model-resnet_custom_v3.h5'
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
def load_labels() -> list[str]:
    path = r'models/deepdanbooru-v3-20211112-sgd-e28/tags.txt'
    try:
        with open(path) as f:
            labels = [line.strip() for line in f.readlines()]
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return []
    return labels
