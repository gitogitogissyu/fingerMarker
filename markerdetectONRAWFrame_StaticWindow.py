# -*- coding: utf-8 -*-


"""
条件
・指座標系を切り出して計測しています
・マーカーの枠は移動シています．
・マーカーテンプレートは更新していません．








TODO
関数を独立して駆動できるような設計にすること．

関数の内容が間違ってないかサイド確認すること
正しいアルゴリズムを使っているか
	現状使っているアルゴリズムはテンプレートマッチング
	書き方が間違っているかもしれないので再度確認．
切り取るやり方と，枠を固定する方法の二週類でできるようにする．



命名規則
raw*:生の，全く改変がなされていないもの
finger*:指座標系の，
absoluteFingerTemplate*:絶対的な，一番基準になったりシているものに対して

"""

"""
いつかのめも

    2016-09-01　18:19　もう意味が無いけど，Tipsの意味で残しておく．
    #このアスタリスクの意味
    そもそもpoint_locが(array,array)の形になっている
    （arrayが２つタプルの中に入ってしまっている）ので，アスタリスクでタプルを展開する必要がある．
    zipは引数として，zip(array,array)みたいな感じになるので．
    もしアスタリスクがなければ，zip((array,array))で引数一つじゃねーかと突っ込まれる．



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

def main():

	

    #=============================PARAMETERS=========================
    #skipframes: 　　　  処理を開始するフレーム数，それまではスキップするのでこんな名前になってる
	#nearbywindow:       複数認識された場合に周辺何ピクセルまでのダブリを消去するかを定める定数．
	#			         大体25ピクセルだと全部キレイに消えてくれる．
	#fingerFrameHeightとか: absoluteFingerTemplate（指の位置を検出するテンプレート）で検出した左上の座標
	#					  を基準として，どの程度の幅，高さで画像を切り出すかを指定する．
	#					  正方形で切り取っておけば問題ない．（大体750px*750pxで十分なはず）
	#markerCutOffset:     マーカーを認識する際に余分に切り取るオフセット．5~10の間が良い．
	#fingerPlace_offset:  指位置を認識するときのオフセット．10~20程度が良い．
	#gaussianWindow:      ガウシアンフィルタをかけるときの窓の大きさ
	#markerThreshold:     マーカーの場所を探索するときのしきい値．（defalt = 0.7)


    skipframes = 0
    nearbywindow = 20
    fingerFrameHeight,fingerFrameWidth,fingerFrameDim = (500,750,3)
    markerCutOffset = 7
    fingerPlace_offset = 10
    gaussianWindow = (5,5)
    markerThreshold = 0.70

    rec_fingerFrameName = 'fingerFrameVideo.avi'
    rec_VideoFrameName = 'VideoFrameVideo.avi'
    outVideoArrowName = 'arrow.avi'


    #==============================READFILES======================================
    #rawVideoName:撮影した動画ファイル名
    #absoluteRawVideoFrameName:rawVideoから切り出したいちフレーム画像名(名前中にフレーム名があるはず)
	#absoluteMarkerTemplateName:マーカーの場所を大雑把に認識するために用いるテンプレート．
	#							一般的には誰かのマーカーテンプレートを使っても十分なはず．
	#absoluteFingerTemplateName:指の位置を検出するために用いるテンプレート．これは画像から切り出す必要あり．
	#							絶対マーカーと指の輪郭がダブっているところを利用する．

	#作業フォルダ内に入る

	
    #os.chdir(u'C:\\Users\\razer\\Dropbox\\Lab\\opencv\\Worldhaptics\\sakuragi\\0.7mm')


    #rawVideoName = 'C0325.MP4'
    #absoluteRawVideoFrameName = 'C0325.mp4_frame_360_.png'
    #absoluteMarkerTemplateName = '../../SURA_marker.png'
    #absoluteFingerTemplateName = 'C0325.mp4_frame_360_finger.png'


    os.chdir(u'C:\\Users\\razer\\Dropbox\\Lab\\opencv\\python\\src')


    rawVideoName = 'capture0.m1v'
    absoluteRawVideoFrameName = '0.png'
    absoluteMarkerTemplateName = 'point.png'
    absoluteFingerTemplateName = 'point.png'


    rawVideo = cv2.VideoCapture(rawVideoName)
    absoluteRawVideoFrame = cv2.imread(absoluteRawVideoFrameName)
    absoluteMarkerTemplate = cv2.imread(absoluteMarkerTemplateName)
    absoluteFingerTemplate = cv2.imread(absoluteFingerTemplateName)

    #マーカー画像幅高さ取得
    d,markerFrameWidth,markerFrameHeight  = absoluteMarkerTemplate.shape[::-1]
    

    
    #========画像反転======================
    #今後の動画を読み込むときにも画像反転をすること．
    
    absoluteRawVideoFrame = cv2.flip(absoluteRawVideoFrame,1)
    absoluteMarkerTemplate = cv2.flip(absoluteMarkerTemplate,1)
    absoluteFingerTemplate = cv2.flip(absoluteFingerTemplate,1)
    
    
    #===================fingerTemplate作成============================================
	#指だけを切り取った画像をフレームから作成する．
    tttmp = cv2.matchTemplate(absoluteFingerTemplate,absoluteRawVideoFrame,cv2.TM_CCOEFF_NORMED)
    a,b,c,max_loc = cv2.minMaxLoc(tttmp)
    
    fingerTemplate = mf.cutimg(absoluteRawVideoFrame,max_loc,fingerFrameWidth,fingerFrameHeight)
    
    
    

    #=例外処理=
    if fingerTemplate is None or absoluteMarkerTemplate is None:
    	print "FINGER TEMPLATE IS UNDEFINED!\n"
        return -1
        


    #======================CSVデータ出力のための準備=======================
    #やってること
    #*結果を入れるためのフォルダ作成
    #*csvファイルの作成

    font = cv2.FONT_HERSHEY_PLAIN
    font_size =1
    #make csvWriter
    today = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + rawVideoName
    today = today.replace('/','')
    
    os.mkdir(today)
    os.chdir(today)
    today = today +'.csv'
    f= open(today,'ab')
    file = open("fingerplace.csv","ab")
    csvWriter = csv.writer(f)
    csvWriter_fingerplace = csv.writer(file)
    


    
    

    """
    #absoluteMarkerTemplateの幅で円のテンプレ作成
    #もういらなくなったのでコメントアウト
    img = np.zeros((markerFrameHeight,markerFrameWidth),np.uint8)
    cv2.circle(img,(markerFrameHeight/2,markerFrameWidth/2),markerFrameHeight/2-7,255,-1)
    """
   

    #=========================マーカーの動きビデオ出力準備==========================

    ret , videoFrame = rawVideo.read()
    #videoFrame = cv2.flip(videoFrame,1)

    if not(ret):
        print "error!  video cannot read!"
        return  
    #call videoparam
    #ビデオの設定！
    __outVideo_frameRate = float(60.0)
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')

    tmp_fingerTemplate_videoshape = (fingerFrameWidth,fingerFrameHeight)
    tmp_rawVideo_videoshape = (videoFrame.shape[1],videoFrame.shape[0])


    outVideo_fingertemplate = cv2.VideoWriter(rec_fingerFrameName,
                                              fourcc,
                                              __outVideo_frameRate,
                                              tmp_rawVideo_videoshape)
    outVideo_VideoFrame = cv2.VideoWriter(rec_VideoFrameName,
                                          fourcc,
                                          __outVideo_frameRate,
                                          tmp_rawVideo_videoshape)
    outVideo_Arrow = cv2.VideoWriter(outVideoArrowName,
                                          fourcc,
                                          20.0,
                                          (fingerFrameWidth,fingerFrameHeight))






    #=====================ガウシアンフィルタ適用=====================================
    fingerTemplate = cv2.GaussianBlur(fingerTemplate,gaussianWindow,0)
    absoluteMarkerTemplate = cv2.GaussianBlur(absoluteMarkerTemplate,gaussianWindow,0)
    videoFrame = cv2.GaussianBlur(videoFrame,gaussianWindow,0)



    
    
    """
    #========================色抽出して２値化したなごり============================
    色抽出の名残．
    H_upper = 142
    H_lower = 30
    S_upper = 199
    S_lower = 0
    V_upper = 135
    V_lower = 36

    
    lower = np.array([H_lower,S_lower,V_lower])
    upper = np.array([H_upper,S_upper,V_upper])
    fingerTemplate_IO = IO_exchange(fingerTemplate,lower,upper)
    absoluteMarkerTemplate_IO = IO_exchange(absoluteMarkerTemplate,lower,upper)
    videoFrame_IO = IO_exchange(videoFrame,lower,upper)
    """

    #fingerTemplateを利用してマーカー位置のあたりをつける．（ある種ラベリング）
    #通常ラベリングだと，つながってしまっているやつがあって二値化しても綺麗に撮れないから
    """
    shape[0]:HEIGHT
    shape[1]:WIDTH
    shape[2]:dimention*あったりなかったり

    全部これ以降(y,x)の順番で統一
    """
    
    #---------------------------------------------------
    
    
	#=====================STEP 1============================
	#=================マーカーのばしょ取得=================
	#
	#
	#


    #マーカー場所にあたりを付ける作業
    matchtemplate_result = cv2.matchTemplate(absoluteRawVideoFrame,
                            absoluteMarkerTemplate,
                            cv2.TM_CCOEFF_NORMED)
    
    # 二値化処理でノイズ除去
    kerne_removeIOnoise = np.ones((5,5),np.uint8)
    matchtemplate_result = cv2.morphologyEx(matchtemplate_result,cv2.MORPH_OPEN,kerne_removeIOnoise)
    

    #シャープ化処理
    k = 2.0
    shape_operatior = np.array([[0,    -k,    0],
        [-k,1+4*k,-k],
        [0,-k,0]])
    matchtemplate_result_shape = cv2.filter2D(matchtemplate_result,-1,shape_operatior)
    
    #しきい値．設定は計画的に！！！！
    
    point_loc = np.where(matchtemplate_result_shape >= markerThreshold)
 
     #<<<<<<<point_locは(y(array),x(array))順に入っていますよ！！！！！>>>>>>>>>>>>>>>

        
   
    
    #np.c_は配列のattendと一緒！
    everyMarkerPointPlace = np.c_[point_loc[1],point_loc[0]]
    everyMarkerPointPlace = mf.nearbypoint_delete(everyMarkerPointPlace,nearbywindow)

    
    #新しい場所を入れる用の配列
    point_loc_new = np.array(everyMarkerPointPlace)
    point_cut_place = np.array(everyMarkerPointPlace)

    #csvHeaderの記入．
    csvWriter.writerow(mf.make_x_y_pattern(len(everyMarkerPointPlace)))






    #<<<<<<<<<<<<DEBUG>>>>>>>>>>>>>>>
    #===================STEP1の状態チェック===========================================
    fingerTemplate_show = np.array(absoluteRawVideoFrame)

    #デバッグとか行ってるけど，通常状態でも付けておいた方が賢明です．
    for i in xrange(len(everyMarkerPointPlace)):
        cv2.rectangle(fingerTemplate_show,(int(round(everyMarkerPointPlace[i][0])),int(round(everyMarkerPointPlace[i][1]))),
            (int(round(everyMarkerPointPlace[i][0]))+markerFrameWidth,int(round(everyMarkerPointPlace[i][1]))+markerFrameHeight),
            (0,0,255),2)
        text = str(i)
        cv2.putText(fingerTemplate_show,text,(int(round(everyMarkerPointPlace[i][0])),int(round(everyMarkerPointPlace[i][1]))),font, font_size,(255,255,0))

    tmp = cv2.minMaxLoc(matchtemplate_result_shape)
    print tmp[1],tmp[3]
    cv2.namedWindow("fiasn")
    #cv2.setMouseCallback("fiasn",onMouse,["fiasn",fingerTemplate])
    cv2.imshow("test",fingerTemplate_show)
    cv2.imshow("fingertemp",matchtemplate_result_shape)
    cv2.imshow("fiasn",fingerTemplate)
    cv2.imshow("asfdf",absoluteMarkerTemplate)
    cv2.imshow("videoFrame",videoFrame)
    cv2.imshow("tesasdhfjd",videoFrame)
    cv2.imshow("jshshshshsh",tttmp)
    cv2.imshow("sfsdfjsdfksdjkf",absoluteFingerTemplate)
    cv2.imwrite("markerIO.jpg",fingerTemplate)
    cv2.imwrite("fingertmp.jpg",fingerTemplate_show)

    cv2.waitKey(0)
    
    print len(everyMarkerPointPlace)
    
    
    #---------------デバッグ終わり------------------
    #--------------ここからビデオに対する処理----------------------------

    """
    二値化の名残
    H_upper = 180
    H_lower = 0
    S_upper = 82
    S_lower = 0
    V_upper = 113
    V_lower = 61


    lower = np.array([H_lower,S_lower,V_lower])
    upper = np.array([H_upper,S_upper,V_upper])
    """

    tx = 100
    ty =100


    #=====================STEP2 動画に対してのマーカー追尾=======================

    #フレーム指定
    rawVideo.set(cv2.CAP_PROP_POS_FRAMES,skipframes)
    
    #カウンタを実際のフレームに対応させる
    counter = skipframes




    while(rawVideo.isOpened()):
        print "nowframe: %d" % counter

        #カウンタとかビデオのフレーム読みとか
        counter = counter +1
        ret , videoFrame = rawVideo.read()
        videoFrame  = cv2.flip(videoFrame,1)
        """
        videoFrame = np.zeros((1500,1000,3),np.uint8)
        videoFrame = 255 - videoFrame
        ty = ty+1
        videoFrame[tx:fingerTemplate.shape[0]+tx,ty:fingerTemplate.shape[1]+ty] = fingerTemplate#これで座標をずらしながら出来る．
        """
        arrowimg = np.zeros((fingerFrameHeight,fingerFrameWidth),np.uint8)
  

        
        if not(ret):

            print "MovieFrame cannot read!"
            break
        


        #===================指の場所を探索=============================

        #ガウシアンフィルタ
        videoFrame = cv2.GaussianBlur(videoFrame,gaussianWindow,0)
        #videoFrame_IO = IO_exchange(videoFrame,lower,upper)

        #これで，ゆびの場所をとる
        fingerplace,fingerplace__ = mf.getfingerplace(absoluteRawVideoFrame,videoFrame,fingerPlace_offset)
        
        #指のとこだけトリミング
        videoFrame_Finger = mf.cutimg(videoFrame,fingerplace,fingerFrameWidth,fingerFrameHeight)


        #CSV出力用の配列宣言
        newMarkerplace = np.empty((0,2),float)
        marker_cutplace = np.empty((0,2))



        #===================マーカーの追尾=============================
        #各マーカーのある場所に対して
        for i in xrange(len(everyMarkerPointPlace)):

            #最初に指定したマーカーテンプレートを用いる
            markerTemplate = mf.cutimg(absoluteRawVideoFrame,everyMarkerPointPlace[i],markerFrameWidth,markerFrameHeight)
            
            #今のフレームからオフセットつけた矩形の中でテンプレートマッチング
            tmp___ =mf.find_marker(markerTemplate,everyMarkerPointPlace[i],videoFrame,markerCutOffset,i)
            tmp_markerpoint = tmp___[0]
            cutplace__ = tmp___[1]

            #print tmp___
            #print tmp_markerpoint
            #print cutplace__


            """
            cvmyLine(arrowimg,
                (int(point_loc_new[i][1]),int(point_loc_new[i][0])),
                (int(tmp_markerpoint[1]),int(tmp_markerpoint[0])),
                (255,255,255),10)
            """
            
            #次のループ用に配列に突っ込む
            newMarkerplace = np.r_[newMarkerplace,[tmp_markerpoint]]
            marker_cutplace = np.r_[marker_cutplace,[cutplace__]]


            if i ==129:
                print "markerplint %s" % tmp_markerpoint
                cutppoint = point_loc_new[i] - markerCutOffset
                #ccccc = cutimg(videoFrame_Finger,cutppoint,markerFrameHeight+(markerCutOffset*2),markerFrameWidth+(markerCutOffset*2)) 

                #cv2.imshow("asdkljlsdfjlskd",ccccc)

        #csv書き出し
        csvWriter.writerow(mf.flatten(newMarkerplace))
        csvWriter_fingerplace.writerow(fingerplace__)

        #新マーカーポイントコピー・指座標画像コピー
        point_loc_new = np.array(newMarkerplace)
        point_cut_place = np.array(marker_cutplace)

        
        #fingerTemplate = np.array(videoFrame_Finger)
        #こいつは，指のテンプレートを新しい座標でとってしまってたので，コメントアウトしました．
        #2016/09/07．
        videoFrame_Finger_print = np.array(videoFrame)

        
        #四角形を書くよ！
        for i in xrange(len(point_loc_new)):
            if point_loc_new[i][0] == "Nan":
                continue

            #print "everyMarkerPointPlace %s" % everyMarkerPointPlace
            #各マーカーに四角形を書くよ
            cv2.rectangle(videoFrame_Finger_print,(int(point_loc_new[i][0]),int(point_loc_new[i][1])),
                (int(point_loc_new[i][0])+markerFrameWidth,int(point_loc_new[i][1])+markerFrameHeight),
                (0,0,255),2)
        #指のところに四角形を書くよ
        cv2.rectangle(videoFrame,fingerplace,(fingerplace[0]+fingerFrameWidth,fingerplace[1]+fingerFrameHeight),(0,0,255),3)
        
        #動画チックに見せるよ
        
        cv2.imshow('frame',videoFrame_Finger_print)
        cv2.imshow('allframe',videoFrame)
        cv2.imshow("arrow",arrowimg)
        cv2.imshow("fingertemplate",fingerTemplate)        

        #VideoOutput用にフレームを書きだすよ
        outVideo_fingertemplate.write(videoFrame_Finger_print)
        outVideo_VideoFrame.write(videoFrame)
        #arrowimg = cv2.resize(arrowimg,(fingerFrameWidth,fingerFrameHeight))
        outVideo_Arrow.write(arrowimg)
        #cv2.imshow('aaaaaaa',videoFrame_Finger)

        #Qで離脱するよ
        if cv2.waitKey(1) == ord('q'):       
            break
        
        

        if counter % 100 == 0:
            winsound.Beep(880,1000)
        #elif counter % 2 == 0:
            #winsound.Beep(440,300)
        
        

        print "nowframe: %d" % counter
        
    


    #後始末はしっかり！
    outVideo_fingertemplate.release()
    outVideo_VideoFrame.release()
    outVideo_Arrow.release()
    rawVideo.release()
    f.close()
    file.close()
    cv2.destroyAllWindows()


    return 0
        

    
    #cv2.imwrite('teasstaaaaaa.jpg',mask)
    

    """
    for y in xrange(fingerTemplate.shape[0]/WINDOWWIDTH):
        for x in xrange(fingerTemplate.shape[1]/WINDOWWIDTH):
            
            #(y,x)の順番
            nowPoint = [y * WINDOWWIDTH,x * WINDOWWIDTH]

            # (minval,maxval,minloc,maxloc) = cv2.minMaxLoc(...)
            minMax_result = cv2.minMaxLoc(
                            matchtemplate_result[nowPoint[0]:nowPoint[0]+WINDOWWIDTH,
                                                nowPoint[1]:nowPoint[1]+WINDOWWIDTH])

            if debug_max:
                print maxval
                print mixval 
                time.sleep(3)

            if maxval >0.65 and maxval <=1.0
                
                shape[0]:HEIGHT
                shape[1]:WIDTH
                shape[2]:dimention*あったりなかったり

                全部これ以降はcsv出力以外は(y,x)の順番で統一
                
    """
	


if __name__ == '__main__':
	tmp =main()