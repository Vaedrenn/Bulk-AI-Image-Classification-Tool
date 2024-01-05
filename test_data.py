import PIL

from data import load_model, load_labels, predict


def test_predict():
    path = r"models/deepdanbooru-v3-20211112-sgd-e28"
    model = load_model(path)
    labels = load_labels(path)
    img_path = r'tests/images/post2021_image.jpg'

    img = PIL.Image.open(img_path)
    threshold_results, all_results, text = predict(model, labels, img, 0.5)
    print("Threshold Results:", threshold_results)
    print("All Results:", all_results)
    print("Text:", text)
