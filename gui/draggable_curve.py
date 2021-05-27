import matplotlib.pyplot as plt
import math
from matplotlib.patches import Polygon
import wx

class DraggableCurve:
    '''
    Draggable Curve
    '''

    click_down = None # flag that signs click has been issued

    def __init__(self, point_set, figure=None, axes=None, selection_radius=0.02, color='#F97306'):
        '''

        :param point_set: Point
        :param selection_radius:
        '''
        # figure initialization:
        if figure is None:
            self._figure = plt.figure("Example plot")
            self._axes = self._figure.add_subplot(111)
            self._axes.grid(which='both')
        else:
            assert axes is not None, 'When figure is input \'axes\' must be specified.'
            self._figure = figure
            self._axes = axes

        self.point_set = point_set
        self.new_point_set = point_set

        self.curve_patch = Polygon(self.point_set, closed=False, fill=False, linewidth=3, color=color, alpha=0.4)

        self._axes.add_patch(self.curve_patch)

        self.cidclick = self.curve_patch.figure.canvas.mpl_connect(
            'button_press_event', self._on_click)
        self.cidrelease = self._figure.canvas.mpl_connect(
            'button_release_event', self._on_release)
        self.cidmotion = self._figure.canvas.mpl_connect(
            'motion_notify_event', self._on_motion)
        self.selection_radius = selection_radius
        self.active = True

    def _disconnect(self):
        "disconnect all the stored connection ids"
        self._figure.canvas.mpl_disconnect(self.cidclick)
        self._figure.canvas.mpl_disconnect(self.cidrelease)
        self._figure.canvas.mpl_disconnect(self.cidmotion)

    def _on_click(self, event):
        '''
        Handler for click event

        :param event:
        :return:
        '''
        # if not self.active:
        #     return

        if DraggableCurve.click_down is None and event.inaxes == self._axes:
            is_contained = self._is_close_to_segment(event)
            # print('Clicked on curve? ', is_contained)
            if not is_contained:
                return
            # if left click then the curve is moved
            if event.button == 1:
                if is_contained:
                    self.click = event.xdata, event.ydata
                    DraggableCurve.click_down = self
            elif event.button == 2:
                # if central button then the whisker is deleted.
                self.delete_from_canvas()

    def delete_from_canvas(self):
        '''
        Removes the draggable curve and disconnects event handlers for this object

        :return:
        '''
        DraggableCurve.lock = None
        self.curve_patch.set_visible(False)
        self.click = None
        self.active = False
        self._disconnect()
        self._figure.canvas.draw()

    def calculate_close_distance_to_curve(self, x, y):
        '''
        Calculates the closest distance to the curve if it fits into the radius of selection

        :param x:
        :param y:
        :return:
        '''
        min_dist = math.inf
        # first finds nearest segment in the polyline
        s1, s2 = None, None
        for p1, p2 in zip(self.point_set[:-1], self.point_set[1:]):
            x2, y2 = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            dist = math.hypot(x - x2, y - y2)
            if dist < min_dist:
                min_dist = dist
                s1, s2 = p1, p2
        # print(' segment 1 and 2: s1 = ', s1, '  s2 = ', s2)
        # checks if the points projedcts on segment. Shadow of point lies in the segment?
        R = math.hypot(s1[0] - s2[0], s1[1] - s2[1])
        d1 = math.hypot(s1[0] - x, s1[1] - y)
        d2 = math.hypot(s2[0] - x, s2[1] - y)
        # this is done check cosine law to be acute angles
        cos_1 = (R ** 2 + d1 ** 2 - d2 ** 2) / (2 * d1 * x)
        cos_2 = (R ** 2 + d2 ** 2 - d1 ** 2) / (2 * d2 * x)
        if cos_1 > 0 and cos_2 > 0:
            # calculates the distance to the segment using the distance from a point to a line formula
            # computes line
            A = (s2[1] - s1[1])
            B = -(s2[0] - s1[0])
            C = s1[1] * (s2[0] - s1[0]) - s1[0] * A
            # evaluates distance = |Axo+Byo+C|/sqrt(A^2+B^2)
            projected_dist = math.fabs(A * x + B * y + C) / math.sqrt(
                A ** 2 + B ** 2) if A != 0 and B != 0 else math.inf
            if projected_dist < self.selection_radius:
                # checks if distance is less that the selection radius
                dist_to_curve = projected_dist
            else:
                dist_to_curve = None
        else:
            dist_to_curve = None

        return dist_to_curve

    def _is_close_to_segment(self, event):
        '''
        Checks if event click happened near to a segment

        :param event:
        :return:
        '''
        x, y = event.xdata, event.ydata
        if self.calculate_close_distance_to_curve(x, y) is None:
            is_close = False
        else:
            is_close = True
        return is_close

    def _on_release(self, event):
        '''
        Handler for release button

        :param event:
        :return:
        '''
        # if not self.active:
        #     return

        if DraggableCurve.click_down == self:
            self.click = None
            DraggableCurve.click_down = None
            self.point_set = self.new_point_set if self.new_point_set is not None else self.point_set


    def _on_motion(self, event):
        '''
        Modifies curve_patch upon mouse motion if click_down flag was activated by clicking event.

        :param event:
        :return:
        '''
        #
        # if not self.active:
        #     return
        #
        if DraggableCurve.click_down == self:
            if event.inaxes == self._axes and event.button == 1:
                xclick, yclick = self.click

                # compute shift respect from the click point
                dx = event.xdata - xclick
                dy = event.ydata - yclick

                # shift point points
                xdx = [i + dx for i, _ in self.point_set]
                ydy = [i + dy for _, i in self.point_set]

                # update plot
                self.new_point_set = list(zip(xdx, ydy))
                self.curve_patch.set_xy(self.new_point_set)
                self.curve_patch.figure.canvas.draw()

    def __str__(self):
        return str(self.point_set[0]) + ' --> ' + str(self.point_set[-1])


if __name__ == '__main__':
    points = [[0.0, 0.0], [0.1, 0.05], [0.2, 0.15], [0.3, 0.20], [0.4, 0.25], [0.5, 0.30],
              [0.6, 0.25], [0.7, 0.15], [0.8, 0.05], [0.9, 0.025], [1.0, 0.5]]
    dc = DraggableCurve(points)
    plt.show()
