import matplotlib.pyplot as plt
import math

class DraggableCurve:
    '''
    Draggable Curve
    '''

    click_down = False # flag that signs click has been issued

    def __init__(self, point_set, figure=None, axes=None, selection_radius=0.02):
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

        self.curve_patch = plt.Polygon(self.point_set, closed=False, fill=False, linewidth=3, color='#F97306')

        self._axes.add_patch(self.curve_patch)

        self.cidclick = self.curve_patch.figure.canvas.mpl_connect(
            'button_press_event', self._on_click)
        self.cidrelease = self._figure.canvas.mpl_connect(
            'button_release_event', self._on_release)
        self.cidmotion = self._figure.canvas.mpl_connect(
            'motion_notify_event', self._on_motion)
        self.selection_radius = selection_radius

    def _on_click(self, event):
        '''
        Handler for click event

        :param event:
        :return:
        '''
        if event.button == 1  and event.inaxes == self._axes:
            is_contained = self._is_close_to_segment(event)
            print('Clicked on curve? ', is_contained)
            if is_contained:
                self.click = event.xdata, event.ydata
                self.click_down = True


    def _is_close_to_segment(self, event):
        '''
        Checks if event click happened near to a segment

        :param event:
        :return:
        '''
        x, y = event.xdata, event.ydata
        min_dist = math.inf
        # first finds nearest segment in the polyline
        s1, s2 = None, None
        for p1, p2 in zip(self.point_set[:-1], self.point_set[1:]):
            x2, y2 = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            dist = math.hypot(x - x2, y - y2)
            if dist < min_dist:
                min_dist = dist
                s1, s2 = p1, p2
        print(' segment 1 and 2: s1 = ', s1, '  s2 = ', s2)
        # checks if the points projects on segment. Shadow of point lies in the segment?
        R = math.hypot(s1[0] - s2[0], s1[1] - s2[1])
        d1 = math.hypot(s1[0] - x, s1[1] - y)
        d2 = math.hypot(s2[0] - x, s2[1] - y)
        # this is done check cosine law to be acute angles
        cos_1 = (R ** 2 + d1 ** 2 - d2 ** 2) / (2 * d1 * x)
        cos_2 = (R ** 2 + d2 ** 2 - d1 ** 2) / (2 * d2 * x)
        print(' cosines: 1 = ', cos_1, ' cos 2 =  ', cos_2 )
        if cos_1 > 0 and cos_2 > 0:
            # calculates the distance to the segment using the distance from a point to a line formula
            # computes line
            A = (s2[1] - s1[1])
            B = -(s2[0] - s1[0])
            C = s1[1]* (s2[0] - s1[0]) - s1[0] * A
            # evaluates distance = |Axo+Byo+C|/sqrt(A^2+B^2)
            projected_dist = math.fabs(A * x + B * y + C) / math.sqrt(A ** 2 + B ** 2) if A !=0 and B !=0 else math.inf
            print('projected distance: ', projected_dist)
            if projected_dist < self.selection_radius:
                # checks if distance is less that the selection radius
                is_close = True
            else:
                is_close = False
        else:
            is_close = False

        return is_close

    def _on_release(self, event):
        '''
        Handler for release button

        :param event:
        :return:
        '''
        if self.click_down:
            self.click = None
            self.click_down = False
            self.point_set = self.new_point_set if self.new_point_set is not None else self.point_set


    def _on_motion(self, event):
        '''
        Modifies curve_patch upon mouse motion if click_down flag was activated by clicking event.

        :param event:
        :return:
        '''
        if self.click_down:
            if event.inaxes == self._axes:
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

if __name__ == '__main__':
    geometry = [[0.0, 0.0], [0.1, 0.05], [0.2, 0.15], [0.3, 0.20], [0.4, 0.25], [0.5, 0.30],
                         [0.6, 0.25], [0.7, 0.15], [0.8, 0.05], [0.9, 0.025], [1.0, 0.5]]
    dc = DraggableCurve(geometry)
    plt.show()
