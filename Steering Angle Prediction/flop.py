import os
import cv2

directory = 'data/IMG_old/'

for file in os.listdir(directory):
    img = cv2.imread(directory + file)
    horizontal_img = cv2.flip( img, 1 )

    #saving now
    cv2.imwrite('data/IMG/' + file, horizontal_img)
print('Done')