# -*- coding: utf-8 -*-


"""
TODO
関数を独立して駆動できるような設計にすること．
関数の内容が間違ってないかサイド確認すること
正しいアルゴリズムを使っているか
	現状使っているアルゴリズムはテンプレートマッチング
	書き方が間違っているかもしれないので再度確認．
切り取るやり方と，枠を固定する方法の二週類でできるようにする．
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