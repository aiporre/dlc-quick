import os
from pathlib import Path
import wx


from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import matplotlib.pyplot as plt
from deeplabcut.gui.widgets import BaseFrame, BasePanel
from deeplabcut.utils import auxiliaryfunctions
from matplotlib.figure import Figure


class ImagePanel(wx.Panel):
    def __init__(self, parent, config, gui_size, title='', **kwargs):

        h = gui_size[0]
        w = gui_size[1]
        super(ImagePanel, self).__init__(parent, -1, style=wx.SUNKEN_BORDER, size=(h, w))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.orig_xlim = None
        self.orig_ylim = None
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        self.config = config
        self.title = ''
    def getfigure(self):
        """
        Returns the figure, axes and canvas
        """
        return self.figure, self.axes, self.canvas


class ImageFrame(BaseFrame):
    def __init__(self, parent, title='Image', config=None):
        super(ImageFrame, self).__init__(parent=parent, frame_title=title)
        window = wx.Window(self)
        self.panel = ImagePanel(window, config, self.gui_size)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(window, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.panel.Layout()


def show(config, startpath='.'):
    app = wx.App()
    frame = ImageFrame(None, config=config)
    frame.Show()
    figure, axes, canvas = frame.panel.getfigure()
    x = [0, 1, 3]
    y = [1.3, 4.3, 7.8]
    axes.plot(x, y)
    canvas.draw()
    app.MainLoop()



if __name__ == '__main__':
    config = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config, startpath)
