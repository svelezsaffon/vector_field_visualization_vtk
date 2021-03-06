__author__ = 'santiago'



import Tkinter as tk
import vtk
import sys

class ImageModification(object):

    def __init__(self,delta,wing):


        self.print_counter=6
        ren = vtk.vtkRenderer()

        self.geo_reader = vtk.vtkUnstructuredGridReader()
        self.geo_reader.SetFileName(wing)


        self.vec_reader = vtk.vtkStructuredPointsReader()
        self.vec_reader.SetFileName(delta)


        geo_Mapper=vtk.vtkDataSetMapper()
        geo_Mapper.SetInputConnection(self.geo_reader.GetOutputPort())

        #glyph actor
        geo_actor = vtk.vtkActor()
        geo_actor.SetMapper(geo_Mapper)

        ren.AddActor(geo_actor)

        self.arrowColor = vtk.vtkColorTransferFunction()

        self.update_look_up_table()


        ren.AddActor(self.create_stream_line(110,-50,0,10))
        ren.AddActor(self.create_stream_line(110,50,0,20))
        ren.AddActor(self.create_stream_line(0,0,10,10,5))





        #Add renderer to renderwindow and render
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(ren)
        self.renWin.SetSize(1920, 1080)

        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(self.renWin)

        iren.AddObserver('RightButtonPressEvent', self.capture_image, 1.0)



        # Scalar Bar actor
        scalar_bar = vtk.vtkScalarBarActor()
        scalar_bar.SetOrientationToHorizontal()
        scalar_bar.SetLookupTable(self.arrowColor)
        scalar_bar.SetTitle("Color map")
        scalar_bar.SetLabelFormat("%5.2f")
        scalar_bar.SetMaximumHeightInPixels(300)
        scalar_bar.SetMaximumWidthInPixels(60)

        # Scalar Bar Widget
        scalar_bar_widget = vtk.vtkScalarBarWidget()
        scalar_bar_widget.SetInteractor(iren)
        scalar_bar_widget.SetScalarBarActor(scalar_bar)
        scalar_bar_widget.On()

        ren.SetBackground(0,0,0)
        self.renWin.Render()
        iren.Start()

    def update_look_up_table(self):

        self.arrowColor.AddRGBPoint(0, 1.0, 0.0, 0.0)

        self.arrowColor.AddRGBPoint(90, 0.0, 1.0, 0.0)

        self.arrowColor.AddRGBPoint(120, 0.0, 0.0, 1.0)


    def create_stream_line(self,y1,y2,y3,n,r=10,tr=2):

        seeds = vtk.vtkPointSource()
        seeds.SetNumberOfPoints(n)
        seeds.SetCenter(y1, y2, y3)
        seeds.SetRadius(r)
        seeds.SetDistributionToShell()


        integ = vtk.vtkRungeKutta4()
        streamline = vtk.vtkStreamLine()
        streamline.SetInputConnection(self.vec_reader.GetOutputPort())
        streamline.SetSourceConnection(seeds.GetOutputPort())
        streamline.SetMaximumPropagationTime(220)
        streamline.SetIntegrationStepLength(0.05)
        streamline.SetStepLength(0.5)
        streamline.SpeedScalarsOn()
        streamline.SetNumberOfThreads(1)
        streamline.SetIntegrationDirectionToIntegrateBothDirections()
        streamline.SetIntegrator(integ)
        streamline.SetSpeedScalars(220);


        streamline_mapper = vtk.vtkPolyDataMapper()
        streamline_mapper.SetInputConnection(streamline.GetOutputPort())


        streamTube = vtk.vtkTubeFilter()
        streamTube.SetInputConnection(streamline.GetOutputPort())
        streamTube.SetRadius(tr)
        streamTube.SetNumberOfSides(12)
        streamTube.SetVaryRadiusToVaryRadiusByVector()
        mapStreamTube = vtk.vtkPolyDataMapper()
        mapStreamTube.SetInputConnection(streamTube.GetOutputPort())
        mapStreamTube.SetLookupTable(self.arrowColor)

        streamTubeActor = vtk.vtkActor()
        streamTubeActor.SetMapper(mapStreamTube)
        streamTubeActor.GetProperty().BackfaceCullingOn()

        return streamTubeActor



    def capture_image(self,obj,eve):
        self.renWin.Render()
        self.w2i = vtk.vtkWindowToImageFilter()
        self.w2i.SetInput(self.renWin)
        self.writer = vtk.vtkJPEGWriter()
        self.writer.SetInputConnection(self.w2i.GetOutputPort())
        self.writer.SetFileName(`self.print_counter` + "vectorscreen.jpg");
        self.print_counter =1 + self.print_counter
        self.writer.Write()



if __name__ == '__main__':
    delta =sys.argv[0:][1]
    wing  =sys.argv[0:][2]

    ImageModification(delta,wing)