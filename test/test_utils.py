import time
import pytest
import cv2
import os
import shutil
import utils
import pathlib

test_image_dir = pathlib.Path(__file__).parent.resolve() / 'img' 
test_data_dir = pathlib.Path(__file__).parent.resolve() / 'data' 


def test_convert_to_img(basedir, remove_testdir):

    # with images 
    testdir = os.path.join(basedir, 'img')
    nbpages = utils.convert_to_img(testdir, 'w8Template.png')
    pagepath = os.path.join(testdir, 'pages')
    assert nbpages == 1
    assert os.path.exists(pagepath)
    assert utils.get_page(pagepath, page=0) == os.path.join(pagepath, 'w8Template_$p#0.png')
    

    # with pdf
    testdir = os.path.join(basedir, 'data')
    nbpages = utils.convert_to_img(testdir, '1042s.pdf')
    pagepath = os.path.join(testdir, 'pages')
    assert nbpages == 7
    assert os.path.exists(pagepath)
    assert utils.get_page(pagepath, page=0) == os.path.join(pagepath, '1042s_$p#0.png')
    assert utils.get_page(pagepath, page=1) == os.path.join(pagepath, '1042s_$p#1.png')