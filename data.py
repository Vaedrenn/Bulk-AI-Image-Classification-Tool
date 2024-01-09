from __future__ import annotations

import os
from typing import Tuple, Dict, Any

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


# Preprocesses images from directory
def process_images_from_directory(model, directory) -> list[(str, np.ndarray)]:
    preprocessed_images = []
    image_filenames = os.listdir(directory)

    # get dimensions from model
    _, height, width, _ = model.input_shape

    for filename in image_filenames:
        image_path = os.path.join(directory, filename)
        try:
            # Model only supports 3 channels
            image = PIL.Image.open(image_path).convert('RGB')

            image = np.asarray(image)
            image = tf.image.resize(image,
                                    size=(height, width),
                                    method=tf.image.ResizeMethod.AREA,
                                    preserve_aspect_ratio=True)
            image = image.numpy()
            image = dd.image.transform_and_pad_image(image, width, height)
            image = image / 255.

            preprocessed_images.append((filename, image))

        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    return preprocessed_images


# images need to preprocessed before using
def predict(model, labels, image: np.ndarray, score_threshold: float = 0.5
            ) -> tuple[dict[Any, Any], dict[Any, Any], str] | None:
    try:
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

    # unprocessed image
    except TypeError:
        print("Images need to be processed before calling this function")
        return None

    except AttributeError:
        print("Channels must be 3, use  image = PIL.Image.open(img_path).convert('RGB')")
        return None


def predict_all(model, labels, directory, score_threshold: float = 0.5):
    images = process_images_from_directory(model, directory)
    processed_images = []
    for image in images:
        result = predict(model, labels, image[1], score_threshold)
        if result is not None:
            processed_images.append((image[0], result))

    return processed_images


if __name__ == "__main__":
    pass
