# coding=utf-8
import glob, os
import numpy as np
import cv2

db_imgs = [] # array of database images
db_files = []# array of names of database images
db_kp = [] # keypoints of database images
db_des = [] # descriptors of database images
# Create ORB detector with 1000 keypoints with a scaling pyramid factor of 1.2
orb = cv2.ORB(1000, 1.2) # feature extration object
# Create Brute Force Matcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Load images from database
def load_database():
    del db_imgs[:]
    del db_files[:]
    del db_kp[:]
    del db_des[:]
    for file in glob.glob("./static/db/*.jpg"):
        print(file)
        db_files.append(file)

    for i_img in range(len(db_files)):
        img = cv2.imread(db_files[i_img], 0)
        cols,rows = img.shape
        img = cv2.resize(img, (500*rows/cols,500))
        db_imgs.append(img)
        (kp, des) = orb.detectAndCompute(db_imgs[i_img], None)
        db_kp.append(kp)
        db_des.append(des)

# Load Database on startup
load_database()

def drawMatches(img1, kp1, img2, kp2, matches):
    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

    # Place the first image to the left
    out[:rows1,:cols1] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2,cols1:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)   
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)


    # Show the image
    cv2.imshow('Matched Features', out)
    cv2.waitKey(0)
    cv2.destroyWindow('Matched Features')

    # Also return the image if you'd like a copy
    return out

def calcMatchesPosition(img1, kp1, img2, kp2, matches):
    error_total_x = 0
    error_total_y = 0

    # para calcular a proporção da imagem
    pos1 = 0
    img1_idx = matches[pos1].queryIdx
    img2_idx = matches[pos1].trainIdx

    (pt1x1, pt1y1) = kp1[img1_idx].pt
    (pt1x2, pt1y2) = kp2[img2_idx].pt

    ratio_x = 0
    ratio_y = 0

    count_x = 0
    count_y = 0
    min_ratio = 0.1
    max_ratio = 10.0
    for pos2 in range(pos1 + 1, len(matches)):
        img1_idx2 = matches[pos2].queryIdx
        img2_idx2 = matches[pos2].trainIdx

        (pt2x1, pt2y1) = kp1[img1_idx2].pt
        (pt2x2, pt2y2) = kp2[img2_idx2].pt

        if (pt1x2 - pt2x2) != 0:
            ratio = (pt1x1 - pt2x1) / (pt1x2 - pt2x2)
            if ratio > min_ratio and ratio < max_ratio:
                ratio_x += ratio
                count_x += 1
        if (pt1y2 - pt2y2) != 0:
            ratio = (pt1y1 - pt2y1) / (pt1y2 - pt2y2)
            if ratio > min_ratio and ratio < max_ratio:
                ratio_y += ratio
                count_y += 1

    if count_x > 0:
        ratio_x /= count_x
    if count_y > 0:
        ratio_y /= count_y
    print 'ratiox: ' + str(ratio_x)
    print 'ratioy: ' + str(ratio_y)

    # para calcular o erro de posicionamento de cada ponto
    for pos1 in range(len(matches)-1):

        # Get the matching keypoints for each of the images
        img1_idx = matches[pos1].queryIdx
        img2_idx = matches[pos1].trainIdx

        (pt1x1,pt1y1) = kp1[img1_idx].pt
        (pt1x2,pt1y2) = kp2[img2_idx].pt

        error_x = 0
        error_y = 0
        for pos2 in range(pos1+1, len(matches)):
            img1_idx2 = matches[pos2].queryIdx
            img2_idx2 = matches[pos2].trainIdx

            (pt2x1, pt2y1) = kp1[img1_idx2].pt
            (pt2x2, pt2y2) = kp2[img2_idx2].pt

            error_x += np.fabs((pt1x1 - pt2x1) - ((pt1x2 - pt2x2) * ratio_x))
            error_y += np.fabs((pt1y1 - pt2y1) - ((pt1y2 - pt2y2) * ratio_y))

        error_x /= (len(matches)- (pos1+1))
        error_y /= (len(matches)- (pos1+1))

        error_total_x += error_x
        error_total_y += error_y
    return (error_total_x/ratio_x + error_total_y/ratio_y) / 2

def findMatch(img_filename):

    error_imgs = []
    img = cv2.imread(img_filename, 0)
    cols,rows = img.shape
    img = cv2.resize(img, (500*rows/cols,500))


    # Detect keypoints of original image
    (kp1,des1) = orb.detectAndCompute(img, None)

    for i_img in range(len(db_imgs)):
        # Do matching
        matches = bf.match(des1,db_des[i_img])

        # Sort the matches based on distance.  Least distance
        # is better
        matches = sorted(matches, key=lambda val: val.distance, reverse=False)
        sum = 0
        total = 20
        for num in range(0,total):
            print 'matches: ' + str(matches[num].distance)
            sum += matches[num].distance
        sum /= total
        print 'media: ' + str(sum)
        # Show only the top 10 matches - also save a copy for use later

        error = calcMatchesPosition(img, kp1, db_imgs[i_img], db_kp[i_img], matches[0:total])

        error_imgs.append(error)
        #out = drawMatches(img1, kp1, img2, kp2, matches[0:total])

    best_match = 0
    smallest_error = error_imgs[0]
    for num in range(1, len(db_imgs)):
        if error_imgs[num] < smallest_error:
            smallest_error = error_imgs[num]
            best_match = num

    print 'ERROR: ' + str(smallest_error)
    if smallest_error > 1000:
        return None
    return db_files[best_match]