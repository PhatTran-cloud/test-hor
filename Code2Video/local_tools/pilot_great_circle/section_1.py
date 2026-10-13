from math_scene_base import *


class Section1Scene(TeachingScene):
    def construct(self):
        self.setup_layout("A QUESTION ABOUT THE SHORTEST WALK", [], number=1)
        left_center = LEFT*3.25 + DOWN*.15
        right_center = RIGHT*3.25 + DOWN*.15
        left = Rectangle(width=5.35, height=3.45, color=DIM, fill_color="#0E1A26", fill_opacity=1).move_to(left_center)
        right = Circle(radius=1.7, color=ICE, fill_color="#163342", fill_opacity=.8).move_to(right_center)
        # Supporting objects make the two models read as separate teaching panels.
        grid = VGroup(*[
            Line(left.get_left()+RIGHT*(i*.67+.55)+UP*.05, left.get_left()+RIGHT*(i*.67+.55)+DOWN*3.0,
                 color="#28414F", stroke_width=1, stroke_opacity=.55)
            for i in range(7)
        ], *[
            Line(left.get_left()+RIGHT*.2+UP*(1.05-i*.55), left.get_right()+LEFT*.2+UP*(1.05-i*.55),
                 color="#28414F", stroke_width=1, stroke_opacity=.55)
            for i in range(5)
        ])
        sheet_tag = Text("FLAT SHEET",font="Courier New",font_size=19,color=CYAN).move_to(left_center+UP*1.25)
        sphere_tag = Text("SPHERE",font="Courier New",font_size=19,color=CYAN).move_to(right_center+UP*2.05)
        ruler = VGroup(Line(ORIGIN, RIGHT*1.15, color=YELLOW, stroke_width=2),
                       *[Line(RIGHT*x+UP*.08, RIGHT*x+DOWN*.08, color=YELLOW, stroke_width=1)
                         for x in np.linspace(0,1.15,6)]).move_to(left_center+DOWN*1.25)
        a = Dot(left_center+LEFT*1.75+UP*.55, color=CYAN); b = Dot(left_center+RIGHT*1.55+DOWN*.7,color=CYAN)
        a_label = Text("A",font="Arial",font_size=18,color=ICE).next_to(a,UL,buff=.08)
        b_label = Text("B",font="Arial",font_size=18,color=ICE).next_to(b,DR,buff=.08)
        line = Line(a,b,color=ALARM,stroke_width=4)
        ant = ant_2d(.42).move_to(a)
        self.play(FadeIn(left), FadeIn(grid), FadeIn(sheet_tag), FadeIn(ruler), run_time=1.3)
        self.play(FadeIn(a), FadeIn(b), FadeIn(a_label), FadeIn(b_label), Create(line), run_time=1.4)
        self.play(FadeIn(ant), MoveAlongPath(ant,line), run_time=2.8)
        self.play(FadeIn(right), FadeIn(sphere_tag), run_time=1)
        latitudes = VGroup(Ellipse(width=2.9,height=.85,color=DIM,stroke_width=1.2).move_to(right_center+UP*.2),
                           Ellipse(width=2.4,height=.55,color=DIM,stroke_width=1.2).move_to(right_center+DOWN*.55))
        ra=Dot(right_center+LEFT*.95+UP*.35,color=CYAN); rb=Dot(right_center+RIGHT*.9+DOWN*.4,color=CYAN)
        ra_label = Text("A",font="Arial",font_size=18,color=ICE).next_to(ra,UL,buff=.08)
        rb_label = Text("B",font="Arial",font_size=18,color=ICE).next_to(rb,DR,buff=.08)
        self.play(Create(latitudes), FadeIn(ra), FadeIn(rb), FadeIn(ra_label), FadeIn(rb_label), run_time=1.4)
        question=Text("WHAT COUNTS AS STRAIGHT?",font="Arial",font_size=27,color=ICE).move_to(DOWN*3.05)
        self.play(Write(question),run_time=1.8)
        self.wait(3)
        self.finish_slot()
