# MIT License
#
# Copyright (c) 2023 Niall McCarroll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from htmlfive.html5_builder import Html5Builder, Fragment, ElementFragment
import base64
from PIL import Image
from matplotlib import cm
import numpy as np
from .utils import prepare_attrs

def save_image(arr,vmin,vmax,path,cmap_name="coolwarm"):
    if cmap_name == "viridis":
        cmap_fn = cm.viridis
    elif cmap_name == "coolwarm":
        cmap_fn = cm.coolwarm
    else:
        raise ValueError("Unknown colour map: "+cmap_name)
    im = Image.fromarray(np.uint8((255*cmap_fn((arr-vmin)/(vmax-vmin)))))
    im.save(path)

def save_image_falsecolour(data_red, data_green, data_blue, path):
    alist = []
    for arr in [data_red, data_green, data_blue]:
        minv = np.nanmin(arr)
        maxv = np.nanmax(arr)
        alist.append((255*(arr-minv) / (maxv-minv)).astype(np.uint8))
    arr = np.stack(alist,axis=-1)
    im = Image.fromarray(arr,mode="RGB")
    im.save(path)


class ImageFragment(ElementFragment):

    def __init__(self, src, alt_text="", w=None, h=None):
        super().__init__("img", prepare_attrs({
            "src": src, "alt":alt_text, "width": w, "height": h}))


def inlined_image(from_path,mime_type="image/png"):
    with open(from_path,"rb") as f:
        content_bytes = f.read()
    return "data:" + mime_type + ";charset=US-ASCII;base64," + str(base64.b64encode(content_bytes), "utf-8")


class InlineImageFragment(ElementFragment):

    def __init__(self, path, alt_text="", w=None, h=None):
        super().__init__("img", prepare_attrs({
            "src": inlined_image(path), "alt":alt_text, "width": w, "height": h}))
