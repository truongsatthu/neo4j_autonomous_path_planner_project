#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import cv2
import numpy as np

img_path = sys.argv[1]
dst_path = sys.argv[2]

img = cv2.imread(img_path)
bgrLower = np.array([5, 5, 5])
bgrUpper = np.array([230, 230, 230])
img_mask = cv2.bitwise_not(cv2.inRange(img, bgrLower, bgrUpper))
result = cv2.bitwise_and(img, img, mask=img_mask)

cv2.imwrite(dst_path, result)
