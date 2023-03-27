import vtk
import itk
# import yaml
from utils import yaml_read
from utils.conf_base import Default_Conf
from vtk_utils import *
from utils.data_path_process import process
from tqdm import tqdm
from heartrate import trace, files


def render_init(conf, source_path, window_index, view_port):
    mhd_data = read_mhd(source_path)

    #* 获取polydata
    surface = get_surface(conf, mhd_data)

    #* set mapper
    mapper = create_mapper(conf, surface)

    #* set actor
    actor = create_actor(conf, mapper)
    #* set renderer
    renderer = create_render(conf, actor)

    renderer.SetViewport(view_port[window_index])

    return renderer


def main(conf):
    process(conf)
    view_port = get_viewport(conf)

    renders = []
    for index, path in tqdm(enumerate(conf.data_path), total=len(conf.data_path), desc='rendering'):
        renders.append(render_init(conf, path, index, view_port))

    #* set render window
    render_window = create_render_window(conf, renders)

    #* set interactor
    interactor = create_interactor(conf, render_window)

    #* start render and interactor
    render_window.Render()
    interactor.Start()


if __name__ == '__main__':
    # heartrate.trace(browser=True)
    trace(files=files.all)
    conf_path = './conf.yml'
    conf = Default_Conf()
    conf.update(yaml_read(conf_path))
    # conf.update
    main(conf)
