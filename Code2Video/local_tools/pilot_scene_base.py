"""Film-specific Manim scaffold: archive UI, schematic spacecraft and icy geometry."""
from manim import *
import numpy as np

INK = "#03070D"
ICE = "#A9C7D5"
CYAN = "#68D9E8"
RUST = "#B46C58"
ALARM = "#FF605E"
DIM = "#526879"


def stars(seed=6):
    rng = np.random.default_rng(seed)
    return VGroup(*[Dot([x, y, 0], radius=r, color=WHITE, fill_opacity=a)
                    for x, y, r, a in zip(rng.uniform(-6.9, 6.9, 80), rng.uniform(-3.8, 3.8, 80),
                                          rng.uniform(.006, .018, 80), rng.uniform(.12, .5, 80))])


def wave_shape(width=10, y=0, phase=0, color=CYAN, amplitude=.7):
    x = np.linspace(-width / 2, width / 2, 180)
    envelope = sum(np.exp(-((x-c)/.3)**2) for c in (-3.1, 0, 3.1))
    signal = .06 * np.sin(11*x+phase) + amplitude * envelope * np.sin(18*x+phase)
    return VMobject(color=color, stroke_width=2.6).set_points_as_corners(
        np.column_stack([x, signal+y, np.zeros_like(x)]))


def spacecraft(scale=.48):
    bus = Cube(side_length=.55, fill_color=ICE, fill_opacity=1, stroke_color=DIM, stroke_width=.7)
    panels = VGroup(*[Rectangle(width=.92, height=.43, color=CYAN, fill_color="#123341",
                               fill_opacity=1, stroke_width=1).shift(RIGHT*x) for x in (-.8, .8)])
    boom = Line3D([0, 0, .22], [0, 0, .75], thickness=.018, color=ICE)
    dish = Cone(base_radius=.19, height=.15, color=ICE, fill_opacity=1,
                direction=OUT, show_base=True).shift(OUT*.8)
    return VGroup(bus, panels, boom, dish).scale(scale)


def ice_sphere(radius=2.1, cutaway=False):
    if cutaway:
        body = Surface(lambda u, v: radius*np.array([np.sin(u)*np.cos(v), np.sin(u)*np.sin(v), np.cos(u)]),
                       u_range=[0, PI], v_range=[0, PI], resolution=(14, 18),
                       fill_color=ICE, fill_opacity=1, stroke_width=.25, stroke_color=DIM,
                       checkerboard_colors=False)
    else:
        body = Sphere(radius=radius, resolution=(20, 14), fill_color=ICE,
                      fill_opacity=1, stroke_width=.1, stroke_color=ICE, checkerboard_colors=False)
    cracks = VGroup()
    for i, latitude in enumerate(np.linspace(.35, 2.7, 8)):
        cracks.add(ParametricFunction(lambda v, u=latitude, k=i: (radius+.014)*np.array([
            np.sin(u+.04*np.sin(v*4+k))*np.cos(v),
            np.sin(u+.04*np.sin(v*4+k))*np.sin(v),
            np.cos(u+.04*np.sin(v*4+k))]),
            t_range=[0, PI if cutaway else TAU, .05], color=RUST, stroke_width=1.15))
    return VGroup(body, cracks)


class FilmMixin:
    def finish_slot(self):
        remaining = 30 - self.renderer.time
        if remaining < .95:
            raise ValueError(f"Shot exceeds its 30-second slot: {self.renderer.time}")
        self.wait(remaining-1)
        for obj in self.mobjects:
            obj.clear_updaters()
        self.play(*[FadeOut(obj) for obj in list(self.mobjects)], run_time=.75)
        self.wait(.25)

    def hud(self, title_text, number, fixed=False):
        self.title = Text(title_text.upper(), font="Arial", font_size=24, color=ICE)
        self.title.to_corner(UL, buff=.42)
        self.lecture = VGroup()
        if fixed:
            self.add_fixed_in_frame_mobjects(self.title)
        else:
            self.add(self.title)


class TeachingScene(FilmMixin, Scene):
    def setup_layout(self, title_text, lecture_lines, number=1):
        self.camera.background_color = INK
        self.hud(title_text, number)


class Teaching3DScene(FilmMixin, ThreeDScene):
    def setup_3d_layout(self, title_text, lecture_lines, phi=65*DEGREES, theta=-52*DEGREES, number=3):
        self.camera.background_color = INK
        self.set_camera_orientation(phi=phi, theta=theta)
        self.hud(title_text, number, fixed=True)

    def screen_label(self, text, position, color=ICE, size=20):
        label = Text(text, font="Courier New", font_size=size, color=color).move_to(position)
        self.add_fixed_in_frame_mobjects(label)
        return label
