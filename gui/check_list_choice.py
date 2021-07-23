#!pythonw

import os
import wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

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


class ChoiceList(wx.Frame):
    def __init__(self, parent, title='choice check box'):
        super(ChoiceList, self).__init__(parent)
        base_window = wx.Window(self)
        # self.panel = ImagePanel(window, config, self.gui_size)
        self.panel = wx.Panel(base_window, -1)
        text = wx.StaticText(self.panel, label="Colored text")

        self.choice = wx.Choice(base_window, id=-1, choices=['option1', 'option2', 'option3'])
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(base_window, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.panel.Layout()


def show(config, startpath='.'):
    app = wx.App()
    frame = ChoiceList(None)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    show(None)
