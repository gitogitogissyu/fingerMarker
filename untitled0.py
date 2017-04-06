# -*- coding: utf-8 -*-
"""
Created on Tue Apr 04 18:02:27 2017

@author: Razer
"""


"""
python書き直し．
このプログラム間違ってるんじゃないか疑惑が発生．

2016/08/25
結局書いたこと
色抽出する際にパラメータがわからないと抽出できない問題があったので，
そのプログラムを書いた．
途中まで書いてた部分は下にコメントとして残してある．


2016/08/23ver0.5
書くこと
*テンプレートマッチングを二値化したモノで行う．
*重心計算関数にミスがないかチェック
*

2016/09/01
書き終わり．
大体の処理は終了しています！！！
現在じっそうできていないのが，矢印動画の部分．
出力ができない問題があるので，どうにかここを解決したい．

2016/11/15
ガウシアンを全部切ったけどやっぱり駄目だった．




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

#デバッグ変数．入れると色々見れるよ！！！
global debug
debug = False
#2016/11/22　14:55
#わかった．
#cvmyLineとかそこら辺に書かれているような，描画系関数はすべて(x,y)で統一されていて，
#それ以外の画像加工系は(y,x)で統一されている．
#関数のはじめに，これは描画系なのか，処理系なのか書いておいて，はんべつがつくようにする．


#2016-11-22　14:51
#コードを見直すと，途中から，(y,x)で処理するようになっている．
#なので，関数に対して点の座標を渡すときは，"(y,x)"になるようにする．
#さっきまで考えてたことは訂正．


#2016-11-22　14:51
#前提として,(x,y)の順番で値を入れて点を管理することになっている．
#横軸方向がx,縦軸方向がyである．
#通常，hogehoge.shapeをすると，(y,x)，ないし，(y,x,dimention)という風に表現される．
#それを例外的な処理として考える．
#つまり，逆転させて問題にならないようにする．



#線の方向は維持しつつ，長さを長くしている関数．
#<<描画系>>
#ここでのpt1,pt2は全部(x,y)で統一．
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
#arr :　[[y,x],[y,x]]みたいな感じを想定.それ以外は未対応．
#rangewidth:周辺何ピクセルに存在する点を消すかを指定．

def nearbypoint_delete(arr,rangewidth):


    returnarr = np.empty((0,2),float)#

    while(len(arr) >= 10):
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
#cutpointは(y,x)で計算する．

def cutimg(input_img,
           cutpoint,
           height,
           width):
    """
    outimg = input_img[int(round(cutpoint[1])):int(round(cutpoint[1]))+height,
                       int(round(cutpoint[0])):int(round(cutpoint[0]))+width]
    """
    
    #2016/11/22　14:44
    #点が(y,x)の時はこっち．
    outimg = input_img[int(round(cutpoint[0])):int(round(cutpoint[0]))+height,
                       int(round(cutpoint[1])):int(round(cutpoint[1]))+width]
    

    return outimg


#----------------------
#flatten
#[[x,y],[x,y]] -> [x,y,x,y]
#２次元配列まで対応．
#そっから先は知らない．
def flatten(nested_list):
    return[e for inner_list in nested_list for e in inner_list]

#----------------------
#make_y_x_pattern
#csvヘッダ作成関数．
#num：ヘッダの横幅指定．  
def make_y_x_pattern(num__):
    listdata = []
    #listdata.append("t")

    for num in range(num__):
        tmp = "y" + str(num)
        listdata.append(tmp)
        tmp = "x" +str(num)
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
#重心導出関数．
#どっかで関数化されてるはずだけど，各種調整のために自作．
#2016-11-22　14:44
#もっと良い関数があったので，変更．

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

    return np.array([gpy,gpx])
 

#-----------------------------------
#getofgrav(処理系）)
#重心導出関数．
#cv2.momentsを利用することで，精度を高めている．
#array:重心計算する行列
#Cutpoint:(y,x)で表される切った左上の点．
def getofgrav(array,cutpoint):
    data = cv2.moments(array)
    if data['m00'] == 0:
        return np.array((0,0))
    
    gpy = data['m10']/data['m00'] + cutpoint[0]
    gpx = data['m01']/data['m00'] + cutpoint[1]
    
    return np.array((gpy,gpx))
    
#-------------------------------------------
#getfingerplace
#指の場所を検索する関数．
#指の場所は重心ではなく，MAXの値を利用して抽出している．
#（もしもブレるようなら，findmarkerみたいにする必要があるかも．）
#
#templatepic:指テンプレート画像．
#framepic:動画のフレーム（探索対象）
#全部(y,x)で返すように設定．
def getfingerplace(templatepic,framepic,fingerPlaceOffset):

    src = framepic
    tmp = templatepic

    res = cv2.matchTemplate(src,tmp,cv2.TM_CCOEFF_NORMED)

    (minval,maxval,minloc,maxloc) = cv2.minMaxLoc(res)
    
    maxtmp = np.array(maxloc[::-1])
    width = fingerPlaceOffset
    minus = np.array([width,width])

    gravtmp = getofgrav(cutimg(res,maxtmp-minus,width*2,width*2),maxtmp-minus)
    #print "fingerplace y:%d,x:%d" % (maxloc[1],maxloc[0])
    return maxloc[::-1],np.r_[maxtmp,gravtmp]#(y,x)の順番で返って来ます．



    #cv2.imshow("test",tmp)

#----------------------
#find_marker
#説明は以下のコメントアウトを読んでください．
#結構汎用性高い．
def find_marker(markerTemplate__,
                markerTemplatePoint,
                videoFrame__OnlyFinger,
                cutOffset,
                i__,
                ):
    """
    ぜんぶここでの値は指座標系の上です！！！
    注意すること。

    markerTemplate
    マーカーのテンプレーとの画像をそのまま入れ込む．
    markerTemplatePoint
    元々のマーカーテンプレートがあった場所を(y,x)の順で入れる．

    videoFrame__OnlyFinger
    新しいビデオのフレーム
    ここで入力されるのは指だけカットしたフレーム．

    メモ
    d , w, h = markerTemplate.shape[::-1]
    """
    if markerTemplatePoint[1] <= 0:
        return [[0,0],[0,0]]


    
 

    w_cutpoint = markerTemplatePoint - cutOffset
    if len(markerTemplate__.shape) == 2:
        hei,wid=markerTemplate__.shape
    else:
        hei,wid,dim=markerTemplate__.shape


    w_shape= np.array([hei,wid]) + cutOffset

    #ここでcutOffsetを２倍するの忘れて苦しい思いしtくぁ．
    cutvideoFrame = cutimg(videoFrame__OnlyFinger,w_cutpoint,hei+(2*cutOffset),wid+(2*cutOffset))

    if cutvideoFrame.shape[0] <= markerTemplate__.shape[0] or cutvideoFrame.shape[1] <= markerTemplate__.shape[1] or hei == 0 or wid == 0:
        return [[0,0],[0,0]]
    else:
        result = cv2.matchTemplate(markerTemplate__,cutvideoFrame, cv2.TM_CCOEFF_NORMED)

    result[result<0] = 0.0

    (minval,maxval,minloc,maxloc) = cv2.minMaxLoc(result)

    maxtmp = np.array(maxloc[::-1] + w_cutpoint)
    #width = fingerPlaceOffset
    #minus = np.array([width,width])

    gravPoint = getofgrav(result,w_cutpoint)


    if i__ == 129:
        #print "markertmp: %s\nw_cutpoint(y,x): %s\nw_shape(h,w): %s" % (markerTemplatePoint,w_cutpoint,w_shape)
        #print "gravPoint(y,x): %s\n" % gravPoint
        cv2.imshow("alkjdklasdj",result)
        cv2.imshow("cutvideoframeaa",cutvideoFrame)
        #print result
        #time.sleep(0.5)
   

    return [gravPoint,maxtmp]

    #(y,x)で返す．これは指座標系での値になっている．
    #もしも絶対座標系での値が欲しかったらCSV出力の時にカットポイントを足し算すればOK．
   




def main():
    debug_min = False
    debug_max = True



    #os.chdir(u'C:\\Users\\seitaro\\Dropbox\\Lab\\opencv\\python\\etc\\2017-02-02')
    os.chdir(u'C:\\Users\\razer\\Dropbox\\Lab\\opencv\\Worldhaptics\\sakuragi\\0.7mm')


    fingerVideoname = 'C0325.MP4'
    # read some files
    fingerVideo = cv2.VideoCapture(fingerVideoname)

    #fingerTemplate = cv2.imread('C210pic_finger.png')
    fingerTemplate_sozai = cv2.imread('C0325.mp4_frame_360_.png')
    fingerPoint = cv2.imread('../../SURA_marker.png')
    absolute = cv2.imread('C0325.mp4_frame_360_finger.png')#これが絶対値で場所をとるやつ
    skipframes = 360
    nearbywindow = 25
 
    h_ftemp , w_ftemp, d_ftemp = (750,750,3)
    
    #画像反転，今後の動画を読み込むときにも画像反転をすること．
    
    fingerTemplate_sozai = cv2.flip(fingerTemplate_sozai,1)
    fingerPoint = cv2.flip(fingerPoint,1)
    absolute = cv2.flip(absolute,1)
    
    
    #fingerTemplateをabsoluteから作成
    tttmp = cv2.matchTemplate(absolute,fingerTemplate_sozai,cv2.TM_CCOEFF_NORMED)
    a,b,c,max_loc = cv2.minMaxLoc(tttmp)
    
    fingerTemplate = cutimg(fingerTemplate_sozai,max_loc[::-1],h_ftemp,w_ftemp)
    
    
    
    if fingerTemplate is None or fingerPoint is None:
        return
        
    #parameters
    #SUPER DAIZI!!!!!!!!!!!!!!!!!!!!!!!!!!
    #--------------------------------------------------
    markerCutOffset = 5
    fingerPlace_offset = 10

    #--------------------------------------------------


    font = cv2.FONT_HERSHEY_PLAIN
    font_size =1


    #make csvWriter
    today = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + fingerVideoname
    today = today.replace('/','')
    
    os.mkdir(today)
    os.chdir(today)
    today = today +'.csv'
    f= open(today,'ab')
    file = open("fingerplace.csv","ab")
    csvWriter = csv.writer(f)
    csvWriter_fingerplace = csv.writer(file)
    


    
    
    d,w,h  = fingerPoint.shape[::-1]
    """
    #FingerPointの幅で円のテンプレ作成
    #もういらなくなったのでコメントアウト
    img = np.zeros((h,w),np.uint8)
    cv2.circle(img,(h/2,w/2),h/2-7,255,-1)
    """
    ret , videoFrame = fingerVideo.read()
    #videoFrame = cv2.flip(videoFrame,1)



    if not(ret):
        print "error!  video cannot read!"
        return  
    #call videoparam
    #ビデオの設定！
    __outVideo_frameRate = float(60.0)
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
    rec_fingerFrameName = 'fingerFrameVideo.avi'
    rec_VideoFrameName = 'VideoFrameVideo.avi'
    tmp_fingerTemplate_videoshape = (w_ftemp,h_ftemp)
    tmp_fingerVideo_videoshape = (videoFrame.shape[1],videoFrame.shape[0])


    outVideo_fingertemplate = cv2.VideoWriter(rec_fingerFrameName,
                                              fourcc,
                                              __outVideo_frameRate,
                                              tmp_fingerTemplate_videoshape)
    outVideo_VideoFrame = cv2.VideoWriter(rec_VideoFrameName,
                                          fourcc,
                                          __outVideo_frameRate,
                                          tmp_fingerVideo_videoshape)
    outVideo_Arrow = cv2.VideoWriter('arrow.avi',
                                          fourcc,
                                          20.0,
                                          (w_ftemp,h_ftemp))






    #make Gaussian Filter
    fingerTemplate = cv2.GaussianBlur(fingerTemplate,(5,5),0)
    fingerPoint = cv2.GaussianBlur(fingerPoint,(5,5),0)
    videoFrame = cv2.GaussianBlur(videoFrame,(5,5),0)



    
    
    """
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
    fingerPoint_IO = IO_exchange(fingerPoint,lower,upper)
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
    
    
    
    #マーカー場所にあたりを付ける作業
    matchtemplate_result = cv2.matchTemplate(fingerTemplate,
                            fingerPoint,
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
    threshold = 0.70
    point_loc = np.where(matchtemplate_result_shape >= threshold)
 
     #<<<<<<<point_locは(y(array),x(array))順に入っていますよ！！！！！>>>>>>>>>>>>>>>

    #print loc[::-1]

    #------------ココらへんからデバッグ-------------

    
    """
    2016-09-01　18:19　もう意味が無いけど，Tipsの意味で残しておく．
    #このアスタリスクの意味
    そもそもpoint_locが(array,array)の形になっている
    （arrayが２つタプルの中に入ってしまっている）ので，アスタリスクでタプルを展開する必要がある．
    zipは引数として，zip(array,array)みたいな感じになるので．
    もしアスタリスクがなければ，zip((array,array))で引数一つじゃねーかと突っ込まれる．
    """

    #np.c_は配列のattendと一緒！
    point_loca = np.c_[point_loc[0],point_loc[1]]
    point_loca = nearbypoint_delete(point_loca,nearbywindow)

    #新しい場所を入れる用の配列
    point_loc_new = np.array(point_loca)
    point_cut_place = np.array(point_loca)

    #csvHeaderの記入．
    csvWriter.writerow(make_y_x_pattern(len(point_loca)))

    fingerTemplate_show = np.array(fingerTemplate)

    #デバッグとか行ってるけど，通常状態でも付けておいた方が賢明です．
    if debug_max == True:
        for i in xrange(len(point_loca)):
            cv2.rectangle(fingerTemplate_show,(int(round(point_loca[i][1])),int(round(point_loca[i][0]))),
                (int(round(point_loca[i][1]))+w,int(round(point_loca[i][0]))+h),
                (0,0,255),2)
            text = str(i)
            cv2.putText(fingerTemplate_show,text,(int(round(point_loca[i][1])),int(round(point_loca[i][0]))),font, font_size,(255,255,0))

        tmp = cv2.minMaxLoc(matchtemplate_result_shape)
        print tmp[1],tmp[3]
        cv2.namedWindow("fiasn")
        cv2.setMouseCallback("fiasn",onMouse,["fiasn",fingerTemplate])
        cv2.imshow("test",fingerTemplate_show)
        cv2.imshow("fingertemp",matchtemplate_result_shape)
        cv2.imshow("fiasn",fingerTemplate)
        cv2.imshow("asfdf",fingerPoint)
        cv2.imshow("videoFrame",videoFrame)
        cv2.imshow("tesasdhfjd",videoFrame)
        cv2.imshow("jshshshshsh",tttmp)
        cv2.imshow("sfsdfjsdfksdjkf",absolute)
        cv2.imwrite("markerIO.jpg",fingerTemplate)
        cv2.imwrite("fingertmp.jpg",fingerTemplate_show)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print len(point_loca)
        


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
    fingerVideo.set(cv2.CAP_PROP_POS_FRAMES,skipframes)
    counter = skipframes
    while(fingerVideo.isOpened()):
        print "nowframe: %d" % counter

        #カウンタとかビデオのフレーム読みとか
        counter = counter +1
        ret , videoFrame = fingerVideo.read()
        #videoFrame  = cv2.flip(videoFrame,1)
        """
        videoFrame = np.zeros((1500,1000,3),np.uint8)
        videoFrame = 255 - videoFrame
        ty = ty+1
        videoFrame[tx:fingerTemplate.shape[0]+tx,ty:fingerTemplate.shape[1]+ty] = fingerTemplate#これで座標をずらしながら出来る．
        """
        arrowimg = np.zeros((h_ftemp,w_ftemp),np.uint8)
  

        
        if not(ret):

            print "MovieFrame cannot read!"
            break
        


        #ガウシアンフィルタ
        videoFrame = cv2.GaussianBlur(videoFrame,(5,5),0)
        #videoFrame_IO = IO_exchange(videoFrame,lower,upper)

        #これで，ゆびの場所をとる
        fingerplace,fingerplace__ = getfingerplace(absolute,videoFrame,fingerPlace_offset)
        
        #指のとこだけトリミング
        videoFrame_Finger = cutimg(videoFrame,fingerplace,h_ftemp,w_ftemp)


        #CSV出力用の配列宣言
        newMarkerplace = np.empty((0,2),float)
        marker_cutplace = np.empty((0,2))
        #各マーカーのある場所に対して
        for i in xrange(len(point_loca)):

            #前の画像からマーカのとこだけカット
            markerTemplate = cutimg(fingerTemplate,point_loca[i],h,w)
            
            #今のフレームからオフセットつけた矩形の中でテンプレートマッチング
            tmp___ =find_marker(markerTemplate,point_loca[i],videoFrame_Finger,markerCutOffset,i)
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
                #ccccc = cutimg(videoFrame_Finger,cutppoint,h+(markerCutOffset*2),w+(markerCutOffset*2)) 

                #cv2.imshow("asdkljlsdfjlskd",ccccc)

        #csv書き出し
        csvWriter.writerow(flatten(newMarkerplace))
        csvWriter_fingerplace.writerow(fingerplace__)

        #新マーカーポイントコピー・指座標画像コピー
        point_loc_new = np.array(newMarkerplace)
        point_cut_place = np.array(marker_cutplace)

        
        #fingerTemplate = np.array(videoFrame_Finger)
        #こいつは，指のテンプレートを新しい座標でとってしまってたので，コメントアウトしました．
        #2016/09/07．
        videoFrame_Finger_print = np.array(videoFrame_Finger)

        
        #四角形を書くよ！
        for i in xrange(len(point_loc_new)):
            if point_loc_new[i][0] == "Nan":
                continue

            #print "point_loca %s" % point_loca
            #各マーカーに四角形を書くよ
            cv2.rectangle(videoFrame_Finger_print,(int(point_loc_new[i][1]),int(point_loc_new[i][0])),
                (int(point_loc_new[i][1])+w,int(point_loc_new[i][0])+h),
                (0,0,255),2)
        #指のところに四角形を書くよ
        cv2.rectangle(videoFrame,fingerplace[::-1],(fingerplace[1]+w_ftemp,fingerplace[0]+h_ftemp),(0,0,255),3)
        
        #動画チックに見せるよ
        
        cv2.imshow('frame',videoFrame_Finger_print)
        cv2.imshow('allframe',videoFrame)
        cv2.imshow("arrow",arrowimg)
        cv2.imshow("fingertemplate",fingerTemplate)        

        #VideoOutput用にフレームを書きだすよ
        outVideo_fingertemplate.write(videoFrame_Finger_print)
        outVideo_VideoFrame.write(videoFrame)
        #arrowimg = cv2.resize(arrowimg,(w_ftemp,h_ftemp))
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
    fingerVideo.release()
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
    sys.exit(main())


