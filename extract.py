import numpy as np
import cv2
import os
import pytesseract 


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

white_pixel_threshold = 53 + 60 # numbers of zeros in the cropped pixel image



def grayscale(image):
	return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def whiten(image):
    image[image > 200] = 255
    image[image < 70] = 0
    return image

def remove_noise(image):
	return cv2.medianBlur(image, 5)

def thresholding(image):
	return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def dilate(image):
	kernel = np.ones((3, 5),np.uint8)
	return cv2.dilate(image, 	kernel, iterations = 1)

def erode(image):
	kernel = np.ones((3,5),np.uint8)
	return cv2.erode(image, 	kernel, iterations = 1)

# opening - erosion followed by dilation
def opening(image):
	kernel = np.ones((5,5),np.uint8)
	return cv2.morphologyEx(image, cv2.MORPH_OPEN, 	kernel)

# canny edge 
def canny(image):
	return cv2.Canny(image, 100, 200)



def extract_text(img, dict_entity):
    
    img_show = img.copy()
    img_mask = np.zeros_like(img_show)
    text = dict()
    
    if not dict_entity:
        return dict(), img_show
    
    for roi in dict_entity:
        
        left, top, right, bottom = roi['bbox']
        
        cv2.rectangle(img_mask, (left, top), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(img_show, roi['label'], (left + 10, bottom + 20), 1, 1, [0, 0, 255], 2)
    
    	# Crop the specific required portion of entire image
        img_cropped = img[top:bottom, left:right]
        
        
        if roi['type'] == 'Text':
            
            # Image filter 
            img_cropped = grayscale(img_cropped)
            # img_cropped = remove_noise(img_cropped)
            img_cropped = whiten(img_cropped)
            # img_cropped = thresholding(img_cropped)
            # img_cropped = erode(img_cropped)
            # img_cropped = np.pad(img_cropped, (15, 5), constant_values=255)
            # cv2.imwrite('output/test/' + roi['name'] + '.png', img_cropped)
        
            # read from image 
            ocr_output = pytesseract.image_to_string(img_cropped, lang='eng')
            cleaned_output = os.linesep.join([s for s in ocr_output.splitlines() if s])
            cleaned_output = cleaned_output.replace("\r\n","@")
            cleaned_output = cleaned_output.split("@")[-1]
            text[roi['label']] = cleaned_output
            
        
        if roi['type'] == 'Box':
            
            # Image filter 
            img_cropped = grayscale(img_cropped)
            img_cropped = thresholding(img_cropped)
            white_pixels_nb = cv2.countNonZero(img_cropped)
            check = 0 if white_pixels_nb > white_pixel_threshold else 1
            text[roi['label']] = check
            
                    
        img_show = cv2.addWeighted(img_show, 0.9, img_mask, 0.1, 0)
            
    return text, img_show
    


def show_highlighted_img(test_dir, page, img):
    dirpath = os.path.join(test_dir, 'show')
    os.makedirs(dirpath, exist_ok=True)
    cv2.imwrite(dirpath + f'/p{page}.png', img)