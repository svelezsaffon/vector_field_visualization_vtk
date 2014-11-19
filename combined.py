__author__ = 'santiago'



import Tkinter as tk
import vtk
import sys

class ImageModification(object):

    def __init__(self,delta,wing,vorticity):


        self.print_counter=11
        self.ren = vtk.vtkRenderer()

        self.geo_reader = vtk.vtkUnstructuredGridReader()
        self.geo_reader.SetFileName(wing)


        self.vec_reader = vtk.vtkStructuredPointsReader()
        self.vec_reader.SetFileName(delta)


        self.vort_reader=vtk.vtkStructuredPointsReader()
        self.vort_reader.SetFileName(vorticity)


        geo_Mapper=vtk.vtkDataSetMapper()
        geo_Mapper.SetInputConnection(self.geo_reader.GetOutputPort())

        #glyph actor
        geo_actor = vtk.vtkActor()
        geo_actor.SetMapper(geo_Mapper)

        self.ren.AddActor(geo_actor)

        self.arrowColor = vtk.vtkColorTransferFunction()

        self.update_look_up_table()

        self.ren.AddActor(self.create_stream_line(110,-50,0,50))
        self.ren.AddActor(self.create_stream_line(110,50,0,50))
        self.ren.AddActor(self.create_stream_line(0,20,0,50))
        self.ren.AddActor(self.create_stream_line(0,-20,0,50))


        self.load_isosurface()


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

        self.arrowColor.AddRGBPoint(0, 0.0, 1.0, 0.0)

        self.arrowColor.AddRGBPoint(110, 1.0, 0.0, 0.0)



        #self.arrowColor.AddRGBPoint(220, 0.0, 0.0, 1.0)

    def load_isosurface(self):

        isovalues=[100,700,1100,5810,7910,19000,32100,60000]

        colors=[
            [0.078431373,0.850980392,0.0],
            [0.298039216,0.850980392,0.482352941],
            [0.11372549,0.42745098,0.784313725],
            [0.137254902,0.235294118,0.784313725],
            [0.380392157,0.376470588,0.784313725],
            [0.419607843,0.239215686,0.784313725],
            [0.709803922,0.0,0.654901961],
            [1.0,1.0,1.0],
            [1.0,0.01,0.01]
        ]
        opacity=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8]

        apply=8

        for surfin in range(0,apply):



            """Applying the countor filter"""
            contourFilter = vtk.vtkContourFilter()
            contourFilter.SetInputConnection(self.vort_reader.GetOutputPort())

            contourFilter.SetValue(0, isovalues[surfin])

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(contourFilter.GetOutputPort())
            mapper.ScalarVisibilityOff()

            actor = vtk.vtkActor()

            actor.GetProperty().SetColor(colors[2][0],colors[2][1],colors[2][2])

            actor.SetMapper(mapper)

            actor.GetProperty().SetOpacity(opacity[surfin])

            self.ren.AddActor(actor)


    def create_stream_line(self,y1,y2,y3,n,r=10):

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

        streamlineMapper = vtk.vtkPolyDataMapper()
        streamlineMapper.SetInputConnection(streamline.GetOutputPort())
        streamlineMapper.SetLookupTable(self.arrowColor)


        streamline_actor = vtk.vtkActor()
        streamline_actor.SetMapper(streamlineMapper)
        streamline_actor.VisibilityOn()

        return streamline_actor



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
    vorticity=sys.argv[0:][2]
    wing  =sys.argv[0:][3]

    ImageModification(delta,wing,vorticity)