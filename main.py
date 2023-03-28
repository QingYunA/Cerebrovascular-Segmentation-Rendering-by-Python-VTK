#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023/03/28 09:27:41
@Author  :   Serein
@Version :   1.0
@Contact :   serein7z@163.com
@License :   (C)Copyright 2022-2023, USTB_MedicalAI
@Desc    :   {main of vtk}
'''
import vtk
import itk
# import yaml
from utils import yaml_read
from utils.conf_base import Default_Conf
from vtk_utils import *
from utils.data_path_process import *
from tqdm import tqdm
from metrics import *


def render_init(conf, source_path, window_index, view_port, confusion_matrix):
    actors = []
    mc_list = []
    # mhd_data = mhd2itk(source_path)
    #* 获取polydata
    # mc = create_MC(conf, mhd_data)
    # mc_list.appen(mc)
    #* set mapper
    # mapper = create_mapper(conf, mc)
    #* set actor

    # actor = create_actor(conf, mapper, color=conf.self_color)
    # actors.append(actor)
    if conf.render_mode == 'pred and gt':
        for index, (array, color) in enumerate(zip(confusion_matrix, conf.confusion_color)):
            itk_data = np2itk(array)
            confusion_MC = create_MC(conf, itk_data)
            # mc_list.append(confusion_MC)
            confusion_mapper = create_mapper(conf, confusion_MC)
            alpha = 1
            # if index == 0 or index == 1:
            #     alpha = 0.8
            actor = create_actor(conf, confusion_mapper, color=color, alpha=alpha)
            actors.append(actor)
    # append_poly = vtk.vtkAppendPolyData()
    # for mc in mc_list:
    #     append_poly.AddInputConnection(mc.GetOutputPort())
    # #* set renderer

    # mapper = create_mapper(conf, append_poly)
    # actor = create_actor(conf, mapper, color=conf.self_color)
    renderer = create_render(conf, actors)

    renderer.SetViewport(view_port[window_index])

    return renderer


def main(conf):
    select_path(conf)
    view_port = get_viewport(conf)

    renders = []
    for index, (pred_path, gt_path) in tqdm(enumerate(zip(conf.data_path, conf.gt_path)),
                                            total=len(conf.data_path),
                                            desc='rendering'):
        if conf.render_mode == 'pred and gt':
            confusion_matrix = metric_evaluation(pred_path, gt_path)
            renders.append(render_init(conf, pred_path, index, view_port, confusion_matrix))

    #* set render window
    render_window = create_render_window(conf, renders)

    #* set interactor
    interactor = create_interactor(conf, render_window)

    #* start render and interactor
    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    conf_path = './conf.yml'
    conf = Default_Conf()
    conf.update(yaml_read(conf_path))
    # conf.update
    main(conf)
