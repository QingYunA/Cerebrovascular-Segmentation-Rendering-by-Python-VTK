// 加入系统头文件
#include <iostream>
#include <fstream>
#include <time.h>

// 加入ITK头文件

#include "itkImage.h"
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkBinaryThresholdImageFilter.h"
#include "itkVTKImageExport.h"
#include "itkVTKImageImport.h"

// 加入VTK头文件
#include "vtkActor.h"
#include "vtkRenderer.h"
#include "vtkCamera.h"
#include "vtkRenderWindow.h"
#include "vtkRenderWindowInteractor.h"
#include "vtkProperty.h"
#include "vtkInteractorStyleTrackballCamera.h"
#include "vtkPoints.h"
#include "vtkPolyVertex.h"
#include "vtkUnstructuredGrid.h"
#include "vtkDataSetMapper.h"
#include <vtkPolyDataMapper.h>
#include <vtkMarchingCubes.h>
#include <vtkVolume16Reader.h>
#include <vtkPolyData.h>
#include <vtkProperty.h>
#include <vtkTriangleFilter.h>
#include <vtkSmoothPolyDataFilter.h>
#include <vtkDecimatePro.h>
#include <vtkSTLWriter.h>
#include "vtkWriter.h"
#include "vtkPolyDataWriter.h"

#include "vtkImageImport.h"
#include "vtkImageExport.h"
#include "vtkContourFilter.h"
#include "vtkImageData.h"
#include "vtkDataSet.h"
#include "vtkProperty.h"
#include "vtkPolyDataWriter.h"
#include "vtkDataSetSurfaceFilter.h"
#include "vtkCellArray.h"
#include "vtkSurfaceReconstructionFilter.h"
#include "vtkProgrammableSource.h"
#include "vtkContourFilter.h"
#include "vtkReverseSense.h"
#include <vtkTransform.h>
#include <vtkTransformPolyDataFilter.h>

#include <vtkSphereSource.h>
#include <vtkAppendPolyData.h>
#include <vtkCleanPolyData.h>
#include "vtkPolyDataConnectivityFilter.h"
#include "vtkDICOMImageReader.h"
#include <vtkClipPolyData.h>
#include "vtkBox.h"
#include <vtkBooleanOperationPolyDataFilter.h>
#include <vtkImplicitBoolean.h>
#include <vtkIntersectionPolyDataFilter.h>
#include <vtkPolyDataNormals.h>
#include <vtkReverseSense.h>
#include "vtkTriangleFilter.h"
#include "vtkMassProperties.h"
#include <vtkSelectEnclosedPoints.h>
#include "vtkPolyDataReader.h"
#include <vtkTransformPolyDataFilter.h>
#include "vtkMatrix4x4.h"
#include "vtkSTLReader.h"
#include <vtkCurvatures.h>
#include <vtkPolyDataReader.h>
#include <vtkLookupTable.h>
#include <vtkColorTransferFunction.h>
#include <vtkColorSeries.h>
#include <vtkScalarBarActor.h>
#include <vtkImageGaussianSmooth.h>

#include <vtkPolyDataNormals.h>
#include <vtkFillHolesFilter.h>
#include <vtkPCAAnalysisFilter.h>
#include <vtkIntersectionPolyDataFilter.h>

#include <vtkXMLPolyDataWriter.h>

typedef itk::Image<float, 3> FloatImageType;
typedef itk::ImageFileReader<FloatImageType> ReaderType; // 图像读取类
// typedef itk::ImageToVTKImageFilter<FloatImageType> ConnectorType;  //VTK和ITK链接器
typedef itk::BinaryThresholdImageFilter<FloatImageType, FloatImageType> ThresholdType;
typedef itk::BinaryThresholdImageFilter<FloatImageType, FloatImageType> ThresholdType;
typedef itk::VTKImageExport<FloatImageType> ITKToVTKExportFilterType;
// 阈值分割，Threshold为给定阈值
FloatImageType::Pointer Seg3DImage(FloatImageType::Pointer inputImage, float Threshold);
template <typename ITK_Exporter, typename VTK_Importer>
void ConnectPipelines(ITK_Exporter exporter, VTK_Importer *importer);

// 将ITK数据转成VTK数据
vtkImageData *TransformITKToVTK(FloatImageType::Pointer inputImage);
vtkPolyData *GetSurface(vtkImageData *inputData, float isoValue);
// 直接把ITK的分割结果转成polydata，并挪到ITK坐标空间
vtkPolyData *GetSegSurface(FloatImageType::Pointer inputImage);
FloatImageType::Pointer FloatRead3DImage(std::string filename);
// 显示分割表面
void ShowSegSurface(vtkPolyData *inputData, float *color);

vtkSmartPointer<vtkSmoothPolyDataFilter> smoothFilter = vtkSmartPointer<vtkSmoothPolyDataFilter>::New(); // 重构图像全局存放
vtkSmartPointer<vtkImageGaussianSmooth> gaussianSmoothFilter = vtkSmartPointer<vtkImageGaussianSmooth>::New();

int main(int, char *[])
{

	ReaderType::Pointer reader = ReaderType::New();

	// reader->SetFileName("G:\\vessel_complete\\data\\new\\DS\\09.mhd");
	reader->SetFileName("G:\\vessel_complete\\fanxiu\\Centerline\\19.mhd");
	reader->Update();

	FloatImageType::Pointer SegImage = Seg3DImage(reader->GetOutput(), 0.5);
	vtkPolyData *segSurface = GetSegSurface(SegImage);

	float a = 1;

	// 定义颜色
	float red_color[3] = {1, 0, 0};
	float green_color[3] = {0, 1, 0};
	float blue_color[3] = {0, 0, 1};
	float yellow_color[3] = {1, 1, 0};
	float white_color[3] = {1, 1, 1};
	float orange_color[3] = {250, 128, 10};
	float self_color[3] = {0.74, 0.06, 0.06}; // 0.74,0.06,0.06

	ShowSegSurface(segSurface, self_color);

	return 0;
}

// 阈值分割，Threshold为给定阈值
FloatImageType::Pointer Seg3DImage(FloatImageType::Pointer inputImage, float Threshold)
{
	ThresholdType::Pointer thresholder = ThresholdType::New();
	thresholder->SetInput(inputImage);
	thresholder->SetOutsideValue(0);
	thresholder->SetInsideValue(255);
	thresholder->SetLowerThreshold(Threshold);
	thresholder->SetUpperThreshold(40000);
	thresholder->Update();
	return thresholder->GetOutput();
}

template <typename ITK_Exporter, typename VTK_Importer>
void ConnectPipelines(ITK_Exporter exporter, VTK_Importer *importer)
{
	importer->SetUpdateInformationCallback(exporter->GetUpdateInformationCallback());
	importer->SetPipelineModifiedCallback(exporter->GetPipelineModifiedCallback());
	importer->SetWholeExtentCallback(exporter->GetWholeExtentCallback());
	importer->SetSpacingCallback(exporter->GetSpacingCallback());
	importer->SetOriginCallback(exporter->GetOriginCallback());
	importer->SetScalarTypeCallback(exporter->GetScalarTypeCallback());
	importer->SetNumberOfComponentsCallback(exporter->GetNumberOfComponentsCallback());
	importer->SetPropagateUpdateExtentCallback(exporter->GetPropagateUpdateExtentCallback());
	importer->SetUpdateDataCallback(exporter->GetUpdateDataCallback());
	importer->SetDataExtentCallback(exporter->GetDataExtentCallback());
	importer->SetBufferPointerCallback(exporter->GetBufferPointerCallback());
	importer->SetCallbackUserData(exporter->GetCallbackUserData());
}

// 将ITK数据转成VTK数据
vtkImageData *TransformITKToVTK(FloatImageType::Pointer inputImage)
{
	ITKToVTKExportFilterType::Pointer itkExporter = ITKToVTKExportFilterType::New();
	itkExporter->SetInput(inputImage);

	vtkImageImport *vtkImporter = vtkImageImport::New();
	ConnectPipelines(itkExporter, vtkImporter);
	vtkImporter->Update();
	return vtkImporter->GetOutput();
}

vtkPolyData *GetSurface(vtkImageData *inputData, float isoValue)
{
	vtkMarchingCubes *VesselExtractor = vtkMarchingCubes::New();
	VesselExtractor->SetInputData(inputData);
	VesselExtractor->SetNumberOfContours(1);
	VesselExtractor->SetValue(0, isoValue);
	VesselExtractor->Update();

	// 平滑处理
	// vtkSmartPointer<vtkSmoothPolyDataFilter>smoothFilter = vtkSmartPointer<vtkSmoothPolyDataFilter>::New();
	smoothFilter->SetInputConnection(VesselExtractor->GetOutputPort());
	smoothFilter->SetNumberOfIterations(200);
	smoothFilter->Update();

	return smoothFilter->GetOutput();
}

// 直接把ITK的分割结果转成polydata，并挪到ITK坐标空间
vtkPolyData *GetSegSurface(FloatImageType::Pointer inputImage)
{
	vtkImageData *SegData = TransformITKToVTK(inputImage);
	vtkPolyData *SegSurface = GetSurface(SegData, 0.5);
	return SegSurface;
}

FloatImageType::Pointer FloatRead3DImage(std::string filename)
{
	ReaderType::Pointer reader = ReaderType::New();
	reader->SetFileName(filename);
	reader->Update();
	return reader->GetOutput();
}

// 显示单一分割表面
void ShowSegSurface(vtkPolyData *inputData, float *color)
{
	vtkPolyDataMapper *VesselMapper = vtkPolyDataMapper::New();
	VesselMapper->SetInputData(inputData);
	VesselMapper->ScalarVisibilityOff();

	vtkActor *vesselActor = vtkActor::New();
	vesselActor->GetProperty()->SetColor(color[0], color[1], color[2]);
	//    vesselActor->GetProperty()->SetDiffuseColor(0.1, 0.94, 0.52);
	//    vesselActor->GetProperty()->SetSpecular(0.3);
	//    vesselActor->GetProperty()->SetSpecularPower(20);
	vesselActor->SetMapper(VesselMapper);
	vesselActor->GetProperty()->SetInterpolationToGouraud();
	vesselActor->GetProperty()->SetOpacity(1);
	vtkRenderer *ren = vtkRenderer::New();
	ren->AddActor(vesselActor);
	ren->SetBackground(1, 1, 1);

	// vtkCamera* aCamera = vtkCamera::New();
	// aCamera->SetViewUp(0,0,1);
	// aCamera->SetPosition(1100,0,0);
	// aCamera->SetFocalPoint(1.5,0,0);
	// ren->SetActiveCamera(aCamera);

	vtkRenderWindow *renWin = vtkRenderWindow::New();
	renWin->SetSize(800, 800);
	// renWin->BordersOff();

	renWin->AddRenderer(ren);

	vtkSmartPointer<vtkRenderWindowInteractor> iren = vtkSmartPointer<vtkRenderWindowInteractor>::New();
	iren->SetRenderWindow(renWin); // 交互

	// vtkRenderWindowInteractor *iren = vtkRenderWindowInteractor::New();
	// iren->SetRenderWindow(renWin);
	vtkInteractorStyleTrackballCamera *style = vtkInteractorStyleTrackballCamera::New();
	iren->SetInteractorStyle(style);

	iren->Initialize();
	iren->Start();

	VesselMapper->Delete();
	vesselActor->Delete();
	ren->Delete();
	renWin->Delete();
	iren->Delete();
}
