import PIL

from data import load_model, load_labels, predict
import tensorflow as tf

path = r"models/deepdanbooru-v3-20211112-sgd-e28"


def test_load_labels():
    model = load_model(path)
    assert model is not None
    assert isinstance(model, tf.keras.Model)



def test_predict():
    model = load_model(path)
    labels = load_labels(path)
    img_path = r'tests/images/post2021_image.jpg'

    img = PIL.Image.open(img_path)
    threshold_results, all_results, text = predict(model, labels, img, 0.5)
    print("Threshold Results:", threshold_results)
    print("All Results:", all_results)
    print("Text:", text)
