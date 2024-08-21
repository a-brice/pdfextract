import cv2
import extract
import pathlib
import os

DICT_ENTITY = [
    {"label": "2", "bbox": [1541, 1087, 1696, 1125], "page": 0, "type": "Text"},
    {"label": "type", "bbox": [1877, 3013, 2172, 3057], "page": 0, "type": "Text"}, 
    {"label": "rev", "bbox": [2168, 3015, 2370, 3057], "page": 0, "type": "Text"}
]

def test_extract_text(basedir):
    img = cv2.imread(os.path.join(basedir, 'img', 'w8Template.png'))
    info, _ = extract.extract_text(img, DICT_ENTITY)
    assert info['2'] == 'FRANCE', 'the extraction text algorithm does not work properly'
    assert info['type'] == 'Form W-8BEN-E', 'the extraction text algorithm does not work properly'
    assert info['rev'] == '(Rev. 10-2021)', 'the extraction text algorithm does not work properly'

