__author__ = 'santiago'



import Tkinter as tk
import vtk
import sys

class ImageModification(object):

    def __init__(self,delta,wing):


        self.print_counter=0
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



        for i in range(0,3):
            x=25
            if i==1:
                x=110
            if i==2:
                x=225

            plane_mapper=self.create_cut_acto_plane(x)
            ren.AddActor(self.create_glyph(plane_mapper))




        #Add renderer to renderwindow and render
        renWin = vtk.vtkRenderWindow()
        renWin.AddRenderer(ren)
        renWin.SetSize(1920, 1080)

        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(renWin)

        iren.AddObserver('RightButtonPressEvent', self.capture_image, 1.0)



        # Scalar Bar actor
        scalar_bar = vtk.vtkScalarBarActor()
        scalar_bar.SetOrientationToHorizontal()
        scalar_bar.SetLookupTable(self.arrowColor)
        scalar_bar.SetTitle("Color map")
        scalar_bar.SetLabelFormat("%5.2f")
        scalar_bar.SetMaximumHeightInPixels(300)
        scalar_bar.SetMaximumWidthInPixels(100)

        # Scalar Bar Widget
        scalar_bar_widget = vtk.vtkScalarBarWidget()
        scalar_bar_widget.SetInteractor(iren)
        scalar_bar_widget.SetScalarBarActor(scalar_bar)
        scalar_bar_widget.On()




        ren.SetBackground(0,0,0)
        renWin.Render()
        iren.Start()

    def update_look_up_table(self):

        self.arrowColor.AddRGBPoint(0, 1.0, 0.0, 0.0)

        self.arrowColor.AddRGBPoint(110, 0.0, 1.0, 0.0)

        self.arrowColor.AddRGBPoint(220, 0.0, 0.0, 1.0)

    def create_glyph(self,plane_mapper):
        #in here we do the arrows
        arrows = vtk.vtkArrowSource()


        ptMask = vtk.vtkMaskPoints()
        ptMask.SetInputConnection(plane_mapper.GetOutputPort())
        ptMask.SetOnRatio(10)
        ptMask.RandomModeOn()

        #in here we do the glyohs
        glyph = vtk.vtkGlyph3D()
        glyph.SetSourceConnection(arrows.GetOutputPort())
        glyph.SetInputConnection(ptMask.GetOutputPort())
        glyph.SetColorModeToColorByVector()
        glyph.SetScaleFactor(20)


        #Glyph mapper
        gly_mapper = vtk.vtkPolyDataMapper()
        gly_mapper.SetInputConnection(glyph.GetOutputPort())
        gly_mapper.SetLookupTable(self.arrowColor)


        #glyph actor
        gly_actor = vtk.vtkActor()
        gly_actor.SetMapper(gly_mapper)

        return gly_actor

    def create_cut_acto_plane(self,xpos):
        #vtk plane
        plane=vtk.vtkPlane()
        plane.SetOrigin(xpos,0,0)
        plane.SetNormal(1,0,0)

        #create cutter
        cutter=vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputConnection(self.vec_reader.GetOutputPort())
        cutter.Update()


        #probe filter for the cutting plane
        probe_filter=vtk.vtkProbeFilter()
        probe_filter.SetInputConnection(cutter.GetOutputPort())
        probe_filter.SetSourceConnection(self.vec_reader.GetOutputPort())


        return probe_filter

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