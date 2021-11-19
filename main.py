import subprocess
import webbrowser

from pathlib import Path

import wx
import wx.grid
from blockwindow import BlockWindow
import os

from gui.contact_model_generation import ContactModelGeneration
from gui.create_training_set import DLCCreateTrainingSet
from gui.evaluate_dlc_network import EvaluaterNetwork
from gui.extract_frames import ExtractFrames
from gui.osc_model_generation import OscModelGeneration
from gui.project_management import AddNewVideos, NewProjectFrame
from gui.training_dlc_network import TrainNetwork
from gui.utils import parse_yaml
from gui.utils.generic import find_yaml
from gui.utils.main_panel import MainPanel
from gui.video_analysis import AnalyzeVideos
from gui.whisker_detection import DetectWhiskers
from gui.whisker_label_toolbox import LabelWhiskersFrame
from gui.multi_whisker_label_toolbox import LabelWhiskersFrame as MultiLabelWhiskersFrame



print('importing deeplab cut..')

print('Done')

CWD = os.getcwd()


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(640, 500))
        self.mainPanel = MainPanel(self)
        topLbl = wx.StaticText(self.mainPanel, -1, "quick DLC")

        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # create main control elements
        # annotation
        box1, items = self.MakeStaticBoxSizer("Annotation",
                                              ['create new project',
                                               'add new videos',
                                               'extract frames',
                                               'detect whiskers',
                                               'label frames',
                                               'label whiskers',
                                               'check annotations'],
                                              size=(200, 25),
                                              type='button')
        items['create new project'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'create new project'))
        items['add new videos'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'add new videos'))
        items['extract frames'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'extract frames'))
        items['detect whiskers'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'detect whiskers'))
        items['label whiskers'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'label whiskers'))

        items['label frames'].Bind(wx.EVT_BUTTON, self.on_label_frames)
        items['check annotations'].Bind(wx.EVT_BUTTON, self.on_check_annotations)

        print(box1.GetChildren())

        # training
        box2, items = self.MakeStaticBoxSizer("Training",
                                              ['create training set', 'train network', 'evaluate network'],
                                              size=(200, 25),
                                              type='button')
        items['create training set'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'create training set'))
        items['train network'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'train network'))
        items['evaluate network'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'evaluate network'))

        # refinement
        box3, items = self.MakeStaticBoxSizer("Refinement",
                                              ['analyze videos', 'refine labels', 'merge datasets', 'create whisking model'],
                                              size=(200, 25),
                                              type='button')
        items['analyze videos'].Bind(wx.EVT_BUTTON, lambda event: self.on_new_frame(event, 'analyze videos'))
        items['refine labels'].Bind(wx.EVT_BUTTON, self.OnRefineLabels)
        items['merge datasets'].Bind(wx.EVT_BUTTON, self.OnMergeDataset)
        items['create whisking model'].Bind(wx.EVT_BUTTON, self.onCreateWhiskingModel)
        # config path selection:
        configPathLbl = wx.StaticText(self.mainPanel, -1, "Config path:", size=wx.Size(600, 25))
        cwd = find_yaml()
        self.configPath = wx.FilePickerCtrl(self.mainPanel, -1, cwd, wildcard='*.yaml')
        self.configPath.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_config_path_picked)
        self.startpath = os.getcwd()
        os.chdir(Path(cwd).parent.absolute())

        self.openConfigButton = wx.Button(self.mainPanel, -1, "open config")
        self.openConfigButton.Bind(wx.EVT_BUTTON, self.on_open_config)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.mainPanel), 0,
                      wx.EXPAND | wx.TOP, 5)

        # create a button sizer
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(box1, 0, wx.ALL, 10)
        buttonSizer.Add(box2, 0, wx.ALL, 10)
        buttonSizer.Add(box3, 0, wx.ALL, 10)

        # add button sizer to the main sizer
        mainSizer.Add(buttonSizer, 0, wx.CENTER | wx.TOP, 10)
        mainSizer.Add(configPathLbl, 0, wx.EXPAND | wx.TOP, 10)
        mainSizer.Add(self.configPath, 0, wx.EXPAND | wx.BOTTOM, 10)
        openConfigSizer = wx.BoxSizer(wx.HORIZONTAL)
        openConfigSizer.Add(self.openConfigButton)
        mainSizer.Add(openConfigSizer, 0, wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, 10)


        self.mainPanel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150, 25), type='block'):
        box = wx.StaticBox(self.mainPanel, -1, boxlabel)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        items = {}
        for label in itemlabels:
            if type == 'block':
                item = BlockWindow(self.mainPanel, label=label, size=size)
            elif type == 'button':
                item = wx.Button(self.mainPanel, label=label)
            else:
                item = BlockWindow(self.mainPanel, label=label, size=size)
            items[label] = item
            sizer.Add(item, 0, wx.EXPAND, 2)
        return sizer, items

    def on_open_config(self, event):
        config_path = self.configPath.GetPath()
        if config_path != "" and os.path.exists(config_path) and config_path.endswith(".yaml"):
            # For mac compatibility
            import platform
            if platform.system() == "Darwin":
                self.file_open_bool = subprocess.call(["open", config_path])
                self.file_open_bool = True
            else:
                self.file_open_bool = webbrowser.open(config_path)

            if self.file_open_bool:
                pass
            else:
                raise FileNotFoundError("Error while opening config.yaml file: " + str(config_path))

    def on_label_frames(self, event):
        print('opening dlc labeling tool box...')
        import deeplabcut as d
        config_path = self.configPath.GetPath()
        d.label_frames(config_path)
        print('Done')

    def on_check_annotations(self, event):
        print('check labels...')
        import deeplabcut as d
        config_path = self.configPath.GetPath()
        config = d.auxiliaryfunctions.read_config(config_path)
        if config.get('multianimalproject', False):
            d.check_labels(config_path, visualizeindividuals=True)
        d.check_labels(config_path, visualizeindividuals=False)
        print('Done')

    def on_new_frame(self, event, frame_type):
        if frame_type is None or len(frame_type) == 0:  # empty string:
            print('new frame not specified in button!! ')
            return
        elif frame_type == 'create new project':
            frame = NewProjectFrame(self.GetParent(), self, config=self.configPath.GetPath())
        elif frame_type == 'add new videos':
            frame = AddNewVideos(self.GetParent(), current_working_dir=CWD, config=self.configPath.GetPath())
        elif frame_type == 'extract frames':
            frame = ExtractFrames(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'detect whiskers':
            frame = DetectWhiskers(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'create training set':
            frame = DLCCreateTrainingSet(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'train network':
            frame = TrainNetwork(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'evaluate network':
            frame = EvaluaterNetwork(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'analyze videos':
            frame = AnalyzeVideos(self.GetParent(), config=self.configPath.GetPath())
        elif frame_type == 'label whiskers':
            config = parse_yaml(self.configPath.GetPath())
            if config.get('multianimalproject',False):
                frame = MultiLabelWhiskersFrame(self.GetParent(), config=self.configPath.GetPath(),config3d=None, sourceCam=None)
            else:
                frame = LabelWhiskersFrame(self.GetParent(), config=self.configPath.GetPath(), imtypes=["*.png"], config3d=None, sourceCam=None)



        else:
            return
        frame.Show()

    def OnRefineLabels(self, event):
        import deeplabcut as d
        d.refine_labels(self.configPath.GetPath())

    def OnMergeDataset(self, event):
        import deeplabcut as d
        d.merge_datasets(self.configPath.GetPath())

    def onCreateWhiskingModel(self, event):
        cfg = parse_yaml(self.configPath.GetPath())
        assert len(cfg.get('project_type', '')) >0, 'Project type is not configured please take care of your config.yaml'
        project_type = cfg['project_type']
        if project_type == 'contact':
            frame = ContactModelGeneration(self.Parent, self.startpath, config=self.configPath.GetPath())
        elif project_type in ['motion', 'whisking']:
            frame = OscModelGeneration(self.Parent, self.startpath, config=self.configPath.GetPath())
        else:
            raise Exception('Project type is not correct: ', project_type)
        frame.Show()

    def on_config_path_picked(self, event):
        print('===> on config path picked!! ')
        wd = Path(self.configPath.GetPath()).resolve().parents[0]
        os.chdir(str(wd))


# Object app
class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(parent=None, title='Quick DLC interface')
        self.frame.Show()
        # self.log = Log()
        # self.log.Show()
        return True


if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()
