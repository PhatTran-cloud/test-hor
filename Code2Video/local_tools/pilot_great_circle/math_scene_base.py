from pilot_scene_base import *


def ant_2d(scale=1.0, color=ALARM):
    body = Ellipse(width=.44, height=.25, color=color, fill_color=color, fill_opacity=1)
    head = Circle(radius=.13, color=color, fill_color=color, fill_opacity=1).shift(RIGHT*.27)
    legs = VGroup(*[
        Line([-0.10, 0, 0], [x, y, 0], color=color, stroke_width=2)
        for x, y in [(-.25,.20), (0,.24), (.24,.20), (-.25,-.20), (0,-.24), (.24,-.20)]
    ])
    feelers = VGroup(Line([.35,.08,0],[.57,.25,0],color=color,stroke_width=1.5),
                     Line([.35,-.08,0],[.57,-.25,0],color=color,stroke_width=1.5))
    return VGroup(body, head, legs, feelers).scale(scale)


def sphere_grid(radius=2.2, color=ICE, opacity=.75):
    sphere = Sphere(radius=radius, resolution=(24, 16), fill_color="#163342", fill_opacity=opacity,
                    stroke_color=color, stroke_width=.22, checkerboard_colors=False)
    lines = VGroup()
    for lat in np.linspace(-1.15, 1.15, 7):
        rr = radius*np.cos(lat)
        lines.add(Circle(radius=max(.04, rr), color=DIM, stroke_width=.55).rotate(90*DEGREES, axis=RIGHT).shift(OUT*radius*np.sin(lat)))
    for lon in np.linspace(0, TAU, 8, endpoint=False):
        lines.add(Circle(radius=radius, color=DIM, stroke_width=.55).rotate(lon, axis=OUT))
    return VGroup(sphere, lines)


def point_on_sphere(radius, lat, lon):
    return radius*np.array([np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)])


def great_circle_points(a, b, count=80):
    a = np.array(a, dtype=float); b = np.array(b, dtype=float)
    a /= np.linalg.norm(a); b /= np.linalg.norm(b)
    omega = np.arccos(np.clip(np.dot(a,b), -1, 1))
    if omega < 1e-6: return np.array([a for _ in range(count)])
    ts = np.linspace(0, 1, count)
    return np.array([(np.sin((1-t)*omega)*a + np.sin(t*omega)*b)/np.sin(omega) for t in ts])


def path_3d(points, radius=2.2, color=CYAN, width=4):
    return VMobject(color=color, stroke_width=width).set_points_smoothly([radius*np.array(p) for p in points])
