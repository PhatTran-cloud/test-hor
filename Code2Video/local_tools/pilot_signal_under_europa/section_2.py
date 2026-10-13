from pilot_scene_base import *


class Section2Scene(TeachingScene):
    def construct(self):
        self.setup_layout("02:47 UTC / THE COORDINATE", [], number=2)
        grid = NumberPlane(x_range=[-6,6,1], y_range=[-3,3,1], x_length=12, y_length=6,
                           axis_config={"stroke_opacity":0},
                           background_line_style={"stroke_color":DIM,"stroke_opacity":.28,"stroke_width":1})
        self.add(grid)
        top = VMobject(color=ICE, stroke_width=2).set_points_smoothly([[-5.5,.9,0],[-3.5,.7,0],[-1.5,1.05,0],[.5,.85,0],[3,.98,0],[5.5,.8,0]])
        sub = top.copy().shift(DOWN*.18).set_color(DIM)
        coordinate = Text("43.2 N  /  12.7 W", font="Courier New", font_size=27, color=CYAN).shift(UP*2.25)
        self.play(Create(top), Create(sub), Write(coordinate), run_time=2)
        target = Circle(radius=.15, color=CYAN, stroke_width=2).move_to([0,.86,0])
        cross = VGroup(Line(LEFT*.3,RIGHT*.3,color=CYAN),Line(DOWN*.3,UP*.3,color=CYAN)).move_to(target)
        self.play(Create(target), Create(cross), run_time=1)
        self.wait(3)
        self.play(target.animate.shift(DOWN*2.05).set_color(ALARM), cross.animate.shift(DOWN*2.05).set_color(ALARM), run_time=5)
        depth = DashedLine([0,.86,0],[0,-1.19,0], color=ALARM, dash_length=.09)
        depth_label = Text("800 m",font="Arial",font_size=33,color=ALARM).next_to(depth,RIGHT,buff=.35)
        self.play(Create(depth), FadeIn(depth_label), run_time=1)
        search = Text("TRANSMITTER RECORDS: 0",font="Courier New",font_size=23,color=DIM).move_to(RIGHT*2.8+DOWN*1.8)
        self.play(Write(search),run_time=2)
        self.wait(3)
        invitation = Text("THIS LOCATION DOES NOT EXIST IN THE LOG",font="Courier New",font_size=18,color=ALARM).move_to(search)
        self.play(Transform(search,invitation),target.animate.scale(1.6),run_time=1.5)
        self.finish_slot()
