import io
import os
import re

import requests
from PIL import Image, UnidentifiedImageError
from django.core.files import File


def set_value_to_immutable_dict(immutable, key, value):
    # IMPORTANT NOTE OF THIS METHOD:
    # CHANGING IMMUTABLE TYPES IS BAD PRACTICE
    # but sometimes, we don't have other solutions as easy
    mutable = immutable.copy()
    if type(value) is list:
        mutable.setlist(key, value)
    else:
        mutable[key] = value
    return mutable


# https://stackoverflow.com/a/63419911/14506165
def is_svg(file):
    SVG_R = r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b'
    SVG_RE = re.compile(SVG_R, re.DOTALL)
    file_contents = file.decode('latin_1')  # avoid any conversion exception
    is_svg = SVG_RE.match(file_contents) is not None
    return is_svg


def get_image_file_by_url(url):
    try:
        r_content = requests.get(url).content
        file_bytes = io.BytesIO(requests.get(url).content)
        if is_svg(r_content):
            return File(file_bytes, name=os.path.basename(url))
        else:
            # to trigger pillow's image control exceptions
            Image.open(file_bytes)
            return File(file_bytes, name=os.path.basename(url))
    except (requests.exceptions.RequestException, UnidentifiedImageError) as e:
        return None
