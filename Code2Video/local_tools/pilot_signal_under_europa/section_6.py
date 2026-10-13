from pilot_scene_base import *


class Section6Scene(Teaching3DScene):
    def construct(self):
        self.setup_3d_layout("05:11 UTC / FINAL FRAME",[],phi=42*DEGREES,theta=-90*DEGREES,number=6)
        # A real opening in the annular mesh, not a black sticker on a cube.
        terrain=Surface(lambda r,t: np.array([r*np.cos(t),r*np.sin(t),
                        .05*np.sin(2*t+r)+.04*np.cos(5*t-r)]),
                        u_range=[1.25,5.8],v_range=[0,TAU],resolution=(10,32),
                        fill_color=ICE,fill_opacity=1,stroke_color=DIM,stroke_width=.18,
                        checkerboard_colors=False)
        void=Circle(radius=1.23,fill_color=BLACK,fill_opacity=1,stroke_opacity=0).shift(IN*.17)
        rim=Circle(radius=1.26,color=RUST,stroke_width=2)
        cracks=VGroup(*[ParametricFunction(lambda r,k=k: np.array([
            r*np.cos(k+.018*np.sin(5*r)),r*np.sin(k+.018*np.sin(5*r)),.08]),
            t_range=[1.3,4.7,.1],color=RUST,stroke_width=1.1) for k in np.linspace(0,TAU,11)[:-1]])
        self.play(FadeIn(terrain),FadeIn(void),Create(rim),Create(cracks),run_time=2)
        status=self.screen_label("RECEIVING...",[0,2.6,0],CYAN,22)
        self.move_camera(phi=20*DEGREES,zoom=1.18,run_time=6)
        for i in range(1,5):
            replacement=Text(str(i),font="Courier New",font_size=42,color=ALARM).move_to([0,2.6,0])
            self.play(Transform(status,replacement),run_time=.3)
            self.wait(1.0)
        self.play(FadeOut(status),run_time=.5)
        self.move_camera(phi=0,zoom=2.5,run_time=8)
        last=self.screen_label("STILL HERE?",[0,2.6,0],ALARM,26)
        self.wait(2)
        self.play(FadeOut(last),FadeOut(self.title),run_time=.6)
        self.finish_slot()
