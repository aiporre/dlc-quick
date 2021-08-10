
import os.path

import cv2
import matplotlib.colors as mcolors
import numpy as np
import wx.lib.scrolledpanel as SP
from matplotlib.backends.backend_wxagg import (
    NavigationToolbar2WxAgg as NavigationToolbar,
)
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from deeplabcut.gui.widgets import WidgetPanel, BasePanel, BaseFrame

to_action = {'positive': 0, 'negative': 1, 'delete': 2}
from_action = {0: 'positive', 1: 'negative', 2: 'delete'}
import os
from pathlib import Path
import wx
from deeplabcut.gui.widgets import WidgetPanel, BaseFrame
from deeplabcut.utils import auxiliaryfunctions
from gui.utils import parse_yaml
from shutil import move

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

    def add_slider(self, max_value):
        # vSplitter.SetSashGravity(1)
        # adding radio buttons
        self.sliderBox = wx.BoxSizer(wx.VERTICAL)

        self.slider = wx.Slider(self, value=1, minValue=1, maxValue=max_value,
                             style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sliderBox.Add(self.slider, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizerAndFit(self.sliderBox)
        self.Layout()
        return (self.sliderBox, self.slider)


class ImagePanel(BasePanel):
    def __init__(self, parent, config, gui_size, **kwargs):
        super(ImagePanel, self).__init__(parent, config, gui_size, **kwargs)
        self.config = config
        self.toolbar = None
        self.cnt = 10

    def drawplot(self, img, title, keep_view=False):
        print('new plot')
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        self.axes.clear()
        #im = cv2.imread(img)[..., ::-1]
        # im = np.random.random((250,320,3))
        self.cnt +=1
        ax = self.axes.imshow(img)
        self.orig_xlim = self.axes.get_xlim()
        self.orig_ylim = self.axes.get_ylim()
        divider = make_axes_locatable(self.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.axes.set_title(title)
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

class VideoFrame(BaseFrame):
    def __init__(self, parent, config, video_path):
        super(VideoFrame, self).__init__(
            "Video player", parent,
        )
        # load video
        if os.path.exists(video_path) and video_path.endswith('.npy'):
            self.data = np.load(video_path, allow_pickle=True)
        else:
            raise FileExistsError(f'File {video_path} do not exist.')
        self.vid = self.data[()]['data']
        self.window_index = self.data[()]['window_index']
        self.statusbar.SetStatusText(
            "Loaded video paltin mode the slider to chand e tthe farmes."
        )
        # define layout
        topSplitter = wx.SplitterWindow(self)
        self.image_panel = ImagePanel(
            topSplitter, config, self.gui_size)
        self.figure, self.axes, self.canvas, self.toolbar = self.image_panel.drawplot(self.vid[0], 'First title')
        self.figure.canvas.draw()
        self.choice_panel = ScrollPanel(topSplitter)
        self.slider_box, self.slider = self.choice_panel.add_slider(self.window_index)
        self.slider.Bind(wx.EVT_SLIDER, self.onSliderChanged)
        self.slider.Enable(True)
        topSplitter.SplitHorizontally(
            self.image_panel, self.choice_panel, sashPosition=self.gui_size[1] * 0.83
        )  # 0.9
        topSplitter.SetSashGravity(1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def onSliderChanged(self, event):
        print('slider changed new plot')
        slider_value = self.slider.GetValue()-1
        print('__. frame',  slider_value)
        self.figure, self.axes, self.canvas, self.toolbar = self.image_panel.drawplot(self.vid[slider_value], 'New title')
        self.figure.canvas.draw()

class OscCorrections(BaseFrame):
    def __init__(self, parent, title='Osc Whisker Corrections', config=None):
        super(OscCorrections, self).__init__(parent=parent, frame_title=title)
        self.panel = WidgetPanel(self)
        self.WIDTHOFINPUTS = 100
        self.config = config

        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Osc Whisker Corrections")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # choice iteration from configuration file
        cfg = parse_yaml(self.config)
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        current_iteration = 'iteration-' + str(cfg['iteration'])
        self.iterations = self.find_iterations()
        assert len(self.iterations) > 0, "Couldn't find an iteration, you must train a dlc-model first."

        self.iteration = wx.Choice(self.panel, id=-1, choices=self.iterations)
        # sets the current interation from the config.yaml file.
        try:
            self.iteration.SetSelection(self.iterations.index(current_iteration))
        except ValueError as e:
            print('Error' + str(e))
            self.iteration.SetSelection(0)

        # Initial datapath calculation
        self.project_path = cfg['project_path']
        datapathLbl = wx.StaticText(self.panel, -1, "Dataset path:", size=wx.Size(self.gui_size[0], 25))
        self.datapath = wx.DirPickerCtrl(self.panel, -1)
        datapath_initial = os.path.join(self.project_path, 'training-datasets', self.iterations[self.iteration.GetSelection()],'osc-dataset')
        self.datapath.SetPath(datapath_initial)
        self.datapath.Bind(wx.EVT_DIRPICKER_CHANGED, self.update_sample_list)
        
        # list the samples
        samplesLbl = wx.StaticText(self.panel, -1, "Samples: ", size=wx.Size(self.gui_size[0], 25))
        self.listSamples = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT)
        self.listSamples.InsertColumn(0, "index")
        self.listSamples.InsertColumn(1, "Name")
        self.listSamples.InsertColumn(2, "Num Videos")
        self.listSamples.SetColumnWidth(0, int(self.gui_size[0]*0.1))
        self.listSamples.SetColumnWidth(1, int(self.gui_size[0]*0.8))
        self.listSamples.SetColumnWidth(1, int(self.gui_size[0]*0.1))
        self.listSamples.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.update_selected_sample)

        # list of sections in the selected sample
        sampleSectionsLbl = wx.StaticText(self.panel, -1, "Sections: ")
        self.listSampleSections = wx.Choice(self.panel, id=-1, choices=[])
        self.sampleSectionsPointer = None
        self.listSampleSections.Bind(wx.EVT_CHOICE, self.onSelectNewSection)

        # action to perform
        self.choice_panel = ScrollPanel(self.panel)
        self.action_box, self.action_rdb = self.choice_panel.add_radio_buttons()
        self.action_rdb.Bind(wx.EVT_RADIOBOX, self.onActionSelection)
        self.action_rdb.Enable(False)

        # button to create dataset object in the trainer, also saves the training config with the given parameters.
        self.buttonPlay = wx.Button(self.panel, label="Play Section")
        self.buttonPlay.Bind(wx.EVT_BUTTON, self.onPlay)
        self.buttonPlay.Enable(False)

        # button to plot 16 images of the datatset, batchsize has no influence in that
        self.buttonSpec = wx.Button(self.panel, label="Show Spectrogram")
        self.buttonSpec.Bind(wx.EVT_BUTTON, self.onShowSpec)
        self.buttonSpec.Enable(False)

        # button to train model
        self.buttonApplyActions = wx.Button(self.panel, label="Apply Corrections")
        self.buttonApplyActions.Bind(wx.EVT_BUTTON, self.onApplyCorrections)
        self.buttonApplyActions.Enable(False)

        # button to train model
        self.buttonNext = wx.Button(self.panel, label="next >>")
        self.buttonNext.Bind(wx.EVT_BUTTON, self.onNext)
        self.buttonNext.Enable(False)

        # button to train model
        self.buttonPrev = wx.Button(self.panel, label="<< prev")
        self.buttonPrev.Bind(wx.EVT_BUTTON, self.onPrev)
        self.buttonPrev.Enable(False)

        # create the main sizer that contains the context and input sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)
        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer= wx.BoxSizer(wx.HORIZONTAL)
        inputSizer = wx.BoxSizer(wx.VERTICAL)

        # adding stuff to the inputsizer, i.e. buttons checkboxes.. etc.
        inputSizer.Add(iterationLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.iteration, 0, wx.EXPAND, 2)

        inputSizer.Add(datapathLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.datapath, 0, wx.EXPAND, 2)
        inputSizer.Add(samplesLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.listSamples, 0, wx.EXPAND | wx.ALL, 2)
        inputSizer.Add(sampleSectionsLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.listSampleSections, 0, wx.EXPAND, 2)
        inputSizer.Add(self.choice_panel, 0 , wx.EXPAND, 2)

        # adding buttons
        buttonSizer.Add(self.buttonPlay, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonSpec, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonApplyActions, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonPrev, 0, wx.CENTER | wx.ALL, 15)
        buttonSizer.Add(self.buttonNext, 0, wx.CENTER | wx.ALL, 15)

        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonSizer, 0, wx.CENTER, 15)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

        # initialize the list of samples, list of sample section and action radio box
        self.samples = {}
        self.sampleSelected = None
        self.update_sample_list(None)

    def find_iterations(self):
        '''find the iterations given a config file.'''
        cfg = parse_yaml(self.config)
        iterations = [f for f in os.listdir(os.path.join(cfg['project_path'], 'dlc-models')) if 'iteration' in f]
        return iterations

    def force_numeric_int(self, event, edit):
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or keycode == 8:
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()

    def force_numeric_float(self, event, edit):
        raw_value = edit.GetValue().strip()
        keycode = event.GetKeyCode()
        if keycode < 255:
            # valid ASCII
            if chr(keycode).isdigit() or keycode == 8 or chr(keycode) == '.' and ('.' not in raw_value):
                event.Skip()
        if keycode == 314 or keycode == 316:
            event.Skip()

    def onPlay(self, event):
        video_paths = self.samples[self.sampleSelected]['video_paths']
        metadata_path = os.path.splitext(video_paths[self.listSampleSections.GetSelection()])[0] + '.npy'
        print('metadata path: ', metadata_path)
        frame = VideoFrame(self.GetParent(), config=self.config, video_path=metadata_path)
        frame.Show()

    def onShowSpec(self, event):
        freqs_r, time_r, spectrogram_r = self.samples[self.sampleSelected]['spectrogram_r']
        freqs_l, time_l, spectrogram_l = self.samples[self.sampleSelected]['spectrogram_l']
        plt.figure()
        plt.subplot(1,2,1)
        plt.pcolormesh(time_r, freqs_r, spectrogram_r, shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.colorbar()
        plt.title('Spectrogram \n Right side [power db]')
        plt.subplot(1,2,2)
        plt.pcolormesh(time_l, freqs_l, spectrogram_l, shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.colorbar()
        plt.title('Spectrogram \n Left side [power db]')
        plt.show()

    def onActionSelection(self, event):
        print(' new action selected: ', self.sampleSelected)
        if self.sampleSelected:
            action = from_action[self.action_rdb.GetSelection()]
            print('actions in sample>>>>> ', action)
            actions_in_sample = self.samples[self.sampleSelected]['actions']
            print(actions_in_sample)
            actions_in_sample[self.listSampleSections.GetSelection()] = action
            print('action ins sample end:', actions_in_sample)
            # updates in samples cached
            self.samples[self.sampleSelected]['actions'] = actions_in_sample

    def onSelectNewSection(self, event):
        print(' select a  new section self.sampleSelected: ', self.sampleSelected)
        if self.sampleSelected:
            current_action_str = self.samples[self.sampleSelected]['actions'][self.listSampleSections.GetSelection()]
            self.action_rdb.SetSelection(to_action[current_action_str])

    def onApplyCorrections(self, event):
        print('Applying corrections... ')
        for name , sample in self.samples.items():
            print('----> ', sample)
            actions = sample['actions']
            video_paths = sample['video_paths']
            metadata_paths = [os.path.splitext(vp)[0]+'.npy' for vp in video_paths]
            for a,v,m in zip(actions, video_paths, metadata_paths):
                if a != 'delete':
                    new_v = os.path.join(self.datapath.GetPath(), a, os.path.basename(v))
                    new_m = os.path.join(self.datapath.GetPath(), a, os.path.basename(m))
                    move(v, new_v)
                    move(m, new_m)
                else:
                    os.remove(v)
                    os.remove(m)
        self.Close()

    def onNext(self, event):
        print('next value in the selection')
        current_selection = self.listSampleSections.GetSelection()
        if current_selection+1< self.listSampleSections.GetCount():
            self.listSampleSections.SetSelection(current_selection+1)
            self.onSelectNewSection(None)

    def onPrev(self, event):
        print('prev value in the selection')
        current_selection = self.listSampleSections.GetSelection()
        if current_selection-1 >= 0 :
            self.listSampleSections.SetSelection(current_selection-1)
            self.onSelectNewSection(None)


    def get_samples(self):
        current_datapath = self.datapath.GetPath()
        videos =Path(current_datapath).rglob('whisker_clip_*.avi')
        samples = {}
        for v in videos:
            vname = v.name
            name = vname[len('whisker_clip_'): vname.rfind("_")]
            metadata = np.load(str(v.with_suffix('.npy')), allow_pickle=True)
            action = v.parent.name
            if not action in ['positive', 'negative']:
                print('skiping video: ', vname)
                continue
            if name in samples:
                # read data
                sample = samples[name]
                sample['n_samples'] += 1
                windows = sample['windows']
                actions = sample['actions']
                windows.append((metadata[()]['t0'], metadata[()]['t1'], metadata[()]['index0'], metadata[()]['index1']))
                actions.append(action)
                sample['video_paths'].append(v.resolve().absolute())
                sample['windows'] = windows
                sample['actions'] = actions
                samples[name] = sample
            else:
                windows = [(metadata[()]['t0'], metadata[()]['t1'], metadata[()]['index0'], metadata[()]['index1'])]
                samples[name] = {'n_samples': 1, 'windows': windows, 'spectrogram_r': metadata[()]['spectrogram_r'],
                                 'spectrogram_l': metadata[()]['spectrogram_l'], 'video_name': metadata[()]['video_name'],
                                 'actions': [action],  'video_paths': [v.resolve().absolute()]}
        return samples

    def update_sample_list(self, event):
        print('new sample list generated....')
        self.listSamples.DeleteAllItems()
        self.samples = self.get_samples()
        # if samples are found in the self.datapath widgets are populated and button enabled
        # otherwise disable buttons and clear old fields
        if len(self.samples)>0:
            for i, (name, sample) in enumerate(self.samples.items()):
                self.listSamples.InsertItem(i, str(i))
                self.listSamples.SetItem(i, 1, sample['video_name'])
                self.listSamples.SetItem(i, 2, str(sample['n_samples']))
            self.apply_sample_selection(0)
            if self.sampleSelected:
                self.buttonPrev.Enable(True)
                self.buttonNext.Enable(True)
                self.buttonPlay.Enable(True)
                self.buttonApplyActions.Enable(True)
                self.buttonSpec.Enable(True)
        else:
            self.buttonPrev.Enable(False)
            self.buttonNext.Enable(False)
            self.buttonPlay.Enable(False)
            self.buttonApplyActions.Enable(False)
            self.buttonSpec.Enable(False)
            self.action_rdb.Enable(False)

    def update_selected_sample(self, event):
        if self.listSamples.GetItemCount() > 0:
            selected_item = self.listSamples.GetFirstSelected()
            self.apply_sample_selection(selected_item)

    def apply_sample_selection(self, sample_selection_index):
        # gets the video name
        video_name = self.listSamples.GetItemText(sample_selection_index, col=1)
        print('video_name: ', video_name)
        self.sampleSelected = None
        # finds the sample hash name in the sample list/dict that has this video name
        for name, sample_values in self.samples.items():
            if sample_values['video_name'] == video_name:
                self.sampleSelected = name
                break
        # sample selected ins the hash and finds windodws and actions
        if self.sampleSelected:
            sections = [f'#{i} from {t0} to {t1}' for i, (t0, t1, ii0, ii1) in
                        enumerate(self.samples[self.sampleSelected]['windows'])]
            self.listSampleSections.SetItems(sections)
            self.listSampleSections.SetSelection(0)
            self.action_rdb.Enable(True)
            actions = self.samples[self.sampleSelected]['actions']
            self.action_rdb.SetSelection(to_action[actions[0]])
        else:
            print('Not samples found selection')

def show(config, startpath='.'):
    app = wx.App()
    frame = OscCorrections(None, startpath, config=config).Show()
    app.MainLoop()


if __name__ == '__main__':
    #config = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/config.yaml'
    config=r'D:\behaviorVids\projects-whisker\wtfree5ma-dlc2\wtfree5ma-agkuner-2021-06-25\config.yaml'
    startpath = os.getcwd()
    wd = Path(config).resolve().parents[0]
    os.chdir(str(wd))
    cfg = auxiliaryfunctions.read_config(config)
    show(config, startpath)