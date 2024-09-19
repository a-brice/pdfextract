import numpy as np
import cv2
import os
import pytesseract 


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

black_pixel_threshold = 0.12 # proportion of black pixel on white pixel



def grayscale(image):
	return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def thresholding(image):
    img = cv2.threshold(image, 190, 255, cv2.THRESH_TRUNC)[1]
    return cv2.threshold(img, 130, 255, cv2.THRESH_TOZERO)[1]


def dilate(image):
	kernel = np.ones((2, 2),np.uint8)
	return cv2.dilate(image, 	kernel, iterations = 1)


def erode(image):
	kernel = np.ones((3,3),np.uint8)
	return cv2.erode(image, 	kernel, iterations = 1)

# opening - erosion followed by dilation
def opening(image):
	kernel = np.ones((2,2),np.uint8)
	return cv2.morphologyEx(image, cv2.MORPH_OPEN, 	kernel)

# canny edge 
def canny(image):
	return cv2.Canny(image, 50, 150)


def remove_box_line(image):
    """Remove box line to get the response easily"""
    edges = canny(image)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=10, minLineLength=10, maxLineGap=5)
    for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x1 - x2) <= 2 or abs(y1 - y2) <= 2:
                cv2.line(image, (x1, y1), (x2, y2), 255, 2)
    return image



def remove_square_box(img):
    
    cts = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    squares = []
    
    for i in [1, 2]: # contours of square interior + exterior 
        if i >= len(cts):
            break
        peri = cv2.arcLength(cts[i], True)
        approx = cv2.approxPolyDP(cts[i], 0.04 * peri, True)

        if len(approx) == 4: # square -> 4 points 
            squares += [approx]
    
    if len(squares) == 2:
        mask = np.zeros(img.shape)
        cv2.drawContours(mask, [squares[1]], -1, 255, -1)  
        img = np.where(mask == 255, img, 255)
    if len(squares) == 1:
        cv2.drawContours(img, [squares[0]], -1, 0, 3)  
        
    return img
        
        


def extract_text(img, dict_entity):
    
    img_show = img.copy()
    img_mask = np.zeros_like(img_show)
    text = dict()
    
    if not dict_entity:
        return dict(), img_show
    
    for roi in dict_entity:
        
        left, top, right, bottom = np.array(roi['bbox']).astype(int)
        
        # Draw rectangle on image to show
        cv2.rectangle(img_mask, (left, top), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.rectangle(img_show, (left, top), (right, bottom), (0, 0, 120), 2)
        
        # Add text on image to show 
        textcoords = left + 10 if roi['type'] == 'Text' else right + 10, (bottom + top) // 2 
        cv2.putText(img_show, roi['label'], (textcoords[0], textcoords[1]), 1, 1, [0, 0, 200], 2)
        
    	# Crop the specific required portion of entire image
        img_cropped = img[top:bottom, left:right]

        # Image filter 
        img_cropped = grayscale(img_cropped)
        img_cropped = thresholding(img_cropped)

        # handle void image quickly
        if len(np.unique(img_cropped)) == 1:
            text[roi['label']] = ''


        if roi['type'] == 'Text':
        
            # read from image 
            ocr_output = pytesseract.image_to_string(img_cropped, lang='eng')
            cleaned_output = ocr_output.strip()
            text[roi['label']] = cleaned_output
        
        
        if roi['type'] == 'Digit':

            # read from image 
            params = '--psm 7 -c tessedit_char_whitelist=0123456789,.-'
            ocr_output = pytesseract.image_to_string(img_cropped, lang='eng', config=params)
            cleaned_output = ocr_output.strip()
            text[roi['label']] = cleaned_output
            
        
        if roi['type'] == 'Box':
            
            # Image filter 
            img_cropped = cv2.threshold(img_cropped, 140, 255, cv2.THRESH_BINARY)[1]
            img_cropped = remove_square_box(img_cropped)
            black_pixels_nb = np.count_nonzero(img_cropped == 0)
            white_pixels_nb = np.count_nonzero(img_cropped == 255)
            prop = black_pixels_nb / white_pixels_nb
            check = 1 if prop > black_pixel_threshold else 0
            text[roi['label']] = check
        
        cv2.imwrite(f'output/{roi["label"]}.png', img_cropped)                       
    
    img_show = cv2.addWeighted(img_show, 0.95, img_mask, 0.05, 0)
            
    return text, img_show
    


def show_highlighted_img(test_dir, page, img):
    dirpath = os.path.join(test_dir, 'show')
    os.makedirs(dirpath, exist_ok=True)
    cv2.imwrite(dirpath + f'/p{page}.png', img)