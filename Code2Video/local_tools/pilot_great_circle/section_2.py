from math_scene_base import *


class Section2Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("STRAIGHT THROUGH OR CURVED AROUND", [],phi=67*DEGREES,theta=-43*DEGREES,number=2)
        sphere=sphere_grid(); a=point_on_sphere(2.2,.35,2.8); b=point_on_sphere(2.2,-.25,.25)
        A=Dot3D(a,color=CYAN,radius=.1); B=Dot3D(b,color=CYAN,radius=.1)
        chord=Line3D(a,b,color=ALARM,thickness=.035)
        arcpts=great_circle_points(a/2.2,b/2.2,80); arc=path_3d(arcpts,color=CYAN,width=4)
        ant=ant_2d(.36,ALARM).rotate(90*DEGREES,axis=RIGHT).move_to(a)
        self.play(FadeIn(sphere),FadeIn(A),FadeIn(B),run_time=1.5)
        self.play(Create(chord),run_time=2)
        self.screen_label("SHORTER IN 3D  /  NOT ALLOWED",[0,-2.45,0],ALARM,20)
        self.wait(2)
        self.play(Create(arc),FadeIn(ant),run_time=2.5)
        self.screen_label("THE ANT MUST STAY ON THE SURFACE",[0,2.55,0],CYAN,19)
        self.play(MoveAlongPath(ant,arc),run_time=7,rate_func=linear)
        self.move_camera(theta=-63*DEGREES,run_time=4)
        self.finish_slot()
