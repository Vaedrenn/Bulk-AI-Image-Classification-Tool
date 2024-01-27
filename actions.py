from __future__ import annotations

import os
from typing import Tuple, Dict, Any, List

import deepdanbooru as dd
import numpy as np
from PIL import Image, ExifTags
import tensorflow as tf


# loads the model from /models/
# loading should be done before calling predict
def load_model(model_path: str | os.path) -> tf.keras.Model:
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
def load_labels(model_path: str | os.path) -> list[str]:
    path = os.path.join(model_path, "tags.txt")
    try:
        with open(path) as f:
            labels = [line.strip() for line in f.readlines()]
    except (FileNotFoundError, IOError, OSError) as file_error:
        print(f"Error reading labels file: {file_error}")
        return []
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

            preprocessed_images.append((filename, image))

        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    return preprocessed_images


# images need to preprocessed before using
def predict(model: tf.keras.Model, labels: list[str], image: np.ndarray, score_threshold: float = 0.5
            ) -> tuple[dict[str, float], dict[str, float], dict[str, float], str] | None:
    try:
        # Make a prediction using the model
        probs = model.predict(image[None, ...])[0]
        probs = probs.astype(float)

        # Extract the last three tags as ratings
        rating_labels = labels[-3:]
        rating_probs = probs[-3:]
        result_rating = dict(zip(rating_labels, rating_probs))

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
        return result_threshold, result_all, result_rating, result_text

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
def predict_all(model: tf.keras.Model, labels: list[str], directory: str | os.path, score_threshold: float = 0.5
                ) -> list[tuple[Any, tuple[dict[str, float], dict[str, float], dict[str, float], str]]] | None:
    images = process_images_from_directory(model, directory)
    processed_images = []
    for image in images:
        result = predict(model, labels, image[1], score_threshold)
        if result is not None:
            processed_images.append((image[0], result))
    if processed_images is not None:
        return processed_images
    else:
        print("No results within threshold: ", score_threshold)
        return None


def write_tags(image_path: str, info: str):
    # Open the image using PIL
    with Image.open(image_path) as img:
        # Get the existing Exif data (if any)
        exif_data = img.info.get("exif", b"")

        # Convert the Exif data to an ExifTags dictionary
        exif_dict = {ExifTags.TAGS[key]: exif_data[key] for key in ExifTags.TAGS.keys() if key in exif_data}

        # Set or update the "ImageDescription" tag in the Exif data
        exif_dict[ExifTags.TAGS["ImageDescription"]] = info

        # Convert the ExifTags dictionary back to Exif data
        new_exif_data = b"".join(
            ExifTags.MARKER + bytes([key, 0]) + bytes(value)
            for key, value in exif_dict.items()
        )

        # Save the modified Exif data back to the image
        img.save(image_path, exif=new_exif_data)


if __name__ == "__main__":
    pass
