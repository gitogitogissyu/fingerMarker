# -*- coding: utf-8 -*-

"""
This is My functions
このファイルは，自分が今まで作った自作関数をまとめたものです．
特に，マーカー追尾のために作られたプログラムが主です．
書くときのルール．
１，ここでのpt1,pt2は全部タプルの(x,y)で統一．
２，テストが終わっていない関数は使わないこと．
テストが終わり次第，必ず，「テスト済み」マークをつける．



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



#=============テスト済み=================
def returnx(arr):
    return len(arr[0])

#=============テスト済み=================
def returny(arr):
    return len(arr)

#=============テスト済み=================
def returnsize(arr):
    return (returnx(arr),returny(arr))


#線の方向は維持しつつ，長さを長くしている関数．
#<<描画系>>
#ここでのpt1,pt2は全部(x,y)で統一．
#2017-04-07現在，あまり使って無いので未テスト
def cvmyLine(img,pt1,pt2,color,times = 3.0,thickness=1,lineType = 8,shift =0):
     vx = pt2[0] - pt1[0]
     vy = pt2[1] - pt1[1]
     v  = math.sqrt(vx ** 2.0 + vy ** 2.0)
    
     v = v * times
     newpt = (int(pt1[0]+vx*v),int(pt1[1]+vy*v))
     cv2.line(img,pt1,newpt,color,thickness,lineType,shift)


#------------------------------
#cvArrow(描画系)(x,y)座標表示．
#やじるし引くための関数．cv2.lineと引数はほぼ同じ．
#矢印が存在してないと，先端部分が引けずにバグに陥るので注意．
#2017-04-07現在，あまり使って無いので未テスト
def cvArrow(img, pt1, pt2, color, thickness=1, lineType=8, shift=0):
    cv2.line(img,pt1,pt2,color,thickness,lineType,shift)
    vx = pt2[0] - pt1[0]
    vy = pt2[1] - pt1[1]
    v  = math.sqrt(vx ** 2 + vy ** 2)
    ux = vx / (v+0.01)
    uy = vy / (v+0.01)
    # 矢印の幅の部分
    w = 5
    h = 10
    ptl = (int(pt2[0] - uy*w - ux*h), int(pt2[1] + ux*w - uy*h))
    ptr = (int(pt2[0] + uy*w - ux*h), int(pt2[1] - ux*w - uy*h))
    # 矢印の先端を描画する
    cv2.line(img,pt2,ptl,color,thickness,lineType,shift)
    cv2.line(img,pt2,ptr,color,thickness,lineType,shift)      


#-----------------------
#nearbypoint_delete
#しきい値で区切るだけだと，ダブリが出てしまうので，それの削除をする．
#arr :　[[x,y],[x,y]]みたいな感じを想定.それ以外は未対応．
#rangewidth:周辺何ピクセルに存在する点を消すかを指定．
#=============テスト済み=================
def nearbypoint_delete(arr,rangewidth,threshold =10):
    """
    #nearbypoint_delete
    #しきい値で区切るだけだと，ダブリが出てしまうので，それの削除をする．
    #arr :　[[x,y],[x,y]]みたいな感じを想定.それ以外は未対応．
    #rangewidth:周辺何ピクセルに存在する点を消すかを指定．
    """

    #代入用配列宣言
    returnarr = np.empty((0,2),float)

    #かぶりが10こ以上あれば除去作業開始
    while(len(arr) >= threshold):
        removeindex = []
        i=1
        while(i <= len(arr)-1):
            if np.linalg.norm(arr[0]-arr[i]) < rangewidth:
                removeindex = removeindex + [i]
            i = i+1

        arr = np.delete(arr,removeindex,0)

        returnarr = np.append(returnarr,np.array([arr[0]]),0)
        arr = np.delete(arr,0,0)
        print len(arr)

    return returnarr


#------------------------------
#cutimg
#そのなの通り，画像を指定点から横幅，縦幅分切り取りする関数．
#いちいち配列にかくのだるかったから関数を使うことをおすすめします！！！！
#cutpointはfloatだろうがなんだろうが適用できます！
#cutpointは(x,y)で計算する．
#=============テスト済み=================
def cutimg(input_img,
           cutpoint,
           width,
           height):
    
    
    outimg = input_img[int(round(cutpoint[1])):int(round(cutpoint[1]))+height,
                       int(round(cutpoint[0])):int(round(cutpoint[0]))+width]
    

    return outimg


#----------------------
#flatten
#[[x,y],[x,y]] -> [x,y,x,y]
#２次元配列まで対応．
#そっから先は知らない．
#=============テスト済み=================
def flatten(nested_list):
    return[e for inner_list in nested_list for e in inner_list]

#----------------------
#make_y_x_pattern
#csvヘッダ作成関数．
#num：ヘッダの横幅指定．  
#=============テスト済み=================
def make_y_x_pattern(num__):
    listdata = []
    #listdata.append("t")

    for num in range(num__):
        tmp = "y" + str(num)
        listdata.append(tmp)
        tmp = "x" +str(num)
        listdata.append(tmp)
    return listdata


#----------------------
#make_x_y_pattern
#csvヘッダ作成関数．
#num：ヘッダの横幅指定． 
#=============テスト済み================= 
def make_x_y_pattern(num__):
    listdata = []
    #listdata.append("t")

    for num in range(num__):
        tmp = "x" + str(num)
        listdata.append(tmp)
        tmp = "y" +str(num)
        listdata.append(tmp)
    return listdata


#<<<<FOR DEBUG>>>>>---------------
#onMouse
#マウスでクリックしたところの座標を返すためのイベントドライブ関数．
#main関数内に，
#cv2.setMouseCallback("<WINDOWNAME>",onMouse,<PARAMS>)
#を書く必要有り．
#この関数では，paramsは２つ突っ込む必要有り．
def onMouse(event, x, y ,flag , params):
    wname, img = params

    if event == cv2.EVENT_LBOTTONDOWN:
        print "pressed!"
        print(x,y)
        print(img[y][x])

#<NOUSE>-----------------------------
#使ってません
def nothing(x):
    pass

#使ってません！！！！！-----------------------------
#IO_exchange
#色抽出を用いて画像二値化関数
#ノイズ除去，色抽出を同時に行っています．
#
def IO_exchange(Template__,lower_,upper_):
    #I/O exchange
    template_HSV = cv2.cvtColor(Template__,cv2.COLOR_BGR2HSV)

    #For remove I/O picture noise
    kerne_removeIOnoise = np.ones((5,5),np.uint8)
    kerne_comp = np.ones((3,3),np.uint8)

    """
    lower_green = np.array([0,0,0])
    upper_green = np.array([180,100,100])
    """

    lower_green = lower_
    upper_green = upper_
    #template IO remove noise
    template_IO = cv2.inRange(template_HSV,lower_green,upper_green)
    template_IO = cv2.morphologyEx(template_IO,cv2.MORPH_OPEN,kerne_removeIOnoise)
    template_IO = cv2.morphologyEx(template_IO,cv2.MORPH_CLOSE,kerne_comp)

    return template_IO

#-----------------------------------
#getofgrav
#未使用
#重心導出関数．
#どっかで関数化されてるはずだけど，各種調整のために自作．
#2016-11-22　14:44
#もっと良い関数があったので，変更．
#<<<<<<<<<<<<<<未使用>>>>>>>>>>>>>>>>>
def __getofgrav(array,cutpoint):  
    sums =0.0
    sx = 0.0
    sy = 0.0
    for y in range(len(array)):
        for x in range(len(array[y])):
            
            sums += array[y][x] +0.001
            sx += (array[y][x]+0.001) * (x+cutpoint[1])
            sy += (array[y][x]+0.001) * (y+cutpoint[0])
            #print sums,sx,sy
    gpx = (sx/sums)
    gpy = (sy/sums)

    return np.array([gpx,gpy])
 

#-----------------------------------
#getofgrav(処理系）)
#重心導出関数．
#cv2.momentsを利用することで，精度を高めている．
#array:重心計算する行列
#Cutpoint:(x,y)で表される切った左上の点．
#==============テスト済み=========================
def getofgrav(array,cutpoint):
    data = cv2.moments(array)
    if data['m00'] == 0:
        return np.array((0,0))
    
    gpx = (data['m10']/data['m00']) + cutpoint[0]
    gpy = (data['m01']/data['m00']) + cutpoint[1]
    
    return np.array((gpx,gpy))
    
#-------------------------------------------
#getfingerplace
#指の場所を検索する関数．
#指の場所は重心ではなく，MAXの値を利用して抽出している．
#（もしもブレるようなら，findmarkerみたいにする必要があるかも．）
#
#templatepic:指テンプレート画像．
#framepic:動画のフレーム（探索対象）
#全部(x,y)で返すように設定．
#============テスト済み======================

def getfingerplace(templatepic,framepic,fingerPlaceOffset=10):

    src = framepic
    tmp = templatepic

    res = cv2.matchTemplate(src,tmp,cv2.TM_CCOEFF_NORMED)

    (minval,maxval,minloc,maxloc) = cv2.minMaxLoc(res)
    
    maxtmp = np.array(maxloc)
    width = fingerPlaceOffset
    minus = np.array([width,width])

    gravtmp = getofgrav(cutimg(res,maxtmp-minus,width*2,width*2),maxtmp-minus)
    #print "fingerplace y:%d,x:%d" % (maxloc[1],maxloc[0])
    return maxloc,np.r_[maxtmp,gravtmp]#(x,y)の順番で返って来ます．



    #cv2.imshow("test",tmp)

#----------------------
#find_marker
#説明は以下のコメントアウトを読んでください．
#結構汎用性高い．
#=============テスト済み=================
def find_marker(markerTemplate__,
                markerTemplatePoint,
                videoFrame__OnlyFinger,
                cutOffset,
                i__=129,
                debug=0):
    """
    ぜんぶここでの値は指座標系の上です！！！
    注意すること。

    markerTemplate
    マーカーのテンプレーとの画像をそのまま入れ込む．
    markerTemplatePoint
    元々のマーカーテンプレートがあった場所を(x,y)の順で入れる．

    videoFrame__OnlyFinger
    新しいビデオのフレーム
    ここで入力されるのは指だけカットしたフレーム．

    メモ
    d , w, h = markerTemplate.shape[::-1]
    """
    if markerTemplatePoint[0] <= 0:
        return [[0,0],[0,0]]


    
 
    #W_cutpoint:切り出す左端の座標
    #ここはmarkerTemplatePointがnumpyだから引き算できる．
    w_cutpoint = markerTemplatePoint - cutOffset

    #マーカーテンプレート事態の横幅とか
    if len(markerTemplate__.shape) == 2:
        hei,wid=markerTemplate__.shape
    else:
        hei,wid,dim=markerTemplate__.shape

    #窓自体の横幅縦幅
    w_shape= np.array([hei,wid]) + cutOffset*2


    print hei,wid
    #ここでcutOffsetを２倍するの忘れて苦しい思いしtくぁ．
    cutvideoFrame = cutimg(videoFrame__OnlyFinger,w_cutpoint,wid+(2*cutOffset),hei+(2*cutOffset))

    if cutvideoFrame.shape[0] <= markerTemplate__.shape[0] or cutvideoFrame.shape[1] <= markerTemplate__.shape[1] or hei == 0 or wid == 0:
        return [[0,0],[0,0]]
    else:
        result = cv2.matchTemplate(markerTemplate__,cutvideoFrame, cv2.TM_CCOEFF_NORMED)

    result[result<0] = 0.0

    (minval,maxval,minloc,maxloc) = cv2.minMaxLoc(result)

    maxtmp = np.array(maxloc + w_cutpoint)
    #width = fingerPlaceOffset
    #minus = np.array([width,width])

    gravPoint = getofgrav(result,w_cutpoint)


    if i__ == 129:
        #print "markertmp: %s\nw_cutpoint(y,x): %s\nw_shape(h,w): %s" % (markerTemplatePoint,w_cutpoint,w_shape)
        print "gravPoint(y,x): %s\n" % gravPoint
        #cv2.imshow("alkjdklasdj",result)
        #cv2.imshow("cutvideoframeaa",cutvideoFrame)
        #print result
        #time.sleep(0.5)


    return [gravPoint,maxtmp]

    #(y,x)で返す．これは指座標系での値になっている．
    #もしも絶対座標系での値が欲しかったらCSV出力の時にカットポイントを足し算すればOK．
   