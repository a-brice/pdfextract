import pathlib 
import alignement
import cv2

def test_align_to_template(basedir):
    template = str(basedir / 'img' / 'w8Template.png')
    example = str(basedir / 'img' / 'w8Example.png')

    template_img = cv2.imread(template)
    aligned_img = alignement.align_to_template(example, template)
    res = cv2.matchTemplate(aligned_img, template_img, cv2.TM_CCOEFF_NORMED)[0, 0]
    assert res > 0.6, 'The alignement isn\'t working properly'
