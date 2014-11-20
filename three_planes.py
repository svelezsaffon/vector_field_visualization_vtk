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


        self.plane1=None
        for i in range(0,3):
            if i==0:
                x=32.30   ##46.14
            if i==1:
                x=113.86
            if i==2:
                x=216.94  ##213.86

            plane_mapper=self.create_cut_acto_plane(x)
            ren.AddActor(self.create_glyph(plane_mapper))




        #Add renderer to renderwindow and render
        self.renWin = vtk.vtkRenderWindow()
        self.renWin.AddRenderer(ren)
        self.renWin.SetSize(1920, 1080)

        iren = vtk.vtkRenderWindowInteractor()
        iren.SetRenderWindow(self.renWin)

        iren.AddObserver('RightButtonPressEvent', self.capture_image, 1.0)

        """
        #Slider 1
        sliderRep1=vtk.vtkSliderWidget()
        sliderRep1.SetInteractor(iren)
        sliderRep1.SetRepresentation(self.create_color_slider("X-Position",0.02,0.15,0,220))
        sliderRep1.SetEnabled(True)
        sliderRep1.AddObserver("InteractionEvent", self.change_iso)
        """


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
        self.renWin.Render()
        iren.Start()

    def change_iso(self,obj,event):

      self.plane1.SetOrigin(obj.GetSliderRepresentation().GetValue(),0,0)


    def create_color_slider(self,name,left,right,down,up,default_value=0.02):

        slider=vtk.vtkSliderRepresentation2D()
        slider.SetMinimumValue(down)
        slider.SetMaximumValue(up)
        slider.SetValue(default_value)
        slider.SetTitleText(name)
        slider.SetLabelFormat("%5.2f")

        slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        slider.GetPoint1Coordinate().SetValue(left, 0.1)

        slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        slider.GetPoint2Coordinate().SetValue(right, 0.1)

        return slider

    def update_look_up_table(self):

        self.arrowColor.AddRGBPoint(0, 1.0, 0.0, 0.0)

        self.arrowColor.AddRGBPoint(60, 0.0, 1.0, 0.0)

        self.arrowColor.AddRGBPoint(120, 0.0, 0.0, 1.0)

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

        if xpos>170 and xpos <220:
            self.plane1=plane

        return probe_filter

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