__author__ = 'santiago'



import Tkinter as tk
import vtk
import sys

class ImageModification(object):

    def __init__(self,delta,wing):

        self.arrowColor = vtk.vtkColorTransferFunction()

        self.update_look_up_table()

        self.print_counter=0
        self.ren = vtk.vtkRenderer()

        self.geo_reader = vtk.vtkUnstructuredGridReader()
        self.geo_reader.SetFileName(wing)


        self.vec_reader = vtk.vtkStructuredPointsReader()
        self.vec_reader.SetFileName(delta)

        """ This is for drawing the wing,"""
        geo_Mapper=vtk.vtkDataSetMapper()
        geo_Mapper.SetInputConnection(self.geo_reader.GetOutputPort())

        geo_actor = vtk.vtkActor()
        geo_actor.SetMapper(geo_Mapper)

        self.ren.AddActor(geo_actor)

        """End of adding the wing """


        self.ren.AddActor(self.create_stream_line(25,150,0,0.5))


        #Add renderer to renderwindow and render
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(self.ren)
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

        self.ren.SetBackground(0,0,0)
        self.renWin.Render()
        iren.Start()

    def update_look_up_table(self):

        self.arrowColor.AddRGBPoint(0, 1.0, 0.0, 0.0)

        self.arrowColor.AddRGBPoint(60, 0.0, 1.0, 0.0)

        self.arrowColor.AddRGBPoint(120, 0.0, 0.0, 1.0)




    def create_stream_line(self,x,y,z,opa):

        rake = vtk.vtkLineSource()
        rake.SetPoint1(x, -y, z)
        rake.SetPoint2(x, y, z)
        rake.SetResolution(150)

        """
        rake_mapper = vtk.vtkPolyDataMapper()
        rake_mapper.SetInputConnection(rake.GetOutputPort())
        rake_actor = vtk.vtkActor()
        rake_actor.SetMapper(rake_mapper)
        self.ren.AddActor(rake_actor)
        """

        integ = vtk.vtkRungeKutta4()
        streamline = vtk.vtkStreamLine()
        streamline.SetInputConnection(self.vec_reader.GetOutputPort())
        streamline.SetSourceConnection(rake.GetOutputPort())
        streamline.SetIntegrator(integ)
        streamline.SetMaximumPropagationTime(300)
        streamline.SetIntegrationStepLength(0.01)
        streamline.SetIntegrationDirectionToForward()
        streamline.SpeedScalarsOn()
        streamline.SetStepLength(0.05)

        scalarSurface = vtk.vtkRuledSurfaceFilter()
        scalarSurface.SetInputConnection(streamline.GetOutputPort())
        #scalarSurface.SetOffset(0)
        scalarSurface.SetOnRatio(1)
        scalarSurface.PassLinesOn()
        scalarSurface.SetRuledModeToPointWalk()
        scalarSurface.SetDistanceFactor(30)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(scalarSurface.GetOutputPort())
        #mapper.SetScalarRange(self.vec_reader.GetOutput().GetScalarRange())
        mapper.SetLookupTable(self.arrowColor)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opa)

        return actor



    def capture_image(self,obj,eve):
        self.renWin.Render()
        self.w2i = vtk.vtkWindowToImageFilter()
        self.w2i.SetInput(self.renWin)
        self.writer = vtk.vtkJPEGWriter()
        self.writer.SetInputConnection(self.w2i.GetOutputPort())
        self.writer.SetFileName(`self.print_counter` + "vrprintscreen.jpg");
        self.print_counter =1 + self.print_counter
        self.writer.Write()



if __name__ == '__main__':
    delta =sys.argv[0:][1]
    wing  =sys.argv[0:][2]

    ImageModification(delta,wing)