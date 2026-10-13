from pilot_scene_base import *


class Section1Scene(TeachingScene):
    def construct(self):
        self.setup_layout("02:13 UTC / FIRST CONTACT", [], number=1)
        self.add(stars())
        opening = Text("THE SIGNAL\nUNDER EUROPA", font="Arial", font_size=54, line_spacing=.8, color=ICE)
        fiction = Text("AN ORIGINAL COSMIC HORROR STORY", font="Courier New", font_size=18, color=DIM).next_to(opening, DOWN, buff=.5)
        self.play(FadeIn(opening), FadeIn(fiction), run_time=1.2)
        self.wait(1.3)
        self.play(FadeOut(opening), FadeOut(fiction), run_time=1)
        baseline = Line(LEFT*5.5, RIGHT*5.5, color=DIM, stroke_width=1).shift(DOWN*.4)
        waveform = wave_shape(y=-.4)
        source = Text("RECEIVER 04  /  EUROPA", font="Courier New", font_size=25, color=CYAN).shift(UP*1.6)
        axis = VGroup(*[Line(DOWN*.07, UP*.07, color=DIM).move_to([x,-1.8,0]) for x in np.linspace(-5.5,5.5,23)])
        scan = Line(DOWN*1.65, UP*.7, color=CYAN, stroke_width=1.2).shift(LEFT*5.4)
        self.play(Create(baseline), FadeIn(source), Create(axis), Create(waveform), run_time=1.5)
        phase = ValueTracker(0)
        waveform.add_updater(lambda obj: obj.become(wave_shape(y=-.4, phase=phase.get_value())))
        self.add(scan)
        self.play(scan.animate.shift(RIGHT*10.8), phase.animate.set_value(9), run_time=12, rate_func=linear)
        classification = Text("CLASSIFICATION: INTERFERENCE", font="Courier New", font_size=22, color=DIM).shift(DOWN*2.15)
        self.play(Write(classification), run_time=1.2)
        self.wait(2)
        replacement = Text("CLASSIFICATION: [ REMOVED ]", font="Courier New", font_size=22, color=ALARM).move_to(classification)
        waveform.clear_updaters()
        self.play(Transform(classification, replacement), waveform.animate.set_color(ALARM), run_time=.8)
        self.finish_slot()
