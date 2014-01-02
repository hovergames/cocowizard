# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from path import path
from PIL import Image
import os
from ..utils import config
from ..utils.log import debug, error

def resize(sourceImage, newWidth, newHeight, destName):
    img = Image.open(sourceImage)
    img = img.resize((newWidth, newHeight), Image.ANTIALIAS)
    img.save(destName)

def run():
    input_dir = path("Meta/screenshots")
    output_dir = path("Meta/_generated/screenshots")
    output_dir.makedirs_p()

    #landscape
    baseResolution = [1024, 768]
    destResolutions = [[1280, 800, "png"], [960, 640, "png"], [1136, 640, "png"], [640, 480, "jpg"], [1280, 720, "jpg"], [1280, 768, "png"], [800, 480, "png"], [1920, 1080, "jpg"]]
    langs = ["", "_de", "_en", "_nl", "_it", "_es", "_fr"]
    for screenNo in range(1, 6):
        for destRes in destResolutions:
            for lang in langs:
                sourceFile = input_dir + "/" + str(baseResolution[0]) + "x" + str(baseResolution[1]) + "_0" + str(screenNo) + str(lang) + ".png"
                if os.path.exists(sourceFile):
                    destFile = output_dir + "/screenshot" + str(destRes[0]) + "x" + str(destRes[1]) + "_0" + str(screenNo) + str(lang) + "." + str(destRes[2])
                    resize(sourceFile, destRes[0], destRes[1], destFile)

    # portrait
    baseResolution = [768, 1024]
    destResolutions = [[800, 1280], [640, 960], [640, 1136], [768, 1280], [480, 800, "png"], [768, 1280, "png"]]
    for screenNo in range(1, 6):
        for destRes in destResolutions:
            for lang in langs:
                sourceFile = input_dir + "/" + str(baseResolution[0]) + "x" + str(baseResolution[1]) + "_0" + str(screenNo) + str(lang) + ".png"
                if os.path.exists(sourceFile):
                    destFile = output_dir + "/screenshot" + str(destRes[0]) + "x" + str(destRes[1]) + "_0" + str(screenNo) + str(lang) + ".png"
                    resize(sourceFile, destRes[0], destRes[1], destFile)
