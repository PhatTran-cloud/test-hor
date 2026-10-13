from math_scene_base import *


class Section6Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("THE RULE IN ONE EQUATION", [],phi=68*DEGREES,theta=-50*DEGREES,number=6)
        sphere=sphere_grid(); a=point_on_sphere(2.2,.45,2.6); b=point_on_sphere(2.2,-.2,.25)
        arc=path_3d(great_circle_points(a/2.2,b/2.2),color=ALARM,width=5)
        ant=ant_2d(.35,ALARM).move_to(a)
        formula=MathTex(r"d = R\,\theta",font_size=54,color=YELLOW).to_edge(DOWN,buff=.55)
        radius=Line3D(ORIGIN,a,color=YELLOW,thickness=.025)
        theta_arc=Arc(radius=.55,start_angle=0,angle=.45,color=YELLOW,stroke_width=3)
        self.play(FadeIn(sphere),Create(radius),Create(arc),FadeIn(ant),run_time=2)
        self.play(Write(formula),run_time=2)
        self.play(MoveAlongPath(ant,arc),run_time=7,rate_func=linear)
        self.screen_label("ON THE SURFACE:  SHORTEST = GREAT-CIRCLE ARC",[0,2.5,0],CYAN,18)
        self.play(Indicate(formula,color=YELLOW),run_time=1)
        self.move_camera(theta=-75*DEGREES,run_time=4)
        self.wait(2)
        self.finish_slot()
