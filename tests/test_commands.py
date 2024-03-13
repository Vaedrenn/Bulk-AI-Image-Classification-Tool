import deepdanbooru as dd
import numpy as np
import pytest
import tensorflow as tf
from PIL import Image

from src.commands.exif_actions import write_tags, read_exif
from src.commands.load_actions import load_model, load_labels, load_char_labels
from src.commands.predict_all import predict, process_images_from_directory, predict_all

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


@pytest.fixture
def char_labels():
    char_labels = load_char_labels(path)
    return char_labels


def test_load_model(model):
    assert model is not None
    assert isinstance(model, tf.keras.Model)


def test_load_labels(labels):
    assert labels is not None


def test_load_char_labels(char_labels):
    assert char_labels is not None


def test_predict(model, labels):
    img_path = r'tests/images/test1.jpg'
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

    result_threshold, result_all, result_rating, result_char, result_text = predict(model, labels, [], image, 0.5)

    assert result_threshold
    assert result_rating
    assert result_all
    assert result_text == "sketch, denim, greyscale, monochrome, pants, short_hair, long_sleeves, simple_background, long_hair, shirt, shorts, hood, 1girl, standing, white_background, concept_art, partially_colored, jeans, looking_at_viewer"


def test_process_all(model, labels):
    dir = r"tests/images"
    images = process_images_from_directory(model, dir)
    assert images


def test_predict_all(model, labels, char_labels):
    dir = r"tests/images"
    results = predict_all(model, labels, char_labels, dir, 0.5)

    assert results

    for image in results:
        filename = image[0]
        result_threshold, result_all, result_rating, result_char, result_text = image[1]

        # Just making sure something is returned here
        assert len(result_threshold) > 0
        assert len(result_all) > 0
        assert len(result_rating) > 0
        assert len(result_char) == 0
        assert len(result_text) > 0


def test_write_tags(tmp_path):
    image_path = tmp_path / 'test.jpg'
    image = Image.new('RGB', (300, 300), color='red')
    image.save(image_path)

    write_tags(image_path, "TEST")
    assert read_exif(image_path) == "TEST"

