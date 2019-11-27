#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 14:55:43 2015

This script is to convert the txt annotation files to appropriate format needed by YOLO

@author: Guanghan Ning
Email: gnxr9@mail.missouri.edu
"""

# ここに分類するクラスを記述する。
classes = ["chino","rize", "cocoa", "chia", "sharo"]


import sys
import subprocess
import os
import random
import time
from os import walk, getcwd
from PIL import Image
from shutil import copyfile


def create_config(data_dir, train_ratio, class_num):
    all_list = []
    for i in range(class_num):
        # list_file = open("{0}/darknet_data/config/{1}_list.txt".format(data_dir, i + 1), 'r')
        list_file = open("{0}/data/config/{1}_list.txt".format(data_dir, i + 1), 'r')
        for file_name in list_file.readlines():
            if not (file_name in all_list):
                all_list.append(file_name)
    random.shuffle(all_list)
    train_num = int(train_ratio * len(all_list))
    train_list = all_list[:train_num]
    valid_list = all_list[train_num:]
    # train_list_file = open("{0}/darknet_data/config/train.txt".format(data_dir), "w")
    train_list_file = open("{0}/data/config/train.txt".format(data_dir), "w")
    for file_name in train_list:
        train_list_file.write(file_name)
    train_list_file.close()
    # valid_list_file = open("{0}/darknet_data/config/valid.txt".format(data_dir), "w")
    valid_list_file = open("{0}/data/config/valid.txt".format(data_dir), "w")
    for file_name in valid_list:
        valid_list_file.write(file_name)
    valid_list_file.close()

    # data_config = open("{0}/darknet_data/config/learning.data".format(data_dir), "w")
    data_config = open("{0}/data/config/learning.data".format(data_dir), "w")
    data_config.write("classes = {0}\n".format(class_num))
    data_config.write("train = config/train.txt\n")
    data_config.write("valid = config/valid.txt\n")
    data_config.write("names = config/learning.names\n")
    data_config.write("backup = backup\n")
    data_config.close()

    # names_config = open("{0}/darknet_data/config/learning.names".format(data_dir), "w")
    names_config = open("{0}/data/config/learning.names".format(data_dir), "w")
    for i in range(class_num):
        names_config.write("name{0}\n".format(i + 1))
    names_config.close()

    base_config = open("config/base.cfg", "r")
    # new_config = open("{0}/darknet_data/config/learning.cfg".format(data_dir), "w")
    new_config = open("{0}/data/config/learning.cfg".format(data_dir), "w")

    for line in base_config.readlines():
        if line.find("$FILTERS_NUM") != -1:
            filter_num = 5 * (class_num + 4 + 1)
            new_config.write("filters={0}\n".format(filter_num))
        elif line.find("classes") != -1:
            new_config.write("classes={0}\n".format(class_num))
        else:
            new_config.write(line)
    base_config.close()
    new_config.close()
    
    for i in range(class_num):
        # subprocess.call("del {0}/darknet_data/config/{1}_list.txt".format(data_dir, i + 1), shell=True)
        subprocess.call("del {0}\\data\\config\\{1}_list.txt".format(data_dir, i + 1), shell=True)


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def execute(data_dir, outpath, cls_id):
    wd = getcwd()
    print ("outpath = " + outpath)
    list_file = open(
        '{0}/config/{1}_list.txt'.format(outpath, cls_id), 'w')

    """ Get input text file list """
    txt_name_list = []
    label_path = "{0}/inflated_labels/{1}".format(data_dir, cls_id)
    for (dirpath, dirnames, filenames) in walk(label_path):
        for filename in filenames:
            if filename.find(".txt") != -1:
                txt_name_list.append(filename)
    """ Process """
    for txt_name in txt_name_list:
        """ Open input text files """
        txt_path = "{0}/{1}".format(label_path, txt_name)
        print("Input:" + txt_path)
        txt_file = open(txt_path, "r")
        lines = txt_file.readlines()

        """ Open output text files """
        txt_outpath = outpath + "/" +  txt_name
        print("Output:" + txt_outpath)
        txt_outfile = open(txt_outpath, "a")

        """ Convert the data to YOLO format """
        ct = 0
        img_path = str('{0}/inflated_images/{1}/{2}.jpg'.format
                       (data_dir, cls_id, os.path.splitext(txt_name)[0]))
        for line in lines:
            elems = line.split(' ')
            print(elems)
            if len(elems) != 4:
                continue
            ct = ct + 1

            xmin = elems[0]
            xmax = elems[2]
            ymin = elems[1]
            ymax = elems[3]
            im = Image.open(img_path)
            w = int(im.size[0])
            h = int(im.size[1])

            print(w, h)
            b = (float(xmin), float(xmax), float(ymin), float(ymax))
            bb = convert((w, h), b)
            print(bb)
            txt_outfile.write(classes[int(cls_id) - 1] + " " +
                              " ".join([str(a) for a in bb]) + '\n')

        """ Save those images with bb into list"""
        if(ct != 0):
            list_file.write('{0}/{1}/{2}.jpg\n'.format(wd, outpath,
                                                       os.path.splitext(txt_name)[0]))
            copyfile(
                img_path, "{0}/{1}.jpg".format(outpath, os.path.splitext(txt_name)[0]))

    list_file.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print ("please set data directory path and train ratio.")
        exit(-1)
    data_dir = sys.argv[1]
    train_ratio = float(sys.argv[2])
    #if not os.path.exists("{0}/darknet_data".format(data_dir)):
    if not os.path.exists("{0}/data".format(data_dir)):
        #os.makedirs("{0}/darknet_data".format(data_dir))
        os.makedirs("{0}/data".format(data_dir))
    #if not os.path.exists("{0}/darknet_data/config".format(data_dir)):
    if not os.path.exists("{0}/data/config".format(data_dir)):
        #os.makedirs("{0}/darknet_data/config".format(data_dir))
        os.makedirs("{0}/data/config".format(data_dir))
    dst_cls_num = 0
    for _, dirs, _ in os.walk("{0}/inflated_images/".format(data_dir)):
        for class_num in dirs:
            dst_cls_num += 1
            # outpath = "{0}/darknet_data/".format(data_dir)
            outpath = "{0}/data".format(data_dir)
            execute(data_dir, outpath, class_num)
    create_config(data_dir, train_ratio, dst_cls_num)
