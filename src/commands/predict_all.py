from __future__ import annotations

import os
from collections import OrderedDict
from typing import Any

import deepdanbooru as dd
import numpy as np
import tensorflow as tf
from PIL import Image
from PyQt5.QtCore import QRunnable, QThreadPool


# Preprocesses images from directory using qt's multiprocessing model
class Runnable(QRunnable):
    def __init__(self, image_path, size, preprocessed_images):
        super().__init__()
        self.image_path = image_path
        self.size = size
        self.preprocessed_images = preprocessed_images

    def run(self):
        try:
            # Model only supports 3 channels
            image = Image.open(self.image_path).convert('RGB')

            image = np.asarray(image)
            image = tf.image.resize(image,
                                    size=self.size,
                                    method=tf.image.ResizeMethod.AREA,
                                    preserve_aspect_ratio=True)
            image = image.numpy()
            image = dd.image.transform_and_pad_image(image, self.size[0], self.size[1])
            image = image / 255.

            self.preprocessed_images.append((self.image_path, image))

        except Exception as e:
            print(f"Error processing {self.image_path}: {e}")


#   Processes all images in a directory, does not go into subdirectories.
#   Images need to be shaped before predict can be called on it.
def process_images_from_directory(model: tf.keras.Model, directory: str | os.path) -> list[(str, np.ndarray)]:
    preprocessed_images = []
    image_filenames = os.listdir(directory)
    pool = QThreadPool.globalInstance()

    # get dimensions from model
    _, height, width, _ = model.input_shape
    size = (height, width)

    for filename in image_filenames:
        image_path = os.path.join(directory, filename)
        runnable = Runnable(image_path, size, preprocessed_images)
        pool.start(runnable)

    pool.waitForDone()
    return preprocessed_images


# Predicts tags using TF
def predict(
        model: tf.keras.Model,
        labels: list[str],
        char_labels: list[str],
        image: np.ndarray,
        score_threshold: float = 0.5,
        char_threshold: float = 0.85
) -> tuple[dict[str, float], dict[str, float], dict[str, float], dict[str, float], str] | None:
    try:
        # Make a prediction using the model
        probs = model.predict(image[None, ...])[0]
        probs = probs.astype(float)

        # Extract the last three tags as ratings
        rating_labels = ["rating:safe", "rating:questionable", "rating:explicit"]
        rating_probs = probs[-3:]

        probs = probs[:-3]
        result_rating = OrderedDict(zip(rating_labels, rating_probs))

        # Get the indices of labels sorted by probability in descending order
        indices = np.argsort(probs)[::-1]

        result_all = OrderedDict()
        result_threshold = OrderedDict()
        result_char = OrderedDict()

        # Iterate over the sorted indices
        for index in indices:
            label = labels[index]
            prob = probs[index]

            # Store result for all labels
            result_all[label] = prob

            # If probability is below the threshold, stop adding to threshold results, cannot assume char > general
            if prob < score_threshold and prob < char_threshold:
                break

            # Store result for labels above the threshold
            if prob > score_threshold and label not in char_labels:
                result_threshold[label] = prob
            if prob > char_threshold and label in char_labels:
                result_char[label] = prob

        result_text = ', '.join(result_all.keys())

        if len(result_threshold) > 0 or len(result_char) > 0:
            return result_threshold, result_all, result_rating, result_char, result_text
        else:
            return None

    # unprocessed image
    except TypeError:
        print("Images need to be processed before calling this function, Call process_images_from_directory")
        return None

    except AttributeError:
        print("Channels must be 3, use  image = PIL.Image.open(img_path).convert('RGB')")
        return None


# Predicts all images in the directory
# To unpack:
#    for image in results:
#        filename = image[0]
#        threshold_results, all_results, rating_results, text = image[1]
def predict_all(model: tf.keras.Model,
                labels: list[str],
                char_labels: list[str],
                directory: str | os.path,
                score_threshold: float = 0.5,
                char_threshold: float = 0.85
                ) -> (
        list[tuple[Any, tuple[dict[str, float], dict[str, float], dict[str, float], dict[str, float], str]]] | None):
    images = process_images_from_directory(model, directory)
    processed_images = []
    for image in images:
        result = predict(model, labels, char_labels, image[1], score_threshold, char_threshold)
        if result is not None:
            processed_images.append((image[0], result))
    if processed_images is not None:
        return processed_images
    else:
        print("No results within threshold: ", score_threshold)
        return None
