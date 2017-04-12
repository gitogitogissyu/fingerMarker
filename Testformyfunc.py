# -*- coding: utf-8 -*-

"""
My Fucntion のテストプログラム．

一気に正しいあたいが出るかどうかをテストするためのプログラム．



"""


import numpy as np
import cv2
import math
import time
import csv
import datetime
import os
import sys
import winsound

import myFunction as mf



#nearbypoint_delete TEST
#複数の配列を先にs区政して，様子をみる．

test = np.array(((1,1),(2,2),(2,2),(10,10),(11,10),(12,10)))

result = mf.nearbypoint_delete(test,3)
print result



#cutimg TEST

test = np.arange(100).reshape(10,10)

result = mf.cutimg()

#flatten TEST

test = np.array(((1,1),(2,2),(2,2),(10,10),(11,10),(12,10)))

result = mf.flatten(test)

#make_x_y_pattern TEST

result = mf.make_x_y_pattern(100)

#getofgrav TEST

test = np.ones((10,10))
test = np.ones((2,2))

#getfingerplace TEST

#画像読み込み

img = cv2.imread('./testfiles/kankore.png')
temp = cv2.imread('./testfiles/fubuki.png')
#imgの(251,153)の場所にあるのはtest
test = cv2.imread('./testfiles/tesss.png')


mf.find_marker(test,np.array((251,153)),img,2)


place, a = mf.getfingerplace(temp,img,10)

aaa = mf.cutimg(img,place,100,50)

cv2.imshow('aaa',aaa)
cv2.waitKey()


mf.find_marker(test,np.array((251,153)),img,2)