from __future__ import annotations

import io
import os
from collections import OrderedDict
from typing import Any

import deepdanbooru as dd
import numpy as np
import tensorflow as tf
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import ImageFileDirectory_v2


# loads the model from /models/
# loading should be done before calling predict
def load_model(model_path: str | os.path) -> tf.keras.Model:
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
    print("Loading tags")
    path = os.path.join(model_path, "tags.txt")
    try:
        with open(path) as f:
            labels = [line.strip() for line in f.readlines()]
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return []
    print("Finished Loading tags")
    return labels


def load_char_labels(model_path: str | os.path) -> list[str]:
    print("Loading tags")
    path = os.path.join(model_path, "tags-character.txt")
    try:
        with open(path) as f:
            labels = [line.strip() for line in f.readlines()]
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return []
    print("Finished Loading tags")
    return labels


# Preprocesses images from directory
def process_images_from_directory(model: tf.keras.Model, directory: str | os.path) -> list[(str, np.ndarray)]:
    preprocessed_images = []
    image_filenames = os.listdir(directory)

    # get dimensions from model
    _, height, width, _ = model.input_shape

    for filename in image_filenames:
        image_path = os.path.join(directory, filename)
        try:
            # image = tf.keras.utils.load_img(
            #                                 image_path,
            #                                 grayscale=False,
            #                                 color_mode='rgb',
            #                                 target_size=(height, width),
            #                                 interpolation='nearest',
            #                                 keep_aspect_ratio=True
            # )
            # image = tf.keras.utils.img_to_array(image)

            # Model only supports 3 channels
            image = Image.open(image_path).convert('RGB')

            image = np.asarray(image)
            image = tf.image.resize(image,
                                    size=(height, width),
                                    method=tf.image.ResizeMethod.AREA,
                                    preserve_aspect_ratio=True)
            image = image.numpy()
            image = dd.image.transform_and_pad_image(image, width, height)
            image = image / 255.

            preprocessed_images.append((image_path, image))

        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    return preprocessed_images


# images need to preprocessed before using
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

            # If probability is below the threshold, stop adding to threshold results
            if prob < score_threshold:
                break

            # Store result for labels above the threshold
            result_threshold[label] = prob

        # do the same for character labels
        for index in indices:
            label = labels[index]
            prob = probs[index]

            # If probability is below the threshold, stop adding to threshold results
            # Check if the label is a character label
            if label in char_labels and prob > char_threshold:
                result_char[label] = prob
                # Remove the label from result_threshold if added to result_char
                result_threshold.pop(label, None)
                # Remove the label from result_all if added to result_char
                result_all.pop(label, None)

            if prob < char_threshold:
                break

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


# Writes tags to exif, modified from Vladmanic's https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/6087
def write_tags(image_path: str, info: str):
    # Open the image using PIL
    with Image.open(image_path) as img:
        ifd = ImageFileDirectory_v2()
        exif_stream = io.BytesIO()
        _TAGS = dict(((v, k) for k, v in TAGS.items()))  # enumerate possible exif tags
        ifd[_TAGS["ImageDescription"]] = info
        ifd.save(exif_stream)
        hex = b"Exif\x00\x00" + exif_stream.getvalue()

        img.save(image_path, exif=hex)
        # read_exif(image_path)


def read_exif(image_path):
    # Open the image file
    image = Image.open(image_path)

    # Get Exif data
    exif_data = image.getexif()

    # Check if Exif data exists
    if exif_data:
        # Iterate over Exif tags
        for tag, value in exif_data.items():
            # Look for the tag corresponding to "ImageDescription"
            if TAGS.get(tag) == "ImageDescription":
                # Print out value for "ImageDescription"
                print(f"ImageDescription: {value}")
                break  # Stop iteration once ImageDescription tag is found


if __name__ == "__main__":
    # Example usage:
    image_path = r"tests/images/post_3261444.jpg"
    directory_path = r"models/deepdanbooru-v3-20211112-sgd-e28"
    directory = r"tests/images"
    model = load_model(directory_path)
    labels = load_labels(directory_path)
    char_labels = load_char_labels(directory_path)

    _, height, width, _ = model.input_shape
    image = Image.open(image_path).convert('RGB')

    image = np.asarray(image)
    image = tf.image.resize(image,
                            size=(height, width),
                            method=tf.image.ResizeMethod.AREA,
                            preserve_aspect_ratio=True)
    image = image.numpy()
    image = dd.image.transform_and_pad_image(image, width, height)
    image = image / 255.

    results = predict(model, labels, char_labels, image)

    result_threshold, result_all, result_rating, result_char, result_text = results
    print(result_threshold)
    print(result_all)
    print(result_rating)
    print(result_char)
    print(result_text)
