from math_scene_base import *


class Section3Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("THE GREAT CIRCLE", [],phi=66*DEGREES,theta=-45*DEGREES,number=3)
        sphere=sphere_grid(); a=point_on_sphere(2.2,.55,2.7); b=point_on_sphere(2.2,-.3,.25)
        A=Dot3D(a,color=CYAN,radius=.1); B=Dot3D(b,color=CYAN,radius=.1); center=Dot3D(ORIGIN,color=YELLOW,radius=.1)
        plane=Surface(lambda u,v: np.array([u,v,0]),u_range=[-2.6,2.6],v_range=[-2.6,2.6],resolution=(2,2),fill_color=YELLOW,fill_opacity=.10,stroke_color=YELLOW,stroke_width=.6)
        plane.rotate(38*DEGREES,axis=UP).rotate(20*DEGREES,axis=RIGHT)
        arc=path_3d(great_circle_points(a/2.2,b/2.2),color=CYAN,width=5)
        ant=ant_2d(.35,ALARM).move_to(a)
        self.play(FadeIn(sphere),FadeIn(A),FadeIn(B),FadeIn(center),run_time=1.5)
        self.play(FadeIn(plane),run_time=2)
        self.play(Create(arc),run_time=2)
        self.screen_label("A, CENTER, B  →  ONE PLANE",[0,2.5,0],YELLOW,20)
        self.play(MoveAlongPath(ant,arc),run_time=6,rate_func=linear)
        self.move_camera(theta=-70*DEGREES,run_time=4)
        self.screen_label("GEODESIC = STRAIGHTEST ALLOWED PATH",[0,-2.45,0],CYAN,19)
        self.finish_slot()
