#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./increase_picture.py hogehoge.jpg
#

import cv2
import numpy as np
import sys
import os
from shutil import copyfile
# ヒストグラム均一化
def equalizeHistRGB(src):
    
    RGB = cv2.split(src)
    Blue   = RGB[0]
    Green = RGB[1]
    Red    = RGB[2]
    for i in range(3):
        cv2.equalizeHist(RGB[i])

    img_hist = cv2.merge([RGB[0],RGB[1], RGB[2]])
    return img_hist

# ガウシアンノイズ
def addGaussianNoise(src):
    row,col,ch= src.shape
    mean = 0
    var = 0.1
    sigma = 15
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    gauss = gauss.reshape(row,col,ch)
    noisy = src + gauss
    
    return noisy

# salt&pepperノイズ
def addSaltPepperNoise(src):
    row,col,ch = src.shape
    s_vs_p = 0.5
    amount = 0.004
    out = src.copy()
    # Salt mode
    num_salt = np.ceil(amount * src.size * s_vs_p)
    coords = [np.random.randint(0, i-1 , int(num_salt))
                 for i in src.shape]
    out[coords[:-1]] = (255,255,255)

    # Pepper mode
    num_pepper = np.ceil(amount* src.size * (1. - s_vs_p))
    coords = [np.random.randint(0, i-1 , int(num_pepper))
             for i in src.shape]
    out[coords[:-1]] = (0,0,0)
    return out


def main(data_dir, file_name, class_num, class_name, out_dir):

    # ルックアップテーブルの生成
    min_table = 50
    max_table = 205
    diff_table = max_table - min_table
    gamma1 = 0.75
    gamma2 = 1.5

    LUT_HC = np.arange(256, dtype = 'uint8' )
    LUT_LC = np.arange(256, dtype = 'uint8' )
    LUT_G1 = np.arange(256, dtype = 'uint8' )
    LUT_G2 = np.arange(256, dtype = 'uint8' )

    LUTs = []

    # 平滑化用
    average_square = (10,10)

    # ハイコントラストLUT作成
    for i in range(0, min_table):
        LUT_HC[i] = 0
               
    for i in range(min_table, max_table):
        LUT_HC[i] = 255 * (i - min_table) / diff_table
                                  
    for i in range(max_table, 255):
        LUT_HC[i] = 255

    # その他LUT作成
    for i in range(256):
        LUT_LC[i] = min_table + i * (diff_table) / 255
        LUT_G1[i] = 255 * pow(float(i) / 255, 1.0 / gamma1) 
        LUT_G2[i] = 255 * pow(float(i) / 255, 1.0 / gamma2)

    LUTs.append(LUT_HC)
    LUTs.append(LUT_LC)
    LUTs.append(LUT_G1)
    LUTs.append(LUT_G2)

    # 画像の読み込み
    img_src = cv2.imread(
        "{0}/images/{1}/{2}".format(data_dir, class_num, file_name), 1)
    trans_img = []
    trans_img.append(img_src)
    
    # LUT変換
    for i, LUT in enumerate(LUTs):
        trans_img.append( cv2.LUT(img_src, LUT))

    # 平滑化      
    trans_img.append(cv2.blur(img_src, average_square))      

    # ヒストグラム均一化
    trans_img.append(equalizeHistRGB(img_src))

    # ノイズ付加
    trans_img.append(addGaussianNoise(img_src))
    trans_img.append(addSaltPepperNoise(img_src))

    # 反転
    flip_num = len(trans_img)
    flip_img = []
    for img in trans_img:
        flip_img.append(cv2.flip(img, 1))
    trans_img.extend(flip_img)
    if not os.path.exists("{0}/{1}".format(data_dir, out_dir)):
        os.makedirs("{0}/{1}".format(data_dir, out_dir))
    if not os.path.exists("{0}/inflated_labels".format(data_dir)):
        os.makedirs("{0}/inflated_labels".format(data_dir))

    # 保存
    base = os.path.splitext(os.path.basename(file_name))[0] + "_"
    img_src.astype(np.float64)
    for i, img in enumerate(trans_img):
        if not os.path.exists("{0}/{1}/{2}".format(data_dir, out_dir, class_name)):
            os.makedirs("{0}/{1}/{2}".format(data_dir, out_dir, class_name))
        if not os.path.exists("{0}/inflated_labels/{1}".format(data_dir, class_name)):
            os.makedirs("{0}/inflated_labels/{1}".format(data_dir, class_name))
        new_file_name = base + str(i)
        text_file_name = file_name.replace(".jpg", ".txt")
        cv2.imwrite(
            "{0}/{1}/{2}/{3}".format(data_dir, out_dir, class_name, new_file_name + ".jpg"), img)
        if i < flip_num:
            copyfile("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name),
                     "{0}/inflated_labels/{1}/{2}".format(data_dir, class_name, new_file_name + ".txt"))
        else:
            with open("{0}/inflated_labels/{1}/{2}".format(data_dir,
                                                           class_name,
                                                           new_file_name + ".txt"), "w") as new_bb_data:
                with open("{0}/labels/{1}/{2}".format(data_dir, class_num, text_file_name), "r") as bb_data:
                    for line in bb_data.readlines():
                        elems = line.split(' ')
                        if len(elems) != 4:
                            new_bb_data.write(line)
                            continue
                        x1 = int(elems[0])
                        y1 = int(elems[1])
                        x2 = int(elems[2])
                        y2 = int(elems[3])
                        width = img_src.shape[1]
                        new_bb_data.write("{0} {1} {2} {3}\n".format(
                            width - x2, y1, width - x1, y2))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("please set data directory path.")
        print ("python inflate_images.py [input_dir] [out_dir]")
        exit(-1)
    
    
    # 増幅するフォルダ名の決定
    out_dir = "obj"
    if len(sys.argv) > 2:
    	out_dir = sys.argv[2]
    	
    data_dir = sys.argv[1]
    
    # クラス名のファイルの読み込み
    classes = []
    classes = [line.rstrip() for line in open('{0}/classes.txt'.format(data_dir), 'r')]
    
    print('class name = ', end='')
    for i in classes:
    	print(i, end=' ')
    print("")
    
    for _, dirs, _ in os.walk("{0}/images/".format(data_dir)):
        for class_num,class_name in zip(dirs, classes):
            for _, _, files in os.walk("{0}/images/{1}".format(data_dir, class_num)):
                for file_name in files:
                    main(data_dir, file_name, class_num, class_name, out_dir)
