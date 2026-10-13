from pilot_scene_base import *


class Section4Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("03:52 UTC / TRACKING FAILURE", [],theta=-68*DEGREES,number=4)
        shell = ice_sphere(cutaway=True)
        shadow = Sphere(radius=.6,resolution=(14,10),fill_color="#03050A",fill_opacity=1,
                        stroke_color=ALARM,stroke_width=.5,checkerboard_colors=False).shift(DOWN*.45+OUT*.3)
        cage = VGroup(Circle(radius=.62,color=ALARM,stroke_width=1.2),
                      Circle(radius=.62,color=ALARM,stroke_width=1.2).rotate(PI/2,axis=RIGHT)).move_to(shadow)
        probe = spacecraft().move_to([1.1,-2.7,1])
        self.add(shell,shadow,cage,probe)
        self.screen_label("MASS: NO RETURN   /   HEAT: NO RETURN",[0,2.6,0],DIM,20)
        tether = always_redraw(lambda: DashedLine(shadow.get_center(),probe.get_center(),color=ALARM,dash_length=.07,stroke_width=1.3))
        self.play(Create(tether),run_time=1.5)
        self.wait(3.5)
        # Fictional sensor echo, not a mechanics simulation.
        self.play(probe.animate.shift(LEFT*1.9),shadow.animate.shift(LEFT*1.3),cage.animate.shift(LEFT*1.3),run_time=8)
        self.wait(2)
        self.play(probe.animate.shift(RIGHT*1.35),shadow.animate.shift(RIGHT*1.35),cage.animate.shift(RIGHT*1.35),run_time=4)
        self.move_camera(theta=-82*DEGREES,run_time=3.5)
        self.screen_label("IT IS FOLLOWING THE PROBE",[3.0,-2.25,0],ALARM,19)
        self.finish_slot()
