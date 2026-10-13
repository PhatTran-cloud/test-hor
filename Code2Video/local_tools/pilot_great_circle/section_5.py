from math_scene_base import *


class Section5Scene(TeachingScene):
    def construct(self):
        self.setup_layout("THE MAP IS THE DISTORTION", [],number=5)
        globe=Circle(radius=1.7,color=ICE,fill_color="#163342",fill_opacity=1).shift(LEFT*3.5+DOWN*.1)
        mapbox=Rectangle(width=6.1,height=3.4,color=ICE,fill_color="#0E1A26",fill_opacity=1).shift(RIGHT*2.3+DOWN*.1)
        globe_lines=VGroup(*[Arc(radius=1.7, start_angle=a, angle=PI, color=DIM,stroke_width=1).move_to(globe) for a in np.linspace(-PI/2,PI/2,5)])
        p1=Dot(globe.get_center()+LEFT*.8+UP*.7,color=CYAN); p2=Dot(globe.get_center()+RIGHT*.9+DOWN*.5,color=CYAN)
        mp1=Dot(mapbox.get_center()+LEFT*2.2+UP*.6,color=CYAN); mp2=Dot(mapbox.get_center()+RIGHT*2.1+DOWN*.65,color=CYAN)
        curved=ParametricFunction(lambda t: np.array([2.3+4.0*t, .0+.8*np.sin(PI*t),0]),t_range=[0,1],color=ALARM,stroke_width=4).shift(RIGHT*0+DOWN*.1)
        straight=Line(mp1,mp2,color=YELLOW,stroke_width=3)
        ant=ant_2d(.4,ALARM).move_to(mp1)
        self.play(FadeIn(globe),Create(globe_lines),FadeIn(mapbox),run_time=1.5)
        self.play(FadeIn(p1),FadeIn(p2),FadeIn(mp1),FadeIn(mp2),run_time=1)
        self.play(Create(straight),run_time=1)
        self.play(Create(curved),run_time=2)
        map_label = Text("STRAIGHT ON MAP", font="Courier New", font_size=18, color=YELLOW).move_to([3.1,-2.25,0])
        globe_label = Text("GREAT-CIRCLE PATH", font="Courier New", font_size=18, color=ALARM).move_to([0,-2.25,0])
        self.play(FadeIn(map_label), FadeIn(globe_label), run_time=.5)
        self.play(MoveAlongPath(ant,curved),run_time=4)
        self.play(Indicate(curved,color=ALARM),run_time=1)
        self.finish_slot()
