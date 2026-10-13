from pilot_scene_base import *


class Section5Scene(TeachingScene):
    def construct(self):
        self.setup_layout("04:40 UTC / TRANSMISSION LOG", [],number=5)
        divider=Line(LEFT*5.5,RIGHT*5.5,color=DIM,stroke_width=1).shift(DOWN*.05)
        tx=Text("TRANSMIT QUEUE",font="Courier New",font_size=20,color=CYAN).move_to([-3.75,2.05,0])
        rx=Text("RECEIVE BUFFER",font="Courier New",font_size=20,color=DIM).move_to([-3.75,-.6,0])
        self.play(Create(divider),Write(tx),Write(rx),run_time=2)
        question=Text("WHO ARE YOU?",font="Courier New",font_size=42,color=ICE).move_to([0,1.15,0])
        scheduled=Text("SCHEDULED 04:40:10",font="Courier New",font_size=20,color=CYAN).move_to([3.9,2.05,0])
        self.play(Write(question),Write(scheduled),run_time=3)
        self.wait(3)
        echo=Text("WHO ARE YOU?",font="Courier New",font_size=42,color=ALARM).move_to([0,-1.55,0])
        received=Text("RECEIVED 04:40:00",font="Courier New",font_size=20,color=ALARM).move_to([3.9,-.6,0])
        self.play(Write(echo),FadeIn(received),run_time=1.3)
        self.wait(1)
        waveform=wave_shape(width=9,y=-2.15,color=ALARM,amplitude=.25)
        self.play(Create(waveform),run_time=3)
        verdict=Text("10 SECONDS BEFORE TRANSMISSION",font="Courier New",font_size=23,color=ALARM).shift(DOWN*.05)
        self.play(FadeOut(divider),Write(verdict),run_time=1.5)
        self.wait(3)
        self.play(echo.animate.set_color(WHITE),run_time=.7)
        self.finish_slot()
