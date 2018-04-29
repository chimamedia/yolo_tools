# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import random
import time
from os import walk, getcwd
from PIL import Image

# ここに分類するクラスを記述する。
classes = []

def create_config(data_dir, train_ratio):
    all_list = []
    for i in classes:
        # list_file = open("{0}/darknet_data/config/{1}_list.txt".format(data_dir, i + 1), 'r')
        list_file = open("{0}/config/{1}_list.txt".format(data_dir, i), 'r')
        for file_name in list_file.readlines():
            if not (file_name in all_list):
                all_list.append(file_name)
    
    if(train_ratio > 0):
        random.shuffle(all_list)
        train_num = int(train_ratio * len(all_list))
        train_list = all_list[:train_num]
        valid_list = all_list[train_num:]
    else:
        train_list = all_list
        valid_list = all_list
    
    train_list_file = open("{0}/config/train.txt".format(data_dir), "w")
    for file_name in train_list:
        train_list_file.write(file_name)
    train_list_file.close()
    # valid_list_file = open("{0}/darknet_data/config/valid.txt".format(data_dir), "w")
    valid_list_file = open("{0}/config/valid.txt".format(data_dir), "w")
    for file_name in valid_list:
        valid_list_file.write(file_name)
    valid_list_file.close()

    # data_config = open("{0}/darknet_data/config/learning.data".format(data_dir), "w")
    data_config = open("{0}/config/learning.data".format(data_dir), "w")
    data_config.write("classes = {0}\n".format(len(classes)))
    data_config.write("train = {0}/config/train.txt\n".format(data_dir))
    data_config.write("valid = {0}/config/valid.txt\n".format(data_dir))
    data_config.write("names = {0}/config/learning.names\n".format(data_dir))
    data_config.write("backup = backup\n")
    data_config.close()
    
    names_config = open("{0}/config/learning.names".format(data_dir), "w")
    for i in classes:
        names_config.write("{0}\n".format(i))
    names_config.close()

    base_config = open("base.cfg", "r")
    # new_config = open("{0}/darknet_data/config/learning.cfg".format(data_dir), "w")
    new_config = open("{0}/config/learning.cfg".format(data_dir), "w")

    for line in base_config.readlines():
        if line.find("$FILTERS_NUM") != -1:
            filter_num = 5 * (len(classes) + 4 + 1)
            new_config.write("filters={0}\n".format(filter_num))
        elif line.find("classes") != -1:
            new_config.write("classes={0}\n".format(len(classes)))
        else:
            new_config.write(line)
    base_config.close()
    new_config.close()
    



# 変換処理
def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def main(data_dir, obj_dir):
    # 分類クラス分繰り返す
    for cls in classes:
    	
        # labelデータ input path
        mypath = "{0}/inflated_labels/{1}/".format(data_dir, cls)
        # labelデータ output path
        outpath = "{0}/{1}/{2}/".format(data_dir, obj_dir, cls)
    
        wd = getcwd()
        cls_id = classes.index(cls)
        
        # configフォルダを作成
        confDir = "{0}/config".format(data_dir)
        if not os.path.exists(confDir):
            os.makedirs(confDir)
        
        # outputファイルのpathが列挙されるリストファイル
        list_file = open('%s/%s/config/%s_list.txt'%(wd, data_dir, cls), 'w')
    
        # input ファイル名を取得
        txt_name_list = []
        for (dirpath, dirnames, filenames) in walk(mypath):
            txt_name_list.extend(filenames)
        print ("txt_name_list = " + str(txt_name_list))
    
        # input ファイル数分変換処理
        for txt_name in txt_name_list:
    
            # inputファイルを読み込み、行に分割
            txt_path = mypath + txt_name
            txt_file = open(txt_path, "r")
            lines = txt_file.read().replace("\r\n","\n").split('\n')
    
            # outputファイル作成
            txt_outpath = outpath + txt_name
            txt_outfile = open(txt_outpath, "w")
    
    
            ct = 0
            for line in lines:
                if(len(line) >= 4):
                    ct = ct + 1
                    print(line + "\n")
                    elems = line.split(' ')
                    print(elems)
                    xmin = elems[0]
                    xmax = elems[2]
                    ymin = elems[1]
                    ymax = elems[3]
                    # img_path = str('%s/%s/inflated_images/%s/%s.jpg'%(wd, data_dir, cls, os.path.splitext(txt_name)[0]))
                    img_path = str('%s/%s/%s/%s.jpg'%(data_dir, obj_dir, cls, os.path.splitext(txt_name)[0]))
                    im=Image.open(img_path)
                    w= int(im.size[0])
                    h= int(im.size[1])
                    b = (float(xmin), float(xmax), float(ymin), float(ymax))
                    bb = convert((w,h), b)
                    txt_outfile.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
    
            if(ct != 0):
                # list_file.write('%s/inflated_images/%s/%s.jpg\n'%(wd, cls, os.path.splitext(txt_name)[0]))
                list_file.write('%s/%s/%s/%s.jpg\n'%(data_dir, obj_dir, cls, os.path.splitext(txt_name)[0]))
    
        list_file.close()
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("please set data directory path.")
        print ("python [input_folder] [inflated_images_folder] [learing_ratio]\n\n")
        exit(-1)
    data_dir = sys.argv[1]
    
    obj_dir = "obj"
    if len(sys.argv) > 2:
    	obj_dir = sys.argv[2]
    
    # クラス名のファイルの読み込み
    classes = [line.rstrip() for line in open('{0}/classes.txt'.format(data_dir), 'r')]
    print('class name = ', end='')
    for i in classes:
    	print(i, end=' ')
    print("")
    
    # 学習の割合
    train_ratio = -1
    if len(sys.argv) > 3:
        train_ratio = float(sys.argv[3])
    
    #メインプログラム
    main(data_dir, obj_dir)
    create_config(data_dir, train_ratio)
    
    #不要なリストを削除する
    for i in classes:
        subprocess.call("del {0}\\config\\{1}_list.txt".format(data_dir, i), shell=True)
