import vtk
import itk


def save_png(conf, render_window):
    writer = vtk.vtkPNGWriter()
    wif = vtk.vtkWindowToImageFilter()
    wif.SetInput(render_window)

    writer.SetFileName(conf.save_path + conf.save_name_png)
    writer.SetInputConnection(wif.GetOutputPort())
    writer.Write()


def save_vtk(poly_data, save_path):
    writer = vtk.vtkPolyDataWriter()
    writer.SetInputData(poly_data)
    writer.SetFileName(save_path)
    writer.Write()


def save_obj(poly_data, save_path):
    writer = vtk.vtkOBJWriter()
    writer.SetInputData(poly_data)
    writer.SetFileName(save_path)
    writer.Write()


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
    if conf.save_obj:
        save_obj(smoothFilter.GetOutput(), conf.save_path + conf.save_name_obj)
    return smoothFilter


def create_glyph(conf, vtk_data):
    # * 设置glyph
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
    # * 设置mapper
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
    if file_num == 0:
        raise ValueError("No data to show! Check your data path.")
    if conf.layout == "1*n":
        column = file_num
        view_port = []
        space = 1 / column
        for i in range(column):
            view_port.append([i * space, 0, (i + 1) * space, 1])
        return view_port
    elif conf.layout == "2*n":
        column = file_num // 2 if file_num % 2 == 0 else file_num // 2 + 1
        view_port = []
        space = 1 / column
        for i in range(2):
            for j in range(column):
                view_port.append([j * space, 0.5 - i * 0.5, (j + 1) * space, 1 - i * 0.5])
        return view_port


def single_render_init(conf, window_index, pred_path, view_port, camera):
    mhd_vtk = mhd2vtk(pred_path)
    mc = create_MC(conf, mhd_vtk)
    mapper = create_mapper(conf, mc)
    actor = create_actor(conf, mapper, color=conf.red_color, alpha=1)
    renderer = create_render(conf, [actor])

    renderer.SetViewport(view_port[window_index])

    if window_index == 0:
        camera = renderer.GetActiveCamera()
    else:
        renderer.SetActiveCamera(camera)

    renderer.ResetCamera()

    return renderer, camera


def multi_render_init(conf, window_index, view_port, confusion_matrix, camera):
    actors = []
    mc_list = []
    # * create actors
    for index, (array, color) in enumerate(zip(confusion_matrix, conf.confusion_color)):
        itk_data = np2itk(array)
        confusion_MC = create_MC(conf, itk_data)
        mc_list.append(confusion_MC)
        confusion_mapper = create_mapper(conf, confusion_MC)
        alpha = 1
        if index == 2:
            alpha = conf.alpha
        actor = create_actor(conf, confusion_mapper, color=color, alpha=alpha)
        actors.append(actor)

    renderer = create_render(conf, actors)

    renderer.SetViewport(view_port[window_index])

    if window_index == 0:
        camera = renderer.GetActiveCamera()
    else:
        renderer.SetActiveCamera(camera)

    renderer.ResetCamera()

    return renderer, actors, mc_list, camera


def color_bar_init(conf, window_index, pred_path, gt_path, view_port, camera):
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
    mapper.SetScalarRange(
        output_polydata.GetPointData().GetScalars().GetRange()[0], output_polydata.GetPointData().GetScalars().GetRange()[1]
    )
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(mapper.GetLookupTable())
    scalar_bar.SetTitle("Distance")
    scalar_bar.SetNumberOfLabels(conf.color_bar_labels)
    scalar_bar.UnconstrainedFontSizeOn()

    colors = vtk.vtkNamedColors()

    renderer = create_render(conf, [actor])
    renderer.AddActor2D(scalar_bar)

    renderer.SetViewport(view_port[window_index])

    if window_index == 0:
        camera = renderer.GetActiveCamera()
    else:
        renderer.SetActiveCamera(camera)

    renderer.ResetCamera()

    return renderer, camera
