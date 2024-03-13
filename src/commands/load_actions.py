from __future__ import annotations

import os

import tensorflow as tf


def load_model(model_path: str | os.path) -> tf.keras.Model:
    """
    Loads models model_path, should be called before using predict
    :param model_path: file name
    :return: returns the loaded model
    """
    file_name = "model-resnet_custom_v3.h5"
    path = os.path.join(model_path, file_name)

    try:
        print("Loading model")
        model = tf.keras.models.load_model(path)
    except FileNotFoundError as file_not_found_error:
        print("Model file not found:", file_not_found_error)
        return None
    except (IOError, OSError) as io_os_error:
        print("Error loading model:", io_os_error)
        return None
    print("Finished Loading models")
    return model


# read tags
def load_labels(model_path: str | os.path) -> list[str]:
    """
    Loads labels from  txt file
    :param model_path: file name
    :return: list of tags(labels)
    """
    path = os.path.join(model_path, "tags.txt")
    try:
        with open(path) as f:
            labels = [line.strip() for line in f.readlines()]
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return []
    return labels


def load_char_labels(model_path: str | os.path) -> set[str]:
    """
    Loads character labels from file
    :param model_path: file name
    :return: list of character tags (labels)
    """
    path = os.path.join(model_path, "tags-character.txt")
    try:
        with open(path) as f:
            labels = {line.strip() for line in f.readlines()}  # Use set comprehension
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return set()  # Return an empty set
    return labels
