from .interpolation import uniform_interpolation
import matplotlib.pyplot as plt

def test_uniform_interpolation():
    points = [(0.0,0.1), (1.1,2.9),(1.7,3.1), (2.1,5.1), (2.2,5.2), (3.23,5.2), (4.3, 6.1)]
    uniform_points = uniform_interpolation(points, 7)
    print(uniform_points)
    xs = [xx[0] for xx in points]
    ys = [xx[1] for xx in points]
    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    ax.plot(xs, ys, 'ro')
    xs = [xx[0] for xx in uniform_points]
    ys = [xx[1] for xx in uniform_points]
    ax.plot(xs, ys, 'go')
    ax.set_aspect('equal')
    plt.show()


