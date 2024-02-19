import numpy as np
import pytest

from actions import load_model, load_labels, predict, process_images_from_directory, predict_all, write_tags
import tensorflow as tf
import deepdanbooru as dd
from PIL import Image
import deepdanbooru as dd
import numpy as np
import pytest
import tensorflow as tf
from PIL import Image

from actions import load_model, load_labels, predict, process_images_from_directory, predict_all, write_tags

path = r"models/deepdanbooru-v3-20211112-sgd-e28"

# Define paths for test images and info
TEST_IMAGE_PATH = "test_image.jpg"
TEST_INFO = "Test info"


@pytest.fixture
def model():
    # Load the model once and provide it as a fixture
    model = load_model(path)
    return model


@pytest.fixture
def labels():
    # Load the labels once and provide them as a fixture
    labels = load_labels(path)
    return labels


def test_load_labels():
    assert model is not None
    assert isinstance(model, tf.keras.Model)


def test_load_labels():
    assert labels is not None


def test_predict(model, labels):
    img_path = r'tests/images/post2021_image.jpg'
    _, height, width, _ = model.input_shape

    # Model only supports 3 channels
    image = Image.open(img_path).convert('RGB')

    image = np.asarray(image)
    image = tf.image.resize(image,
                            size=(height, width),
                            method=tf.image.ResizeMethod.AREA,
                            preserve_aspect_ratio=True)
    image = image.numpy()
    image = dd.image.transform_and_pad_image(image, width, height)
    image = image / 255.

    threshold_results, all_results, rating, text = predict(model, labels, image, 0.5)
    # print("Threshold Results:", threshold_results)
    # print("Rating:", rating)
    # print("All Results:", all_results)
    # print("Text:", text)
    # print(len(text))
    assert threshold_results
    assert rating
    assert all_results
    assert text


def test_process_all(model, labels):
    dir = r"tests/images"
    images = process_images_from_directory(model, dir)
    assert images


def test_predict_all(model, labels):
    dir = r"tests/images"
    results = predict_all(model, labels, dir, 0.5)

    assert results

    for image in results:
        filename = image[0]
        threshold_results, all_results, rating_results, text = image[1]
        print("Threshold Results:", threshold_results)
        # print("Rating:", rating_results)
        # print("All Results:", all_results)
        # print("Text:", text)
        assert threshold_results
        assert all_results
        assert rating_results
        assert text


def test_write_tags():
    path = r"tests/images/test.png"
    write_tags(path, "TEST")


