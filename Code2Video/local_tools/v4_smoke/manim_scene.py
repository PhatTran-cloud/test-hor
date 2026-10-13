"""Technical clock/adapter proof. Deliberately mathematical, not a finished film."""
from manim import Circle, Line, Scene, WHITE, BLUE
from v4_runtime import load_contract, absolute_frame, state_at, record_execution


class V4ClockProof(Scene):
    def construct(self):
        productionContract = load_contract()
        start = absolute_frame(productionContract, 0)
        state = state_at(productionContract, "point", start)
        print(f"V4_CLOCK_PROOF absolute_start={start} point.x={state['x']}")
        axis = Line([-4, 0, 0], [4, 0, 0], color=WHITE)
        point = Circle(radius=.15, color=BLUE, fill_opacity=1).move_to([state["x"], 0, 0])
        self.add(axis, point)
        elapsed = 0
        for frame in productionContract["shot"]["execution"]["review_frames"]:
            local = frame - start
            if local > elapsed:
                self.wait((local-elapsed)/60)
            record_execution(productionContract, frame, {"axis": axis, "point": point}, "custom")
            elapsed = local
        self.wait((productionContract["duration_frames"]-elapsed)/60)
