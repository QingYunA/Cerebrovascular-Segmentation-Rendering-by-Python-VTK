import vtk
import itk
from vtk.util import numpy_support


class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, parent=None):
        self.parent = vtk.vtkRenderWindowInteractor()
        if parent is not None:
            self.parent = parent

        self.ResetKey = "r"

    def ResetCamera(self):
        self.parent.ResetCamera()

    def OnKeyPress(self):
        key = self.parent.GetKeySym()

        if key == self.ResetKey:
            self.ResetCamera()

        vtk.vtkInteractorStyleTrackballCamera.OnKeyPress(self)


def mhd2vtk(mhd_path):
    data = itk.imread(mhd_path)
    vtk_data = itk.vtk_image_from_image(data)
    return vtk_data


def np2itk(np_data):
    data = itk.GetImageFromArray(np_data)
    vtk_data = itk.vtk_image_from_image(data)
    return vtk_data


def create_MC(conf, mhd_data):
    cubes = vtk.vtkMarchingCubes()
    cubes.SetInputData(mhd_data)
    cubes.SetNumberOfContours(conf.number_of_contours)
    cubes.SetValue(conf.cube_value[0], conf.cube_value[1])
    cubes.Update()
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetInputConnection(cubes.GetOutputPort())
    smoothFilter.SetNumberOfIterations(conf.iterations)
    smoothFilter.Update()
    return smoothFilter


def create_glyph(conf, vtk_data):
    #* 设置glyph
    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(vtk_data)
    glyph.SetSourceConnection(conf.glyph_source.GetOutputPort())
    glyph.SetVectorModeToUseNormal()
    glyph.SetScaleModeToScaleByVector()
    glyph.SetScaleFactor(conf.glyph_scale)
    glyph.OrientOn()
    glyph.Update()
    return glyph.GetOutput()


def create_mapper(conf, mc):
    #* 设置mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(mc.GetOutput())
    mapper.ScalarVisibilityOff()

    return mapper


def create_actor(conf, mapper, color=None, alpha=None):
    # actor = vtk.vtkActor()
    actor = vtk.vtkLODActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetInterpolationToGouraud()
    if color:
        actor.GetProperty().SetColor(color)

    if alpha:
        actor.GetProperty().SetOpacity(alpha)
    return actor


def create_render(conf, actors):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(conf.background)
    for actor in actors:
        renderer.AddActor(actor)

    return renderer


def create_render_window(conf, renderers):
    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(conf.window_size)
    for renderer in renderers:
        render_window.AddRenderer(renderer)

    return render_window


def create_interactor(conf, render_window):
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    my_style = MyInteractorStyle(interactor)
    interactor.SetInteractorStyle(my_style)
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