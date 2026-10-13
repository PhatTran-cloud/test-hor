from math_scene_base import *


class Section4Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("WHY LATITUDE LINES FOOL US", [],phi=68*DEGREES,theta=-48*DEGREES,number=4)
        sphere=sphere_grid(); eq=Circle(radius=2.2,color=CYAN,stroke_width=4).rotate(90*DEGREES,axis=RIGHT)
        lat=Circle(radius=1.65,color=ALARM,stroke_width=4).rotate(90*DEGREES,axis=RIGHT).shift(OUT*1.45)
        e1=eq.point_from_proportion(.1); e2=eq.point_from_proportion(.65)
        l1=lat.point_from_proportion(.1); l2=lat.point_from_proportion(.65)
        epath=Line3D(e1,e2,color=CYAN,thickness=.025); lpath=ArcBetweenPoints(l1,l2,angle=PI*.55,color=ALARM,stroke_width=4)
        self.play(FadeIn(sphere),run_time=1.2)
        self.play(Create(eq),Create(lat),run_time=2)
        self.screen_label("EQUATOR  /  GREAT CIRCLE",[-3.4,2.35,0],CYAN,18)
        self.screen_label("LATITUDE  /  SMALL CIRCLE",[3.0,2.35,0],ALARM,18)
        self.play(Create(epath),Create(lpath),run_time=3)
        self.play(Indicate(lat,color=ALARM),run_time=1)
        self.move_camera(theta=-70*DEGREES,run_time=5)
        self.finish_slot()
