import vtk
import itk


def read_mhd(mhd_path):
    data = itk.imread(mhd_path)
    vtk_data = itk.vtk_image_from_image(data)
    return vtk_data


def get_surface(conf, mhd_data):
    cubes = vtk.vtkMarchingCubes()
    cubes.SetInputData(mhd_data)
    cubes.SetNumberOfContours(conf.number_of_contours)
    cubes.SetValue(conf.cube_value[0], conf.cube_value[1])
    cubes.Update()
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetInputConnection(cubes.GetOutputPort())
    smoothFilter.SetNumberOfIterations(conf.iterations)
    smoothFilter.Update()
    return smoothFilter.GetOutput()


def create_mapper(conf, surface):
    #* 设置mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(surface)
    mapper.ScalarVisibilityOff()

    return mapper


def create_actor(conf, mapper):
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.SetPosition(conf.position)
    actor.GetProperty().SetColor(conf.self_color)
    actor.GetProperty().SetInterpolationToGouraud()
    actor.GetProperty().SetOpacity(1)
    return actor


def create_render(conf, actor):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(conf.background)
    renderer.AddActor(actor)

    return renderer


def create_render_window(conf, renderers):
    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(conf.window_size)
    # render_window.SetBackground(conf.background)
    for renderer in renderers:
        render_window.AddRenderer(renderer)

    return render_window


def create_interactor(conf, render_window):
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    interactor.Initialize()

    return interactor


def get_viewport(conf):
    file_num = len(conf.data_path)
    column = file_num // 2 if file_num % 2 == 0 else file_num // 2 + 1
    view_port = []
    space = 1 / column
    for i in range(2):
        for j in range(column):
            view_port.append([j * space, 0.5 - i * 0.5, (j + 1) * space, 1 - i * 0.5])
    return view_port