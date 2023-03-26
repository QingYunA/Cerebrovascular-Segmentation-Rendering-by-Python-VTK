import vtk
import itk


def read_mhd(mhd_path):
    data = itk.imread(mhd_path)
    vtk_data = itk.vtk_image_from_image(data)
    return vtk_data


def get_surface(mhd_data):
    cubes = vtk.vtkMarchingCubes()
    cubes.SetInputData(mhd_data)
    cubes.SetNumberOfContours(1)
    cubes.SetValue(0, 0.5)
    cubes.Update()
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetInputConnection(cubes.GetOutputPort())
    smoothFilter.SetNumberOfIterations(200)
    smoothFilter.Update()
    return smoothFilter.GetOutput()


if __name__ == '__main__':
    path = './data/01.mhd'
    self_color = [0.74, 0.06, 0.06]
    mhd_data = read_mhd(path)
    #* 获取polydata
    surface = get_surface(mhd_data)
    #* 设置mapper
    cube_mapper = vtk.vtkPolyDataMapper()
    cube_mapper.SetInputData(surface)
    cube_mapper.ScalarVisibilityOff()

    cube_actor = vtk.vtkActor()
    cube_actor.SetMapper(cube_mapper)
    cube_actor.GetProperty().SetColor(self_color)
    cube_actor.GetProperty().SetInterpolationToGouraud()
    cube_actor.GetProperty().SetOpacity(1)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1, 1, 1)
    renderer.AddActor(cube_actor)

    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName('python vtk')
    render_window.SetSize(800, 800)
    render_window.AddRenderer(renderer)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    interactor.Initialize()
    render_window.Render()
    interactor.Start()
