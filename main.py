#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/03/28 09:27:41
@Author  :   Serein
@Version :   1.0
@Contact :   serein7z@163.com
@License :   (C)Copyright 2022-2023, USTB_MedicalAI
@Desc    :   {main of vtk}
"""

import vtk
import itk

# import yaml
from utils import yaml_read
from utils.conf_base import Default_Conf
from vtk_utils import (
    single_render_init,
    multi_render_init,
    color_bar_init,
    create_render_window,
    get_viewport,
    create_interactor,
    save_png,
)
from utils.data_path_process import select_path
from tqdm import tqdm
from metrics import metric_evaluation
import time


def main(conf):
    select_path(conf)
    view_port = get_viewport(conf)

    start_time = time.time()
    renders = []
    camera = vtk.vtkCamera()

    if conf.render_mode == "single":
        for index, pred_path in tqdm(enumerate(conf.data_path), total=len(conf.data_path), desc="rendering"):
            render, camera = single_render_init(conf, index, pred_path, view_port, camera)
            renders.append(render)

    elif conf.render_mode == "multi":
        for index, (pred_path, gt_path) in tqdm(
            enumerate(zip(conf.data_path, conf.gt_path)), total=len(conf.data_path), desc="rendering"
        ):
            confusion_matrix = metric_evaluation(pred_path, gt_path)
            render, actors, mc_list, camera = multi_render_init(conf, index, view_port, confusion_matrix, camera)
            renders.append(render)

    elif conf.render_mode == "color":
        for index, (pred_path, gt_path) in tqdm(
            enumerate(zip(conf.data_path, conf.gt_path)), total=len(conf.data_path), desc="rendering"
        ):
            render, camera = color_bar_init(conf, index, pred_path, gt_path, view_port, camera)
            renders.append(render)

    # * set render window
    render_window = create_render_window(conf, renders)
    if conf.save_png:
        save_png(conf, render_window=render_window)

    # * set interactor
    interactor = create_interactor(conf, render_window)
    # * start render and interactor
    render_window.Render()

    print("render time: ", time.time() - start_time)
    interactor.Start()


if __name__ == "__main__":
    conf_path = "./conf.yml"
    conf = Default_Conf()
    conf.update(yaml_read(conf_path))
    main(conf)
