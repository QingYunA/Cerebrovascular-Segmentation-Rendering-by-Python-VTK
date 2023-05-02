#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   metrics.py
@Time    :   2023/03/01 18:19:56
@Author  :   Serein
@Version :   1.0
@Contact :   serein7z@163.com
@License :   (C)Copyright 2022-2023, USTB_MedicalAI
@Desc    :   {get metrics from predict file}
'''
from pathlib import Path
import numpy as np
import copy
from tqdm import tqdm
import SimpleITK as sitk
from utils import yaml_read
from utils.conf_base import Default_Conf


def make_subject(image_paths, label_paths, suffixes):
    images_dir = Path(image_paths)
    labels_dir = Path(label_paths)

    image_paths = sorted(images_dir.glob(suffixes))
    label_paths = sorted(labels_dir.glob(suffixes))
    subjects = []
    for (image_path, label_path) in zip(image_paths, label_paths):
        subject = tio.Subject(
            pred=tio.ScalarImage(image_path),
            gt=tio.LabelMap(label_path),
        )
        subjects.append(subject)
    return subjects


def load_itk(filename):
    # 读取图像
    itkimage = sitk.ReadImage(filename)
    # 转换为numpy数组
    numpyImage = sitk.GetArrayFromImage(itkimage)
    # 获取原点和间距
    # numpyOrigin = np.array(list(reversed(itkimage.GetOrigin())))
    # numpySpacing = np.array(list(reversed(itkimage.GetSpacing())))
    return numpyImage


def metric_evaluation(pred_path, gt_path, suffixes="*.mhd"):

    # pred_paths = sorted(Path(predict_dir).glob(suffixes))
    # label_paths = sorted(Path(labels_dir).glob(suffixes))

    # for i, (pred_path, label_path) in tqdm(enumerate(zip(pred_paths, label_paths)),
    #                                        total=len(pred_paths),
    #                                        desc="Generating metrics"):
    preds = load_itk(pred_path)
    gts = load_itk(gt_path)

    pred = preds.astype(int)  # float data does not support bit_and and bit_or
    gdth = gts.astype(int)  # float data does not support bit_and and bit_or
    fp_array = copy.deepcopy(pred)  # keep pred unchanged
    fn_array = copy.deepcopy(gdth)

    intersection = gdth & pred  # only both 1 will be 1
    union = gdth | pred

    tp_array = intersection

    tmp = pred - gdth
    fp_array[tmp < 1] = 0  # fp : false positive

    tmp2 = gdth - pred
    fn_array[tmp2 < 1] = 0

    tn_array = np.ones(gdth.shape) - union

    fp_array = np.array(fp_array, dtype=np.int8)
    fn_array = np.array(fn_array, dtype=np.int8)
    tp_array = np.array(tp_array, dtype=np.int8)
    tn_array = np.array(tn_array, dtype=np.int8)
    return [fp_array, fn_array, tp_array]


if __name__ == '__main__':
    conf_path = './conf.yml'
    conf = Default_Conf()
    conf.update(yaml_read(conf_path))
    metric_evaluation(conf.data_path, conf.gt_path)
