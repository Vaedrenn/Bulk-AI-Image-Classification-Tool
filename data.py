from __future__ import annotations

import os

import deepdanbooru as dd
import numpy as np
import PIL.Image
import tensorflow as tf


# loads the model from /models/
# loading should be done before calling predict
def load_model(model_path) -> tf.keras.Model:
    file_name = "model-resnet_custom_v3.h5"
    path = os.path.join(model_path, file_name)

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


def preprocess_images(model: tf.keras.model, path:os.path, batch_size: int = 32):
    # Get the input shape of the model (assuming it's a 4D tensor)
    _, height, width, _ = model.input_shape
    image_size = (height, width)

    # get all images from path
    dataset = tf.keras.preprocessing.image_dataset_from_directory(
        path,
        image_size=image_size,
        batch_size=batch_size,
        method=tf.image.ResizeMethod.AREA,
        preserve_aspect_ratio=True
    )
    return dataset


def predict(model, labels, image: PIL.Image.Image, score_threshold: float
            ) -> tuple[dict[str, float], dict[str, float], str]:
    # Get the input shape of the model (assuming it's a 4D tensor)
    _, height, width, _ = model.input_shape

    # if unprocessed image then resize
    if image.width > width:
        image = np.asarray(image)
        image = tf.image.resize(image,
                                size=(height, width),
                                method=tf.image.ResizeMethod.AREA,
                                preserve_aspect_ratio=True)
        image = image.numpy()

    # Transform and pad the image using utility function
    image = dd.image.transform_and_pad_image(image, width, height)

    # Normalize pixel values to the range [0, 1]
    image = image / 255.

    # Make a prediction using the model
    probs = model.predict(image[None, ...])[0]
    probs = probs.astype(float)

    # Get the indices of labels sorted by probability in descending order
    indices = np.argsort(probs)[::-1]

    result_all = dict()
    result_threshold = dict()

    # Iterate over the sorted indices
    for index in indices:
        label = labels[index]
        prob = probs[index]

        # Store result for all labels
        result_all[label] = prob

        # If probability is below the threshold, stop adding to threshold results
        if prob < score_threshold:
            break

        # Store result for labels above the threshold
        result_threshold[label] = prob

    result_text = ', '.join(result_all.keys())
    return result_threshold, result_all, result_text
