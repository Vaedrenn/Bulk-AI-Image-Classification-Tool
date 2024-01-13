import PIL
import numpy as np
import pytest

from data import load_model, load_labels, predict, process_images_from_directory, predict_all
import tensorflow as tf
import deepdanbooru as dd

path = r"models/deepdanbooru-v3-20211112-sgd-e28"


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
    img_path = r'tests/images/ヒトこもる_花心_97031695_p0.png'
    _, height, width, _ = model.input_shape

    # Model only supports 3 channels
    image = PIL.Image.open(img_path).convert('RGB')

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
        # print("Image:", filename, " Rating: ", rating_results)
        assert threshold_results
        assert all_results
        assert rating_results
        assert text


# tests if the ratings and labels match up
def test_predict_rating(model, labels):
    img_path = r'tests/images/ヒトこもる_花心_97031695_p0.png'
    _, height, width, _ = model.input_shape

    # Model only supports 3 channels
    image = PIL.Image.open(img_path).convert('RGB')

    image = np.asarray(image)
    image = tf.image.resize(image,
                            size=(height, width),
                            method=tf.image.ResizeMethod.AREA,
                            preserve_aspect_ratio=True)
    image = image.numpy()
    image = dd.image.transform_and_pad_image(image, width, height)
    image = image / 255.

    threshold_results, all_results, rating, text = predict(model, labels, image, 0.5)

    # Check if any key in rating is in threshold_results
    common_keys = set(rating.keys()).intersection(threshold_results.keys())

    for key in common_keys:
        if threshold_results[key] == rating[key]:
            print(f"Key: {key}, Threshold Value: {threshold_results[key]}, Rating Value: {rating[key]}")

    # Assert that all common keys have the same values
    assert all(threshold_results[key] == rating[key] for key in common_keys)
