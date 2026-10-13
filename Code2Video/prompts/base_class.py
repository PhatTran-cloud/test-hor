base_class = """
class TeachingScene(Scene):
    def setup_layout(self, title_text, lecture_lines):
        # BASE
        self.camera.background_color = "#000000"
        self.title = Text(title_text, font="Arial", font_size=28, color=WHITE).to_edge(UP)
        self.add(self.title)

        # Left-side lecture content (bullets with "-")
        lecture_texts = [Text(line, font="Arial", font_size=22, color=WHITE) for line in lecture_lines]
        self.lecture = VGroup(*lecture_texts).arrange(DOWN, aligned_edge=LEFT).scale(0.8)
        self.lecture.to_edge(LEFT, buff=0.2)
        self.add(self.lecture)

        # Define fine-grained animation grid (4x4 grid on right side)
        self.grid = {}
        rows = ["A", "B", "C", "D", "E", "F"]  # Top to bottom
        cols = ["1", "2", "3", "4", "5", "6"]  # Left to right

        for i, row in enumerate(rows):
            for j, col in enumerate(cols):
                x = 0.5 + j * 1
                y = 2.2 - i * 1
                self.grid[f"{row}{col}"] = np.array([x, y, 0])

    def place_at_grid(self, mobject, grid_pos, scale_factor=1.0):
        mobject.scale(scale_factor)
        mobject.move_to(self.grid[grid_pos])
        return mobject

    def place_in_area(self, mobject, top_left, bottom_right, scale_factor=1.0):
        tl_pos = self.grid[top_left]
        br_pos = self.grid[bottom_right]
        
        # Calculate center of the area
        center_x = (tl_pos[0] + br_pos[0]) / 2
        center_y = (tl_pos[1] + br_pos[1]) / 2
        center = np.array([center_x, center_y, 0])
        
        mobject.scale(scale_factor)
        mobject.move_to(center)
        return mobject

    def add_visual_layers(self, foreground=None, midground=None, background=None):
        # Register scene layers so generated code keeps visual hierarchy explicit.
        self.visual_layers = {
            "background": VGroup(*(background or [])),
            "midground": VGroup(*(midground or [])),
            "foreground": VGroup(*(foreground or [])),
        }
        for layer in (self.visual_layers["background"], self.visual_layers["midground"], self.visual_layers["foreground"]):
            self.add(layer)
        return self.visual_layers


class Teaching3DScene(ThreeDScene):
    # Shared 3D explainer scaffold; geometry remains authored by each scene.
    def setup_3d_layout(self, title_text, lecture_lines, phi=68 * DEGREES, theta=-48 * DEGREES):
        self.camera.background_color = "#05070D"
        self.set_camera_orientation(phi=phi, theta=theta)
        self.title = Text(title_text, font="Arial", font_size=28, color=WHITE)
        self.lecture = VGroup(*[
            Text(line, font="Arial", font_size=22, color=WHITE)
            for line in lecture_lines
        ]).arrange(DOWN, aligned_edge=LEFT).scale(0.72)
        self.title.to_edge(UP)
        self.lecture.to_edge(LEFT, buff=0.2)
        self.add_fixed_in_frame_mobjects(self.title, self.lecture)

    def place_3d(self, mobject, point, scale_factor=1.0):
        mobject.scale(scale_factor)
        mobject.move_to(np.array(point, dtype=float))
        return mobject
"""
