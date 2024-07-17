import cv2
import numpy as np

def get_keypoints(img, shape):
    
    # Convert to grayscale.
    img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    
    # Configure ORB feature detector Algorithm with 1000 features.
    orb_detector = cv2.ORB_create(1000)
     
    # Extract key points and descriptors for both images
    keyPoint, des = orb_detector.detectAndCompute(img_grey, None)
     
    # Display keypoints for reference image in green color
    # imgKp = cv2.drawKeypoints(img, keyPoint, 0, (0,222,0), None)
    # imgKp = cv2.resize(imgKp, shape)
    
    return keyPoint, des
    



def align_to_template(cform='examples/fw9.png', template='templates/fw9.png', output_file=None):
    """Align (rotation, scale, translation) a scanned PDF file according to a template file"""
    
    # client form 
    imgTest = cv2.imread(cform)
    
    # Reference Reference image or Ideal image
    imgRef = cv2.imread(template)
    height, width, _ = imgRef.shape
    keyPoint1, des1 = get_keypoints(imgTest, (height, width))
    keyPoint2, des2 = get_keypoints(imgRef,  (height, width))
    
    # Match features between two images using Brute Force matcher with Hamming distance
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
     
    # Match the two sets of descriptors.
    matches = matcher.match(des1, des2)
    
    
    # Sort matches on their Hamming distance and convert the sorted list back to a tuple
    matches = tuple(sorted(matches, key=lambda x: x.distance))
     
    # Take the top 90 % matches forward.
    matches = matches[:int(len(matches) * 0.9)]
    no_of_matches = len(matches)
     
    # Define 2x2 empty matrices
    p1 = np.zeros((no_of_matches, 2))
    p2 = np.zeros((no_of_matches, 2))
     
    # Storing values to the matrices
    for i in range(len(matches)):
        p1[i, :] = keyPoint1[matches[i].queryIdx].pt
        p2[i, :] = keyPoint2[matches[i].trainIdx].pt
     
    # Find the homography matrix.
    homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)
    
    # Use homography matrix to transform the unaligned image wrt the reference image.
    aligned_img = cv2.warpPerspective(imgTest, homography, (width, height))

    # Save aligned image 
    if output_file:
        cv2.imwrite(output_file, aligned_img)
    
    return aligned_img
