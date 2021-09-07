import os
from pathlib import Path

import pandas as pd
import wx

from blockwindow import BlockWindow
from gui.utils import parse_yaml
from gui.utils.parse_yaml import extractTrainingIndexShuffle
from gui.utils.snapshot_index import get_snapshots
from main import MainPanel, parser_yaml, get_available_gpus, get_radiobutton_status


class EvaluaterNetwork(wx.Frame):
    def __init__(self, parent, title='Evaluate network', config=None):
        super(EvaluaterNetwork, self).__init__(parent, title=title, size=(640, 500))
        self.panel = MainPanel(self)
        self.WIDTHOFINPUTS = 400
        self.config = config
        config = parser_yaml(self.config)

        # # title in the panel
        topLbl = wx.StaticText(self.panel, -1, "Evaluate network")
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        # selection of iteration:
        cfg = parser_yaml(self.config)
        iterationLbl = wx.StaticText(self.panel, -1, "Iteration")
        current_iteration = 'iteration-' + str(cfg['iteration'])
        iterations = [current_iteration]
        iterations.extend([it for it in self.find_iterations() if it not in iterations])
        self.iteration = wx.Choice(self.panel, id=-1, choices=iterations)
        self.iteration.SetSelection(0)
        shuffleNumberLbl = wx.StaticText(self.panel, -1, "Shuffles")
        self.shuffleNumber = wx.Choice(self.panel, id=-1, choices=self.find_shuffles())
        self.shuffleNumber.SetSelection(0)
        self.iteration.Bind(wx.EVT_CHOICE, self.onSelectIteration)
        self.shuffleNumber.Bind(wx.EVT_CHOICE, self.onSelectShuffleNumber)


        plottingLbl = wx.StaticText(self.panel, -1, "Plotting")
        self.plotting = wx.CheckBox(self.panel, -1, "")
        self.plotting.SetValue(True)

        showErrorLbl = wx.StaticText(self.panel, -1, "Show error")
        self.showError = wx.CheckBox(self.panel, -1, "")
        self.showError.SetValue(False)

        comparisionBodyPartsLbl = wx.StaticText(self.panel, -1, "Comparision body parts")
        print(config['bodyparts'])
        print(len(config['bodyparts']))
        if config.get("multianimalproject", False):
            bodyparts = config["multianimalbodyparts"]
        else:
            bodyparts = config["bodyparts"]
        comparisionBodyParts, items = self.MakeStaticBoxSizer(boxlabel='body parts',
                                                              itemlabels=bodyparts + ['All'], type='checkBox')

        self.radioButtons = items
        self.radioButtonCurrentStatus = {}
        items['All'].SetValue(True)
        items['All'].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, 'All'))
        for k in items.keys():
            if not k == 'All':
                items[k].Bind(wx.EVT_CHECKBOX, lambda event: self.onRadioButton(event, ''))

        gpusAvailableLbl = wx.StaticText(self.panel, -1, "GPU available")
        self.gpusAvailable = wx.Choice(self.panel, id=-1, choices=['None'] + get_available_gpus())

        rescaleLbl = wx.StaticText(self.panel, -1, "Rescale")
        self.rescale = wx.CheckBox(self.panel, -1, "")
        self.rescale.SetValue(False)

        createMapsAllLbl = wx.StaticText(self.panel, -1, "Creat maps the whole test set (takes time..)")
        self.createMapsAll = wx.CheckBox(self.panel, -1, "")
        self.createMapsAll.SetValue(False)

        snapshotindexLbl = wx.StaticText(self.panel, -1, "Select best snapshot")

        self.snapshots = self.find_snapshots()
        self.snapshotindex = wx.Choice(self.panel, -1, choices=self.snapshots)

        # box of results:
        summaryLbl = wx.StaticText(self.panel, -1, "summaryLbl")
        self.summary = self.generate_summary()

        # button to evaluate netwrok
        buttonEvaluate = wx.Button(self.panel, label="Evaluate")
        buttonEvaluate.Bind(wx.EVT_BUTTON, self.evaluate_network)
        buttonCollect = wx.Button(self.panel, label="Collect results all")
        buttonCollect.Bind(wx.EVT_BUTTON, self.generate_collected_summary_csv)

        buttonConfig = wx.Button(self.panel, label="Write snapshot to config.yaml")
        buttonConfig.Bind(wx.EVT_BUTTON, self.onConfigSnapshot)

        buttonMaps = wx.Button(self.panel, label="Make test maps")
        buttonMaps.Bind(wx.EVT_BUTTON, self.on_create_test_map)

        # create the main sizer:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # add the label on the top of main sizer
        mainSizer.Add(topLbl, 0, wx.ALL, 5)
        mainSizer.Add(wx.StaticLine(self.panel), 0,
                      wx.EXPAND | wx.TOP, 5)

        mainSizer.Add(iterationLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.iteration, 0, wx.EXPAND, 2)
        mainSizer.Add(shuffleNumberLbl, 0, wx.EXPAND, 2)
        mainSizer.Add(self.shuffleNumber, 0, wx.EXPAND, 2)

        # all the stuff insider the
        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        # create inputs box... (name, experimenter, working dir and list of videos)
        inputSizer = wx.BoxSizer(wx.VERTICAL)
        inputSizer2 = wx.BoxSizer(wx.VERTICAL)
        inputSizer3 = wx.BoxSizer(wx.VERTICAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        # inputSizer.Add(selectionAlgoLbl, 0, wx.EXPAND, 2)
        # inputSizer.Add(selectionAlgo, 0, wx.EXPAND, 2)
        inputSizer.Add(plottingLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.plotting, 0, wx.EXPAND, 2)
        inputSizer.Add(showErrorLbl, 0, wx.EXPAND, 2)
        inputSizer.Add(self.showError, 0, wx.EXPAND, 2)

        inputSizer2.Add(comparisionBodyPartsLbl, 0, wx.EXPAND, 2)
        inputSizer2.Add(comparisionBodyParts, 0, wx.EXPAND, 2)
        inputSizer2.Add(snapshotindexLbl, 0, wx.ALIGN_LEFT | wx.ALL, 2 )
        inputSizer2.Add(self.snapshotindex, 0, wx.ALIGN_LEFT | wx.ALL, 2)

        inputSizer3.Add(gpusAvailableLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.gpusAvailable, 0, wx.EXPAND, 2)
        inputSizer3.Add(rescaleLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.rescale, 0, wx.EXPAND, 2)
        inputSizer3.Add(createMapsAllLbl, 0, wx.EXPAND, 2)
        inputSizer3.Add(self.createMapsAll, 0, wx.EXPAND, 2)

        buttonSizer.Add(buttonEvaluate, 0, wx.CENTER | wx.ALL, 4)
        buttonSizer.Add(buttonCollect, 0, wx.CENTER | wx.ALL, 4)
        buttonSizer.Add(buttonConfig, 0, wx.CENTER |  wx.ALL, 4)
        buttonSizer.Add(buttonMaps, 0, wx.CENTER | wx.ALL, 4)
        # at the end of the add to the stuff sizer
        contentSizer.Add(inputSizer, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer2, 0, wx.ALL, 10)
        contentSizer.Add(inputSizer3, 0, wx.ALL, 10)

        # contentSizer.Add(buttonSizer,0,wx.ALL, 10)

        # adding to the main sizer all the two groups
        mainSizer.Add(summaryLbl, 0, wx.EXPAND | wx.ALL, 2)
        mainSizer.Add(self.summary, 0, wx.ALL, 2)
        mainSizer.Add(contentSizer, 0, wx.TOP | wx.EXPAND, 15)
        mainSizer.Add(buttonSizer, 0, wx.BOTTOM | wx.CENTER, 15)

        # mainSizer.Add(rightSizer, 0, wx.ALL, 10)

        # sizer fit and fix
        self.panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)  # Main window

    def evaluate_network(self, event):
        bodyParts = get_radiobutton_status(self.radioButtons)
        print(bodyParts)

        import deeplabcut as d
        gputouse = None if self.gpusAvailable.GetStringSelection() == 'None' else self.gpusAvailable.GetSelection()
        shuffleNumString = self.shuffleNumber.GetStringSelection()
        trainingIndex, shuffleNum = extractTrainingIndexShuffle(self.config, shuffleNumString )

        d.evaluate_network(self.config, trainingsetindex=trainingIndex, Shuffles=[shuffleNum] ,plotting=self.plotting.GetValue(),
                           show_errors=self.showError.GetValue(), comparisonbodyparts=bodyParts, gputouse=gputouse,
                           rescale=self.rescale.GetValue())
        self.Close()

    def on_create_test_map(self, event):
        import deeplabcut as d
        if self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()) == 'None':
            gputouse = None
        else:
            gputouse = int(self.gpusAvailable.GetString(self.gpusAvailable.GetCurrentSelection()))

        trainindex, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffleNumber.GetStringSelection())
        if self.createMapsAll.GetValue():
            print('Creating maps for all samples in the training/test set.. this will take a while....')
            d.extract_save_all_maps(self.config,shuffle_number, trainindex, gputouse=gputouse)
        else:
            print('Creating maps for three samples (0, 5 and 10). Check evaluation_results folder')
            d.extract_save_all_maps(self.config,shuffle_number, trainindex, gputouse=gputouse, Indices=[0,5,10])


    def MakeStaticBoxSizer(self, boxlabel, itemlabels, size=(150, 25), type='block'):
        box = wx.StaticBox(self.panel, -1, boxlabel)

        h_sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        items = {}
        print(itemlabels)
        for i in range(len(itemlabels) // 10 + 1):
            # for groups of 10 items create a sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            for j in range(10):
                if 10 * i + j == len(itemlabels):
                    break
                label = itemlabels[10 * i + j]
                if type == 'block':
                    item = BlockWindow(self.panel, label=label, size=size)
                elif type == 'button':
                    item = wx.Button(self.panel, label=label)
                elif type == 'radioButton':
                    item = wx.RadioButton(self.panel, label=label, size=size)
                elif type == 'checkBox':
                    item = wx.CheckBox(self.panel, -1, label=label)
                else:
                    item = BlockWindow(self.panel, label=label, size=size)
                items[label] = item
                sizer.Add(item, 0, wx.EXPAND, 2)
            h_sizer.Add(sizer, 0, wx.EXPAND, 2)
        return h_sizer, items

    def find_iterations(self):
        '''find the iterations given a config file.'''
        config = parse_yaml(self.config)
        print(" evaluation results: ", os.path.join(config['project_path'], 'evaluation_results'))
        if os.path.exists(os.path.join(config['project_path'], 'evaluation_results')):
            return os.listdir(os.path.join(config['project_path'], 'evaluation_results'))
        else:
            return ['']

    def find_shuffles(self):
        config = parse_yaml(self.config)
        iteration_selection = self.iteration.GetStringSelection()
        files = [ f for f in os.listdir(os.path.join(config['project_path'], 'dlc-models', iteration_selection))if not f.startswith('.') and 'contact-model' not in f and 'whisking-model' not in f and 'motion-model' not in f and 'osc-model' not in f]
        return files

    def find_snapshots(self):
        training_index, shuffle_number = extractTrainingIndexShuffle(self.config, self.shuffleNumber.GetStringSelection())
        return get_snapshots(self.config, shuffle_number, training_index).tolist() + ['latest', 'all']


    def onSelectIteration(self, event):
        self.shuffleNumber.SetItems(self.find_shuffles())
        self.shuffleNumber.SetSelection(0)
        self.onSelectShuffleNumber(None)

    def onSelectShuffleNumber(self, event):
        self.snapshots = self.find_snapshots()
        self.snapshotindex.SetItems(self.snapshots)
        self.snapshotindex.SetSelection(0)

    def onRadioButton(self, event, source):
        if source == 'All':
            for i, k in enumerate(self.radioButtons.keys()):
                self.radioButtons[k].SetValue(False)
            self.radioButtons['All'].SetValue(True)
        else:
            self.radioButtons['All'].SetValue(False)
    def onConfigSnapshot(self, event):
        import deeplabcut as dlc
        snapshotindex = self.snapshotindex.GetSelection()
        if self.snapshotindex.GetStringSelection() == 'latest':
            snapshotindex = -1
        dlc.auxiliaryfunctions.edit_config(self.config, {'snapshotindex': snapshotindex})

    def generate_collected_summary_csv(self, event):
        cfg = parse_yaml(self.config)
        path_to_csv = os.path.join(cfg['project_path'], 'evaluation-results',
                                       'summary-all-results.csv')
        summary = None
        for f in Path(os.path.join(cfg['project_path'], 'evaluation-results')).rglob('DLC*.csv'):
            fname = f.name
            net_type = fname.split('_')[1]
            snapshot = fname.split('_')[-1]
            snapshot = snapshot[:snapshot.index('-results')]
            results = pd.read_csv(f.resolve().absolute(), index_col=0)
            results['net_type'] = [net_type] * len(results.index)
            results['snapshot'] = ['snapshot-' + snapshot] * len(results.index)
            results['iteration'] = [f.parent.parent.name] * len(results.index)


            if summary is None:
                summary = results
            else:
                summary = summary.append(results, ignore_index=True)
        summary.to_csv(path_to_csv)
        print('Summary of all files generated in :', path_to_csv,'\n \[\033[32m\]USE THIS SUMMARY TO CONFIGURE YOUR CONFIG.YAML\[\033[m\]')

    def generate_summary(self):

        # READING VALUES:
        cfg = parse_yaml(self.config)
        iteration_selection = self.iteration.GetStringSelection()
        # for example: "[proj-path]/evaluation-results/iteration-0/CombinedEvaluation-results.csv"
        try:
            path_to_csv = os.path.join(cfg['project_path'], 'evaluation-results', iteration_selection, 'CombinedEvaluation-results.csv')
            results = pd.read_csv(path_to_csv, index_col=0)
            columns = results.columns
        except FileNotFoundError as e:
            print(e)
            print('Making empty results table')
            columns = ['Training iterations', '%Training dataset', 'Shuffle number', 'Train error(px)',
                       'Test error(px)',
                       'p-cutoff', 'used', 'Train error with p-cutoff', 'Test error with p-cutoff']
            results = None
        # Create a wxGrid object
        grid = wx.grid.Grid(self.panel, -1)

        # Then we call CreateGrid to set the dimensions of the grid

        grid.CreateGrid(1, len(columns))
        for i, c in enumerate(columns):
            grid.SetColLabelValue(i, c)
        grid.SetRowLabelSize(0)

        if results is not None:
            print('results.ndim = ', results.ndim)
            for j, row in results.iterrows():
                for i, c in enumerate(columns):
                    try:
                        float(str(row[c]))
                        grid.SetColFormatFloat(j, i, 2)
                    except:
                        pass
                    grid.SetCellValue(j, i, str(row[c]))
                    grid.SetReadOnly(j,i)
                print('grid.GetNumberRows() = ', grid.GetNumberRows())
                if j+1 == grid.GetNumberRows() and j+1< len(results):
                    grid.AppendRows()



        # # And set grid cell contents as strings
        # grid.SetCellValue(0, 0, 'wxGrid is good')
        #
        # # We can specify that some cells are read.only
        # grid.SetCellValue(0, 3, 'This is read.only')
        # grid.SetReadOnly(0, 3)
        #
        # # Colours can be specified for grid cell contents
        # grid.SetCellValue(3, 3, 'green on grey')
        # grid.SetCellTextColour(3, 3, wx.GREEN)
        # grid.SetCellBackgroundColour(3, 3, wx.LIGHT_GREY)
        #
        # # We can specify the some cells will store numeric
        # # values rather than strings. Here we set grid column 5
        # # to hold floating point values displayed with width of 6
        # # and precision of 2
        # grid.SetColFormatFloat(5, 6, 2)
        # grid.SetCellValue(0, 6, '3.1415')
        # sizer = wx.BoxSizer(grid, wx.VERTICAL)
        # sizer.Add(grid, 1, wx.EXPAND, 2)
        grid.AutoSize()
        return grid