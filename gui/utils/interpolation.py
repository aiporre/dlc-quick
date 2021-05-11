import numpy as np


def euclidean_distance(x1, x2, eps=1e-6):
    sqrt_dist = (x1.x - x2.x) ** 2 + (x1.y - x2.y) ** 2
    if sqrt_dist < eps:
        return 0
    else:
        return np.sqrt(sqrt_dist)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'


class Segment:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @property
    def length(self):
        return euclidean_distance(self.end, self.start)

    def __str__(self):
        return f'Segment: (x1= {self.start} ==> x2={self.end}'


def uniform_interpolation(src_points, num_uniform_points):
    result_points = []

    src_points = [Point(*p) for p in src_points]
    segments = [Segment(p1, p2) for p1, p2 in zip(src_points[:-1], src_points[1:])]
    dist_total = sum([segment.length for segment in segments])
    uniform_distance = dist_total / (num_uniform_points - 1)
    current_dist = 0.0
    n = 0
    result_points.append((src_points[0].x, src_points[0].y))
    for k in range(1, num_uniform_points):
        next_distance = k * uniform_distance
        while current_dist + segments[n].length < next_distance:
            current_dist += segments[n].length
            n += 1
        ratio_current_dist = (next_distance - current_dist) / segments[n].length
        x_new = ratio_current_dist * (segments[n].end.x - segments[n].start.x) + segments[n].start.x
        y_new = ratio_current_dist * (segments[n].end.y - segments[n].start.y) + segments[n].start.y

        result_points.append((x_new, y_new))

    return result_points
