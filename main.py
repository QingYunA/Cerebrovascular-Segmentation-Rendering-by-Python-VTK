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
import time


def pred_render_init(conf, pred_path, window_index, view_port):
    mhd_vtk = mhd2vtk(pred_path)
    mc = create_MC(conf, mhd_vtk)
    mapper = create_mapper(conf, mc)
    actor = create_actor(conf, mapper, color=conf.red_color, alpha=1)
    render = create_render(conf, [actor])

    return render


def multi_render_init(conf, window_index, view_port, confusion_matrix):
    actors = []
    mc_list = []
    #* create actors
    for index, (array, color) in enumerate(zip(confusion_matrix, conf.confusion_color)):
        itk_data = np2itk(array)
        confusion_MC = create_MC(conf, itk_data)
        mc_list.append(confusion_MC)
        confusion_mapper = create_mapper(conf, confusion_MC)
        alpha = 1
        if index == 0 or index == 1:
            alpha = 0.8
        actor = create_actor(conf, confusion_mapper, color=color, alpha=alpha)
        actors.append(actor)

    renderer = create_render(conf, actors)

    renderer.SetViewport(view_port[window_index])

    return renderer, actors, mc_list


def colorbar_init(conf, pred_path, gt_path, view_port):
    pred_vtk = mhd2vtk(pred_path)
    gt_vtk = mhd2vtk(gt_path)

    pred_mc = create_MC(conf, pred_vtk)
    gt_mc = create_MC(conf, gt_vtk)

    distance_filter = vtk.vtkDistancePolyDataFilter()
    distance_filter.SetInputData(0, pred_mc.GetOutput())
    distance_filter.SetInputData(1, gt_mc.GetOutput())
    distance_filter.Update()

    output_polydata = distance_filter.GetOutput()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(output_polydata)
    mapper.SetScalarRange(output_polydata.GetPointData().GetScalars().GetRange()[0],
                          output_polydata.GetPointData().GetScalars().GetRange()[1])
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(mapper.GetLookupTable())
    scalar_bar.SetTitle('Distance')
    scalar_bar.SetNumberOfLabels(8)
    scalar_bar.UnconstrainedFontSizeOn()

    colors = vtk.vtkNamedColors()

    renderer = create_render(conf, [actor])
    renderer.AddActor2D(scalar_bar)

    return renderer


def main(conf):
    select_path(conf)
    view_port = get_viewport(conf)

    start_time = time.time()
    renders = []
    window_actor_list = []
    window_mc_list = []

    if conf.render_mode == 'pred and gt':
        for index, (pred_path, gt_path) in tqdm(enumerate(zip(conf.data_path, conf.gt_path)),
                                                total=len(conf.data_path),
                                                desc='rendering'):

            confusion_matrix = metric_evaluation(pred_path, gt_path)
            render, actors, mc_list = multi_render_init(conf, index, view_port, confusion_matrix)
            window_actor_list.append(actors)
            window_mc_list.append(mc_list)
            renders.append(render)

    elif conf.render_mode == 'pred':
        for index, pred_path in tqdm(enumerate(conf.data_path), total=len(conf.data_path), desc='rendering'):
            render = pred_render_init(conf, pred_path, index, view_port)
            renders.append(render)

    elif conf.render_mode == 'colorbar':
        for index, (pred_path, gt_path) in tqdm(enumerate(zip(conf.data_path, conf.gt_path)),
                                                total=len(conf.data_path),
                                                desc='rendering'):
            render = colorbar_init(conf, pred_path, gt_path, view_port)
            renders.append(render)

    transform = vtk.vtkTransform()
    transform_filter = vtk.vtkTransformFilter()
    transform_filter.SetTransform(transform)

    for w_index, (actors, mc_list) in enumerate(zip(window_actor_list, window_mc_list)):
        for index, (actor, mc) in enumerate(zip(actors, mc_list)):
            if w_index == 0 and index == 0:
                transform_filter.SetInputConnection(mc.GetOutputPort())
            elif w_index == 0 and index != 0:
                transform_filter.AddInputConnection(mc.GetOutputPort())
            else:
                transform_filter.AddInputConnection(actor.GetMapper().GetInputConnection(0,0))

    cue = vtk.vtkAnimationCue()
    cue.SetStartTime(0)
    cue.SetEndTime(360)
    cue.SetAnimationCueInfo(transform)
    cue.SetAnimationCall(transform_filter.Update)

    scene = vtk.vtkAnimationScene()
    scene.AddCue(cue)
    scene.SetTimeModeToNormalized()
    scene.SetStartTime(0.0)
    scene.SetEndTime(1.0)

    #* set render window
    render_window = create_render_window(conf, renders)

    #* set interactor
    interactor = create_interactor(conf, render_window)
    interactor.CreateRepeatingTimer(10)
    interactor.AddObserver('TimerEvent', scene.Play)

    #* start render and interactor
    render_window.Render()

    print('render time: ', time.time() - start_time)
    interactor.Start()


if __name__ == '__main__':
    conf_path = './conf.yml'
    conf = Default_Conf()
    conf.update(yaml_read(conf_path))
    # conf.update

    main(conf)
