from pilot_scene_base import *


class Section3Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("03:06 UTC / RADAR RECONSTRUCTION", [], number=3)
        globe = ice_sphere()
        orbit = Circle(radius=2.85, color=DIM, stroke_width=1).rotate(48*DEGREES,axis=RIGHT)
        probe = spacecraft().move_to(orbit.point_from_proportion(.1))
        self.play(FadeIn(globe),Create(orbit),FadeIn(probe),run_time=2)
        self.play(MoveAlongPath(probe,orbit),run_time=9,rate_func=linear)
        cutaway = ice_sphere(cutaway=True)
        self.play(FadeOut(globe),FadeIn(cutaway),run_time=1.4)
        cavity = Sphere(radius=.66,resolution=(14,10),fill_color="#070B13",fill_opacity=1,
                        stroke_color=ALARM,stroke_width=.6,checkerboard_colors=False).shift(DOWN*.4+OUT*.3)
        rings = VGroup(*[Circle(radius=.68,color=ALARM,stroke_width=1.3).rotate(a,axis=RIGHT).move_to(cavity)
                        for a in (0,PI/2)])
        self.play(FadeIn(cavity),Create(rings),run_time=1.6)
        self.screen_label("SUBSURFACE RETURN  /  GEOMETRY: SPHERICAL",[3.05,-2.25,0],ALARM,17)
        self.move_camera(theta=-68*DEGREES,run_time=5)
        self.play(cavity.animate.shift(RIGHT*.2),rings.animate.shift(RIGHT*.2),run_time=2)
        self.finish_slot()
