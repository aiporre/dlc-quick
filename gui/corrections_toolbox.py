
import argparse
import glob
import os
import os.path
from pathlib import Path
from matplotlib.path import Path as plot_path

import cv2
import re
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tables
import shutil
from functools import reduce
import wx
import wx.lib.scrolledpanel as SP
from matplotlib.backends.backend_wxagg import (
    NavigationToolbar2WxAgg as NavigationToolbar,
)
from matplotlib.widgets import LassoSelector
from mpl_toolkits.axes_grid1 import make_axes_locatable

# from gui.widgets import BasePanel, WidgetPanel, BaseFrame
from deeplabcut.gui.widgets import WidgetPanel, BasePanel, BaseFrame

from gui import auxfun_drag

from deeplabcut.utils import auxiliaryfunctions, auxiliaryfunctions_3d
from gui.utils import parse_yaml
from gui.utils.interpolation import uniform_interpolation
from gui.draggable_curve import DraggableCurve

to_action = {'positive_frames': 0, 'negative_frames': 1, 'delete': 2}
from_action = {0: 'positive_frames', 1: 'negative_frames', 2: 'delete'}




class ImagePanel(BasePanel):
    def __init__(self, parent, config, gui_size, **kwargs):
        super(ImagePanel, self).__init__(parent, config, gui_size, **kwargs)
        self.config = config
        self.toolbar = None

    def drawplot(self, img, img_name, itr, images_number, keep_view=False):
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        self.axes.clear()

        im = cv2.imread(img)[..., ::-1]

        ax = self.axes.imshow(im)
        self.orig_xlim = self.axes.get_xlim()
        self.orig_ylim = self.axes.get_ylim()
        divider = make_axes_locatable(self.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.axes.set_title(str(str(itr) + "/" + str(images_number - 1) + " " + img_name))
        self.figure.delaxes(self.figure.axes[1])

        if keep_view:
            self.axes.set_xlim(xlim)
            self.axes.set_ylim(ylim)
        if self.toolbar is None:
            self.toolbar = NavigationToolbar(self.canvas)
        return (self.figure, self.axes, self.canvas, self.toolbar)


    def getColorIndices(self, img, bodyparts):
        """
        Returns the colormaps ticks and . The order of ticks labels is reversed.
        """
        im = cv2.imread(img)
        norm = mcolors.Normalize(vmin=0, vmax=np.max(im))
        ticks = np.linspace(0, np.max(im), len(bodyparts))[::-1]
        return norm, ticks


class ScrollPanel(SP.ScrolledPanel):
    def __init__(self, parent):
        SP.ScrolledPanel.__init__(self, parent, -1, style=wx.SUNKEN_BORDER)
        self.SetupScrolling(scroll_x=True, scroll_y=True, scrollToTop=False)
        self.Layout()
        self.choices = list(to_action.keys())

    def add_radio_buttons(self):
        # adding radio buttons
        self.choiceBox = wx.BoxSizer(wx.VERTICAL)

        choices = self.choices

        self.fieldradiobox = wx.RadioBox(
            self,
            label="Choose correct action: ",
            style=wx.RA_SPECIFY_ROWS,
            choices=choices,
        )

        self.choiceBox.Add(self.fieldradiobox, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(self.choiceBox)
        self.Layout()
        return (self.choiceBox, self.fieldradiobox)


class CorrectionsFrame(BaseFrame):
    def __init__(self, parent, config, imtypes):
        super(CorrectionsFrame, self).__init__(
            "Dataset corrections", parent,
        )

        self.statusbar.SetStatusText(
            "Looking for a folder to start labeling. Click 'Load frames' to begin."
        )
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPressed)
        ###################################################################################################################################################

        # Splitting the frame into top and bottom panels.
        # Bottom panels contains the widgets.
        # The top panel is for showing images and plotting!

        topSplitter = wx.SplitterWindow(self)
        vSplitter = wx.SplitterWindow(topSplitter)

        self.image_panel = ImagePanel(
            vSplitter, config, self.gui_size)

        self.choice_panel = ScrollPanel(vSplitter)
        self.action_box, self.action_rdb = self.choice_panel.add_radio_buttons()
        self.action_rdb.Bind(wx.EVT_RADIOBUTTON, self.onActionSelection)


        vSplitter.SplitVertically(
            self.image_panel, self.choice_panel, sashPosition=self.gui_size[0] * 0.8
        )

        vSplitter.SetSashGravity(1)
        self.widget_panel = WidgetPanel(topSplitter)
        topSplitter.SplitHorizontally(
            vSplitter, self.widget_panel, sashPosition=self.gui_size[1] * 0.83
        )  # 0.9
        topSplitter.SetSashGravity(1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Add Buttons to the WidgetPanel and bind them to their respective functions.
        widgetsizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        self.load = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Load Dataset")
        widgetsizer.Add(self.load, 1, wx.ALL, 15)
        self.load.Bind(wx.EVT_BUTTON, self.browseDir)

        self.prev = wx.Button(self.widget_panel, id=wx.ID_ANY, label="<<Previous")
        widgetsizer.Add(self.prev, 1, wx.ALL, 15)
        self.prev.Bind(wx.EVT_BUTTON, self.prevImage)
        self.prev.Enable(False)

        self.next = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Next>>")
        widgetsizer.Add(self.next, 1, wx.ALL, 15)
        self.next.Bind(wx.EVT_BUTTON, self.nextImage)
        self.next.Enable(False)

        self.help = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Help")
        widgetsizer.Add(self.help, 1, wx.ALL, 15)
        self.help.Bind(wx.EVT_BUTTON, self.helpButton)
        self.help.Enable(True)
        #
        self.zoom = wx.ToggleButton(self.widget_panel, label="Zoom")
        widgetsizer.Add(self.zoom, 1, wx.ALL, 15)
        self.zoom.Bind(wx.EVT_TOGGLEBUTTON, self.zoomButton)
        self.widget_panel.SetSizer(widgetsizer)
        self.zoom.Enable(False)

        self.home = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Home")
        widgetsizer.Add(self.home, 1, wx.ALL, 15)
        self.home.Bind(wx.EVT_BUTTON, self.homeButton)
        self.widget_panel.SetSizer(widgetsizer)
        self.home.Enable(False)

        self.pan = wx.ToggleButton(self.widget_panel, id=wx.ID_ANY, label="Pan")
        widgetsizer.Add(self.pan, 1, wx.ALL, 15)
        self.pan.Bind(wx.EVT_TOGGLEBUTTON, self.panButton)
        self.widget_panel.SetSizer(widgetsizer)
        self.pan.Enable(False)

        self.lock = wx.CheckBox(self.widget_panel, id=wx.ID_ANY, label="Lock View")
        widgetsizer.Add(self.lock, 1, wx.ALL, 15)
        self.lock.Bind(wx.EVT_CHECKBOX, self.lockChecked)
        self.widget_panel.SetSizer(widgetsizer)
        self.lock.Enable(False)

        self.save = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Save")
        widgetsizer.Add(self.save, 1, wx.ALL, 15)
        self.save.Bind(wx.EVT_BUTTON, self.saveActions)
        self.save.Enable(False)

        widgetsizer.AddStretchSpacer(15)
        self.quit = wx.Button(self.widget_panel, id=wx.ID_ANY, label="Quit")
        widgetsizer.Add(self.quit, 1, wx.ALL, 15)
        self.quit.Bind(wx.EVT_BUTTON, self.quitButton)




        self.widget_panel.SetSizer(widgetsizer)
        self.widget_panel.SetSizerAndFit(widgetsizer)
        self.widget_panel.Layout()

        ###############################################################################################################################
        # Variables initialization

        self.currentDirectory = os.getcwd()
        self.images = []
        self.iter = 0
        self.file = 0
        self.updatedCoords = []
        self.dataFrame = None
        self.config_file = config
        self.new_labels = False
        self.buttonCounter = []
        self.bodyparts2plot = []
        self.drs = []
        self.num = []
        self.view_locked = False
        # Workaround for MAC - xlim and ylim changed events seem to be triggered too often so need to make sure that the
        # xlim and ylim have actually changed before turning zoom off
        self.prezoom_xlim = []
        self.prezoom_ylim = []
        self.selected_dir = None


    def OnKeyPressed(self, event=None):
        if event.GetKeyCode() == wx.WXK_RIGHT:
            self.nextImage(event=None)
        elif event.GetKeyCode() == wx.WXK_LEFT:
            self.prevImage(event=None)
        elif event.GetKeyCode() == wx.WXK_DOWN:
            self.nextLabel(event=None)
        elif event.GetKeyCode() == wx.WXK_UP:
            self.previousLabel(event=None)

    def browseDir(self, event):
        self.statusbar.SetStatusText("Looking for a folder to start corrections...")
        cwd = os.path.join(os.getcwd(), "labeled-data")
        dlg = wx.DirDialog(
            self,
            "Choose the directory where your extracted frames are saved:",
            cwd,
            style=wx.DD_DEFAULT_STYLE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.selected_dir = dlg.GetPath()
            self.load.Enable(False)
            self.next.Enable(True)
            self.save.Enable(True)
        else:
            dlg.Destroy()
            self.Close(True)
            return
        dlg.Destroy()

        # Enabling the zoom, pan and home buttons
        self.zoom.Enable(True)
        self.home.Enable(True)
        self.pan.Enable(True)
        self.lock.Enable(True)

        # reading config
        self.cfg = auxiliaryfunctions.read_config(self.config_file)
        self.project_path = self.cfg["project_path"]
        # self.colormap = plt.get_cmap(self.cfg["colormap"])
        # self.colormap = self.colormap.reversed()


        #TODO: image file type is Harcoded!
        imlist = [
                    str(fn)
                    for fn in Path(self.selected_dir).rglob("*.png") if fn.parent.name in to_action.keys()
                ]

        if len(imlist) == 0:
            print("No images found!!")
        else:
            print(f'{len(imlist)} images found')

        self.images = list(sorted(imlist, key=lambda x: int(
            Path(x).name[Path(x).name.index('-f-') + len('-f-'): Path(x).name.index('.png')])))


        self.statusbar.SetStatusText(
            "Working on folder: {}".format(os.path.split(str(self.selected_dir))[-1])
        )


        print(' self.images[0]', self.images[0])

        # parsing labels


        self.current_actions = [to_action[Path(im).parent.name] for im in self.images]
        self.perform_actions = len(self.current_actions) * [None]




        # ploting images:
        self.iter = 0
        self.img = str(self.images[self.iter])
        img_name =  Path(self.img).name
        (
            self.figure,
            self.axes,
            self.canvas,
            self.toolbar,
        ) = self.image_panel.drawplot(
            self.img, img_name, self.iter, len(self.images))
        self.figure.canvas.draw()

        self.action_rdb.SetSelection(self.current_actions[0])




    def prevImage(self, event):
        # Checks for the first image and disables the Previous button
        if self.iter == 0:
            self.prev.Enable(False)
            return
        else:
            self.next.Enable(True)

        self.statusbar.SetStatusText(
            "Working on folder: {}".format(os.path.split(str(self.selected_dir))[-1])
        )

        self.iter = self.iter - 1
        print(self.iter)
        if len(self.images) >= self.iter:
            selected_action  = self.current_actions[self.iter] if self.perform_actions[self.iter] is None else to_action[self.perform_actions[self.iter]]
            print('<<<--', selected_action)
            self.action_rdb.SetSelection(selected_action)
            self.img = str(self.images[self.iter])
            img_name = Path(self.img).name
            self.figure, self.axes, self.canvas, self.toolbar = self.image_panel.drawplot(self.img, img_name, self.iter, len(self.images), keep_view=self.view_locked)
            self.figure.canvas.draw()

    def nextImage(self, event):
        #  Checks for the last image and disables the Next button
        if len(self.images) - self.iter == 1:
            self.next.Enable(False)
            return
        self.prev.Enable(True)

        self.statusbar.SetStatusText(
            "Working on folder: {}".format(os.path.split(str(self.selected_dir))[-1])
        )

        self.iter = self.iter + 1
        print(self.iter)
        if len(self.images) >= self.iter:
            selected_action  = self.current_actions[self.iter] if self.perform_actions[self.iter] is None else to_action[self.perform_actions[self.iter]]
            print('-->>', selected_action)
            self.action_rdb.SetSelection(selected_action)
            self.img = str(self.images[self.iter])
            img_name = Path(self.img).name
            self.figure, self.axes, self.canvas, self.toolbar = self.image_panel.drawplot( self.img,img_name, self.iter, len(self.images), keep_view=self.view_locked)
            self.figure.canvas.draw()

    def helpButton(self, event):
        """
        Opens Instructions
        """
        # MainFrame.updateZoomPan(self)
        wx.MessageBox(
            "1. Select action from the radial button.\n\n 2. Zoom/Pan images by clicking in the button and dragging \n left clicked on the image.\n\n3. Click Next/Previous to move to the next/previous image (or hot-key arrows left and right).\n 8. You can click Cntrl+C to copy+paste labels from a previous image into the current image. \n\n9. When finished labeling all the images, click 'Save' to save all the labels as a .h5 file. \n\n4. Click OK to continue using the labeling GUI. For more tips and hotkeys: see docs!!",
            "User instructions",
            wx.OK | wx.ICON_INFORMATION,
        )
        self.statusbar.SetStatusText("Help")

    def saveActions(self, event):
        if self.selected_dir is None:
            return
        def move_image(iteration, action):
            src_image = self.images[iteration]
            image_name = os.path.split(src_image)[-1]
            dataset_dir = (Path(src_image).parent.parent.absolute())
            dst_image = os.path.join(dataset_dir, action, image_name)
            shutil.move(src_image, dst_image)
            self.images[iteration] = dst_image

        for i, action in enumerate(self.perform_actions):
            if action is None:
                continue
            elif action in ['negative_frames', 'positive_frames']:
                print('moving to ', action)
                move_image(i, action)
                self.perform_actions[i] = None
                self.current_actions[i] = to_action[action]

            elif action == 'delete':
                print('deletering')
                img_src = self.images[i]
                os.remove(img_src)
                self.images.pop(i)
                self.perform_actions.pop(i)
                self.current_actions.pop(i)
            else:
                raise Exception('action is not reconized. possible actions' + str(to_action.keys()))

        print(self.perform_actions[:10])
        print(self.current_actions[:10])


    def quitButton(self, event):
        missing_actions = ''
        # if self.selected_dir:
        #     missing_actions = reduce(lambda x,y: x and y is not None, self.perform_actions, initial=True)
        #     missing_actions = ' Changes were not performed and will be lost' if missing_actions else ''
        continue_corrections = wx.MessageBox(
            "Do you want to exit?" + missing_actions, 'Continue?',
            wx.YES_NO | wx.ICON_INFORMATION,
        )

        self.statusbar.SetStatusText("Quitting now!")
        print('continue_corrections: ', continue_corrections)
        if continue_corrections == 2:
        #     return
        # else:
            self.Destroy()

    def onActionSelection(self, event):
        print('selection of action')
        # asserts that directory was select using browseDir
        if self.selected_dir is None:
            return

        action_selection = self.action_rdb.GetSelection()
        self.perform_actions[self.iter] = from_action[action_selection]
        print(self.perform_actions[:10])


def show(config, config3d, sourceCam, imtypes=["*.png"]):
    app = wx.App()
    frame = CorrectionsFrame(None, config, imtypes).Show()
    app.MainLoop()


if __name__ == '__main__':
    imtypes = ["*.png"]
    config3d = None
    sourceCam = None
    config = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config, config3d, sourceCam, imtypes=imtypes)