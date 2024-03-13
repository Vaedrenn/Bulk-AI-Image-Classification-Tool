from __future__ import annotations

import io

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import ImageFileDirectory_v2


def write_tags(image_path: str, info: str):
    """
    Writes tags to exif, modified from Vladmanic's https://github.com/AUTOMATIC1111/stable-diffusion-webui/issues/6087

    :param image_path: file path of image
    :param info: tags to write
    :return: none
    """
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
    """
    Reads tags from exif
    :param image_path: file path of image
    :return: tags
    """
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
                return value
