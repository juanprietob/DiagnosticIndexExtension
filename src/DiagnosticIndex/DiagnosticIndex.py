import os, sys
import csv
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from types import *
import math
import shutil


class DiagnosticIndex(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        parent.title = "DiagnosticIndex"
        parent.categories = ["Quantification"]
        parent.dependencies = []
        parent.contributors = ["Laura PASCAL (UofM)"]
        parent.helpText = """
            """
        parent.acknowledgementText = """
            This work was supported by the National
            Institutes of Dental and Craniofacial Research
            and Biomedical Imaging and Bioengineering of
            the National Institutes of Health under Award
            Number R01DE024450.
            """


class DiagnosticIndexWidget(ScriptedLoadableModuleWidget):
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # ---- Widget Setup ----

        # Global Variables
        self.logic = DiagnosticIndexLogic(self)
        self.dictVTKFiles = dict()
        self.dictGroups = dict()
        self.dictCSVFile = dict()
        self.directoryList = list()
        self.groupSelected = set()
        self.dictShapeModels = dict()
        self.patientList = list()
        self.dictResult = dict()

        # Interface
        loader = qt.QUiLoader()
        self.moduleName = 'DiagnosticIndex'
        scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        path = os.path.join(scriptedModulesPath, 'Resources', 'UI', '%s.ui' % self.moduleName)
        qfile = qt.QFile(path)
        qfile.open(qt.QFile.ReadOnly)

        widget = loader.load(qfile, self.parent)
        self.layout = self.parent.layout()
        self.widget = widget
        self.layout.addWidget(widget)

        #     global variables of the Interface:
        #          Tab: Creation of CSV File for Classification Groups
        self.collapsibleButton_creationCSVFile = self.logic.get('CollapsibleButton_creationCSVFile')
        self.spinBox_group = self.logic.get('spinBox_group')
        self.directoryButton_creationCSVFile = self.logic.get('DirectoryButton_creationCSVFile')
        self.stackedWidget_manageGroup = self.logic.get('stackedWidget_manageGroup')
        self.pushButton_addGroup = self.logic.get('pushButton_addGroup')
        self.pushButton_removeGroup = self.logic.get('pushButton_removeGroup')
        self.pushButton_modifyGroup = self.logic.get('pushButton_modifyGroup')
        self.directoryButton_exportCSVFile = self.logic.get('DirectoryButton_exportCSVFile')
        self.pushButton_exportCSVfile = self.logic.get('pushButton_exportCSVfile')
        #          Tab: Creation of New Classification Groups
        self.collapsibleButton_creationClassificationGroups = self.logic.get('CollapsibleButton_creationClassificationGroups')
        self.pathLineEdit_NewGroups = self.logic.get('PathLineEdit_NewGroups')
        self.collapsibleGroupBox_previewVTKFiles = self.logic.get('CollapsibleGroupBox_previewVTKFiles')
        self.checkableComboBox_ChoiceOfGroup = self.logic.get('CheckableComboBox_ChoiceOfGroup')
        self.tableWidget_VTKFiles = self.logic.get('tableWidget_VTKFiles')
        self.pushButton_previewVTKFiles = self.logic.get('pushButton_previewVTKFiles')
        self.pushButton_compute = self.logic.get('pushButton_compute')
        self.directoryButton_exportNewClassification = self.logic.get('DirectoryButton_exportNewClassification')
        self.pushButton_exportNewClassification = self.logic.get('pushButton_exportNewClassification')
        #          Tab: Selection Classification Groups
        self.collapsibleButton_SelectClassificationGroups = self.logic.get('CollapsibleButton_SelectClassificationGroups')
        self.pathLineEdit_selectionClassificationGroups = self.logic.get('PathLineEdit_selectionClassificationGroups')
        self.spinBox_healthyGroup = self.logic.get('spinBox_healthyGroup')
        #          Tab: Preview of Classification Groups
        self.collapsibleButton_previewClassificationGroups = self.logic.get('CollapsibleButton_previewClassificationGroups')
        self.pushButton_previewGroups = self.logic.get('pushButton_previewGroups')
        self.MRMLTreeView_classificationGroups = self.logic.get('MRMLTreeView_classificationGroups')
        #          Tab: Select Input Data
        self.collapsibleButton_selectInputData = self.logic.get('CollapsibleButton_selectInputData')
        self.MRMLNodeComboBox_VTKInputData = self.logic.get('MRMLNodeComboBox_VTKInputData')
        self.pathLineEdit_CSVInputData = self.logic.get('PathLineEdit_CSVInputData')
        self.checkBox_fileInGroups = self.logic.get('checkBox_fileInGroups')
        self.pushButton_applyOAIndex = self.logic.get('pushButton_applyOAIndex')
        #          Tab: Result / Analysis
        self.collapsibleButton_Result = self.logic.get('CollapsibleButton_Result')
        self.tableWidget_result = self.logic.get('tableWidget_result')
        self.pushButton_exportResult = self.logic.get('pushButton_exportResult')
        self.directoryButton_exportResult = self.logic.get('DirectoryButton_exportResult')

        # Widget Configuration

        #     disable/enable and hide/show widget
        self.spinBox_healthyGroup.setDisabled(True)
        self.pushButton_previewGroups.setDisabled(True)
        self.pushButton_compute.setDisabled(True)
        self.pushButton_compute.setDisabled(True)
        self.directoryButton_exportNewClassification.setDisabled(True)
        self.pushButton_exportNewClassification.setDisabled(True)
        self.checkBox_fileInGroups.setDisabled(True)
        self.checkableComboBox_ChoiceOfGroup.setDisabled(True)
        self.tableWidget_VTKFiles.setDisabled(True)
        self.pushButton_previewVTKFiles.setDisabled(True)

        #     qMRMLNodeComboBox configuration
        self.MRMLNodeComboBox_VTKInputData.setMRMLScene(slicer.mrmlScene)

        #     initialisation of the stackedWidget to display the button "add group"
        self.stackedWidget_manageGroup.setCurrentIndex(0)

        #     spinbox configuration in the tab "Creation of CSV File for Classification Groups"
        self.spinBox_group.setMinimum(1)
        self.spinBox_group.setMaximum(1)
        self.spinBox_group.setValue(1)

        #     tree view configuration
        headerTreeView = self.MRMLTreeView_classificationGroups.header()
        headerTreeView.setVisible(False)
        self.MRMLTreeView_classificationGroups.setMRMLScene(slicer.app.mrmlScene())
        self.MRMLTreeView_classificationGroups.sortFilterProxyModel().nodeTypes = ['vtkMRMLModelNode']
        self.MRMLTreeView_classificationGroups.setDisabled(True)
        sceneModel = self.MRMLTreeView_classificationGroups.sceneModel()
        # sceneModel.setHorizontalHeaderLabels(["Group Classification"])
        sceneModel.colorColumn = 1
        sceneModel.opacityColumn = 2
        headerTreeView.setStretchLastSection(False)
        headerTreeView.setResizeMode(sceneModel.nameColumn,qt.QHeaderView.Stretch)
        headerTreeView.setResizeMode(sceneModel.colorColumn,qt.QHeaderView.ResizeToContents)
        headerTreeView.setResizeMode(sceneModel.opacityColumn,qt.QHeaderView.ResizeToContents)

        #     configuration of the table for preview VTK file
        self.tableWidget_VTKFiles.setColumnCount(4)
        self.tableWidget_VTKFiles.setHorizontalHeaderLabels([' VTK files ', ' Group ', ' Visualization ', 'Color'])
        self.tableWidget_VTKFiles.setColumnWidth(0, 200)
        horizontalHeader = self.tableWidget_VTKFiles.horizontalHeader()
        horizontalHeader.setStretchLastSection(False)
        horizontalHeader.setResizeMode(0,qt.QHeaderView.Stretch)
        horizontalHeader.setResizeMode(1,qt.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(2,qt.QHeaderView.ResizeToContents)
        horizontalHeader.setResizeMode(3,qt.QHeaderView.ResizeToContents)
        self.tableWidget_VTKFiles.verticalHeader().setVisible(False)

        # --------------------------------------------------------- #
        #                       Connection                          #
        # --------------------------------------------------------- #
        #          Tab: Creation of CSV File for Classification Groups
        self.collapsibleButton_creationCSVFile.connect('clicked()',
                                                       lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_creationCSVFile))
        self.spinBox_group.connect('valueChanged(int)', self.onManageGroup)
        self.pushButton_addGroup.connect('clicked()', self.onAddGroupForCreationCSVFile)
        self.pushButton_removeGroup.connect('clicked()', self.onRemoveGroupForCreationCSVFile)
        self.pushButton_modifyGroup.connect('clicked()', self.onModifyGroupForCreationCSVFile)
        self.pushButton_exportCSVfile.connect('clicked()', self.onExportForCreationCSVFile)
        #          Tab: Creation of New Classification Groups
        self.collapsibleButton_creationClassificationGroups.connect('clicked()',
                                                                    lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_creationClassificationGroups))
        self.pathLineEdit_NewGroups.connect('currentPathChanged(const QString)', self.onNewGroups)
        self.checkableComboBox_ChoiceOfGroup.connect('checkedIndexesChanged()', self.onCheckableComboBoxValueChanged)
        self.pushButton_previewVTKFiles.connect('clicked()', self.onPreviewVTKFiles)
        self.pushButton_compute.connect('clicked()', self.onComputeNewClassificationGroups)
        self.pushButton_exportNewClassification.connect('clicked()', self.onExportNewClassificationGroups)
        #          Tab: Selection of Classification Groups
        self.collapsibleButton_SelectClassificationGroups.connect('clicked()',
                                                                  lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_SelectClassificationGroups))
        self.pathLineEdit_selectionClassificationGroups.connect('currentPathChanged(const QString)', self.onSelectionClassificationGroups)
        #          Tab: Preview of Classification Groups
        self.collapsibleButton_previewClassificationGroups.connect('clicked()',
                                                                   lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_previewClassificationGroups))
        self.pushButton_previewGroups.connect('clicked()', self.onPreviewClassificationGroups)
        #          Tab: Select Input Data
        self.collapsibleButton_selectInputData.connect('clicked()',
                                                       lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_selectInputData))
        self.MRMLNodeComboBox_VTKInputData.connect('currentNodeChanged(vtkMRMLNode*)', self.onVTKInputData)
        self.checkBox_fileInGroups.connect('clicked()', self.onCheckFileInGroups)
        self.pathLineEdit_CSVInputData.connect('currentPathChanged(const QString)', self.onCSVInputData)
        self.pushButton_applyOAIndex.connect('clicked()', self.onComputeOAIndex)
        #          Tab: Result / Analysis
        self.collapsibleButton_Result.connect('clicked()',
                                              lambda: self.onSelectedCollapsibleButtonOpen(self.collapsibleButton_Result))
        self.pushButton_exportResult.connect('clicked()', self.onExportResult)

        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.onCloseScene)

    # function called each time that the user "enter" in Diagnostic Index interface
    def enter(self):
        #TODO
        pass

    # function called each time that the user "exit" in Diagnostic Index interface
    def exit(self):
        #TODO
        pass

    # function called each time that the scene is closed (if Diagnostic Index has been initialized)
    def onCloseScene(self, obj, event):
        #TODO
        pass

    # Only one tab can be display at the same time:
    #   When one tab is opened all the other tabs are closed
    def onSelectedCollapsibleButtonOpen(self, selectedCollapsibleButton):
        if selectedCollapsibleButton.isChecked():
            collapsibleButtonList = [self.collapsibleButton_creationCSVFile,
                                     self.collapsibleButton_creationClassificationGroups,
                                     self.collapsibleButton_SelectClassificationGroups,
                                     self.collapsibleButton_previewClassificationGroups,
                                     self.collapsibleButton_selectInputData,
                                     self.collapsibleButton_Result]
            for collapsibleButton in collapsibleButtonList:
                collapsibleButton.setChecked(False)
            selectedCollapsibleButton.setChecked(True)

    # ---------------------------------------------------- #
    # Tab: Creation of CSV File for Classification Groups  #
    # ---------------------------------------------------- #

    # Function in order to manage the display of these three buttons:
    #    - "Add Group"
    #    - "Modify Group"
    #    - "Remove Group"
    def onManageGroup(self):
        # Display the button:
        #     - "Add Group" for a group which hasn't been added yet
        #     - "Remove Group" for the last group added
        #     - "Modify Group" for all the groups added
        if self.spinBox_group.maximum == self.spinBox_group.value:
            self.stackedWidget_manageGroup.setCurrentIndex(0)
        else:
            self.stackedWidget_manageGroup.setCurrentIndex(1)
            if (self.spinBox_group.maximum - 1) == self.spinBox_group.value:
                self.pushButton_removeGroup.show()
            else:
                self.pushButton_removeGroup.hide()
            # Update the path of the directory button
            if len(self.directoryList) > 0:
                self.directoryButton_creationCSVFile.directory = self.directoryList[self.spinBox_group.value - 1]

    # Function to add a group of the dictionary
    #    - Add the paths of all the vtk files found in the directory given
    #      of a dictionary which will be used to create the CSV file
    def onAddGroupForCreationCSVFile(self):
        # Error message
        directory = self.directoryButton_creationCSVFile.directory.encode('utf-8')
        if directory in self.directoryList:
            index = self.directoryList.index(directory) + 1
            slicer.util.errorDisplay('Path of directory already used for the group ' + str(index))
            return

        # Add the paths of vtk files of the dictionary
        self.logic.addGroupToDictionary(self.dictCSVFile, directory, self.directoryList, self.spinBox_group.value)
        condition = self.logic.checkSeveralMeshInDict(self.dictCSVFile)

        if not condition:
            # Remove the paths of vtk files of the dictionary
            self.logic.removeGroupToDictionary(self.dictCSVFile, self.directoryList, self.spinBox_group.value)
            return

        # Increment of the number of the group in the spinbox
        self.spinBox_group.blockSignals(True)
        self.spinBox_group.setMaximum(self.spinBox_group.value + 1)
        self.spinBox_group.setValue(self.spinBox_group.value + 1)
        self.spinBox_group.blockSignals(False)

        # Message for the user
        slicer.util.delayDisplay("Group Added")

    # Function to remove a group of the dictionary
    #    - Remove the paths of all the vtk files corresponding to the selected group
    #      of the dictionary which will be used to create the CSV file
    def onRemoveGroupForCreationCSVFile(self):
        # Remove the paths of the vtk files of the dictionary
        self.logic.removeGroupToDictionary(self.dictCSVFile, self.directoryList, self.spinBox_group.value)

        # Decrement of the number of the group in the spinbox
        self.spinBox_group.blockSignals(True)
        self.spinBox_group.setMaximum(self.spinBox_group.maximum - 1)
        self.spinBox_group.blockSignals(False)

        # Change the buttons "remove group" and "modify group" in "add group"
        self.stackedWidget_manageGroup.setCurrentIndex(0)

        # Message for the user
        slicer.util.delayDisplay("Group removed")

    # Function to modify a group of the dictionary:
    #    - Remove of the dictionary the paths of all vtk files corresponding to the selected group
    #    - Add of the dictionary the new paths of all the vtk files
    def onModifyGroupForCreationCSVFile(self):
        # Error message
        directory = self.directoryButton_creationCSVFile.directory.encode('utf-8')
        if directory in self.directoryList:
            index = self.directoryList.index(directory) + 1
            slicer.util.errorDisplay('Path of directory already used for the group ' + str(index))
            return

        # Remove the paths of vtk files of the dictionary
        self.logic.removeGroupToDictionary(self.dictCSVFile, self.directoryList, self.spinBox_group.value)

        # Add the paths of vtk files of the dictionary
        self.logic.addGroupToDictionary(self.dictCSVFile, directory, self.directoryList, self.spinBox_group.value)

        # Message for the user
        slicer.util.delayDisplay("Group modified")

    # Function to export the CSV file in the directory chosen by the user
    #    - Save the CSV file from the dictionary previously filled
    #    - Load automatically this CSV file in the next tab: "Creation of New Classification Groups"
    def onExportForCreationCSVFile(self):
        # Path of the csv file
        directory = self.directoryButton_exportCSVFile.directory.encode('utf-8')
        basename = 'Groups.csv'
        filepath = directory + "/" + basename

        # Message if the csv file already exists
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        if os.path.exists(filepath):
            messageBox.setText('File ' + filepath + ' already exists!')
            messageBox.setInformativeText('Do you want to replace it ?')
            messageBox.setStandardButtons( messageBox.No | messageBox.Yes)
            choice = messageBox.exec_()
            if choice == messageBox.No:
                return

        # Save the CSV File
        self.logic.creationCSVFile(directory, basename, self.dictCSVFile, "Groups")

        # Re-Initialization of the first tab
        self.spinBox_group.setMaximum(1)
        self.spinBox_group.setValue(1)
        self.stackedWidget_manageGroup.setCurrentIndex(0)
        self.directoryButton_creationCSVFile.directory = qt.QDir.homePath() + '/Desktop'
        self.directoryButton_exportCSVFile.directory = qt.QDir.homePath() + '/Desktop'

        # Re-Initialization of:
        #     - the dictionary containing all the paths of the vtk groups
        #     - the list containing all the paths of the different directories
        self.directoryList = list()
        self.dictCSVFile = dict()

        # Message in the python console
        print "Export CSV File: " + filepath

        # Load automatically the CSV file in the pathline in the next tab "Creation of New Classification Groups"
        self.pathLineEdit_NewGroups.setCurrentPath(filepath)

    # ---------------------------------------------------- #
    #     Tab: Creation of New Classification Groups       #
    # ---------------------------------------------------- #

    # Function to read the CSV file containing all the vtk filepaths needed to create the new Classification Groups
    def onNewGroups(self):
        # Re-initialization of the dictionary containing all the vtk files
        # which will be used to create a new Classification Groups
        self.dictVTKFiles = dict()

        # Check if the path exists:
        if not os.path.exists(self.pathLineEdit_NewGroups.currentPath):
            return

        print "------ Creation of a new Classification Groups ------"

        # Check if it's a CSV file
        condition1 = self.logic.checkExtension(self.pathLineEdit_NewGroups.currentPath, ".csv")
        if not condition1:
            self.pathLineEdit_NewGroups.setCurrentPath(" ")
            return

        # Download the CSV file
        self.logic.table = self.logic.readCSVFile(self.pathLineEdit_NewGroups.currentPath)
        condition2 = self.logic.creationDictVTKFiles(self.dictVTKFiles)
        condition3 = self.logic.checkSeveralMeshInDict(self.dictVTKFiles)

        # If the file is not conformed:
        #    Re-initialization of the dictionary containing all the data
        #    which will be used to create a new Classification Groups
        if not (condition2 and condition3):
            self.dictVTKFiles = dict()
            self.pathLineEdit_NewGroups.setCurrentPath(" ")
            return

        # Fill the table for the preview of the vtk files in Shape Population Viewer
        self.logic.fillTableForPreviewVTKFilesInSPV(self.dictVTKFiles,
                                               self.checkableComboBox_ChoiceOfGroup,
                                               self.tableWidget_VTKFiles)

        # Enable/disable buttons
        self.checkableComboBox_ChoiceOfGroup.setEnabled(True)
        self.tableWidget_VTKFiles.setEnabled(True)
        self.pushButton_previewVTKFiles.setEnabled(True)
        self.pushButton_compute.setEnabled(True)

    # Function to manage the checkable combobox to allow the user to choose the group that he wants to preview in SPV
    def onCheckableComboBoxValueChanged(self):
        # Update the checkboxes in the qtableWidget of each vtk file
        index = self.checkableComboBox_ChoiceOfGroup.currentIndex
        for row in range(0,self.tableWidget_VTKFiles.rowCount):
            # Recovery of the group of the vtk file contained in the combobox (column 2)
            widget = self.tableWidget_VTKFiles.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1
            if group == (index + 1):
                # check the checkBox
                widget = self.tableWidget_VTKFiles.cellWidget(row, 2)
                tuple = widget.children()
                checkBox = tuple[1]
                checkBox.blockSignals(True)
                item = self.checkableComboBox_ChoiceOfGroup.model().item(index, 0)
                if item.checkState():
                    checkBox.setChecked(True)
                    self.groupSelected.add(index + 1)
                else:
                    checkBox.setChecked(False)
                    self.groupSelected.discard(index + 1)
                checkBox.blockSignals(False)

        # Update the color in the qtableWidget of each vtk file
        colorTransferFunction = self.logic.creationColorTransfer(self.groupSelected)
        self.updateColorInTableForPreviewInSPV(colorTransferFunction)

    # Function to manage the combobox which allow the user to change the group of a vtk file
    def onGroupValueChanged(self):
        # Updade the dictionary which containing the VTK files sorted by groups
        self.logic.onComboBoxTableValueChanged(self.dictVTKFiles, self.tableWidget_VTKFiles)

        # Update the checkable combobox which display the groups selected to preview them in SPV
        self.onCheckBoxTableValueChanged()

    # Function to manage the checkbox in the table used to make a preview in SPV
    def onCheckBoxTableValueChanged(self):
        self.groupSelected = set()
        # Update the checkable comboBox which allow to select what groups the user wants to display in SPV
        self.checkableComboBox_ChoiceOfGroup.blockSignals(True)
        allcheck = True
        for key, value in self.dictVTKFiles.items():
            item = self.checkableComboBox_ChoiceOfGroup.model().item(key - 1, 0)
            if not value == []:
                for vtkFile in value:
                    filename = os.path.basename(vtkFile)
                    for row in range(0,self.tableWidget_VTKFiles.rowCount):
                        qlabel = self.tableWidget_VTKFiles.cellWidget(row, 0)
                        if qlabel.text == filename:
                            widget = self.tableWidget_VTKFiles.cellWidget(row, 2)
                            tuple = widget.children()
                            checkBox = tuple[1]
                            if not checkBox.checkState():
                                allcheck = False
                                item.setCheckState(0)
                            else:
                                self.groupSelected.add(key)
                if allcheck:
                    item.setCheckState(2)
            else:
                item.setCheckState(0)
            allcheck = True
        self.checkableComboBox_ChoiceOfGroup.blockSignals(False)

        # Update the color in the qtableWidget which will display in SPV
        colorTransferFunction = self.logic.creationColorTransfer(self.groupSelected)
        self.updateColorInTableForPreviewInSPV(colorTransferFunction)

    # Function to update the colors that the selected vtk files will have in Shape Population Viewer
    def updateColorInTableForPreviewInSPV(self, colorTransferFunction):
        for row in range(0,self.tableWidget_VTKFiles.rowCount):
            # Recovery of the group display in the table for each vtk file
            widget = self.tableWidget_VTKFiles.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1

            # Recovery of the checkbox for each vtk file
            widget = self.tableWidget_VTKFiles.cellWidget(row, 2)
            tuple = widget.children()
            checkBox = qt.QCheckBox()
            checkBox = tuple[1]

            # If the checkbox is check, the color is found thanks to the color transfer function
            # Else the color is put at white
            if checkBox.isChecked():
                rgb = colorTransferFunction.GetColor(group)
                widget = self.tableWidget_VTKFiles.cellWidget(row, 3)
                self.tableWidget_VTKFiles.item(row,3).setBackground(qt.QColor(rgb[0]*255,rgb[1]*255,rgb[2]*255))
            else:
                self.tableWidget_VTKFiles.item(row,3).setBackground(qt.QColor(255,255,255))

    # Function to display the selected vtk files in Shape Population Viewer
    #    - Add a color map "DisplayClassificationGroup"
    #    - Launch the CLI ShapePopulationViewer
    def onPreviewVTKFiles(self):
        print "--- Preview VTK Files in ShapePopulationViewer ---"
        if os.path.exists(self.pathLineEdit_NewGroups.currentPath):
            # Creation of a color map to visualize each group with a different color in ShapePopulationViewer
            self.logic.addColorMap(self.tableWidget_VTKFiles, self.dictVTKFiles)

            # Creation of a CSV file to load the vtk files in ShapePopulationViewer
            filePathCSV = slicer.app.temporaryPath + '/' + 'VTKFilesPreview_OAIndex.csv'
            self.logic.creationCSVFileForSPV(filePathCSV, self.tableWidget_VTKFiles, self.dictVTKFiles)

            # Launch the CLI ShapePopulationViewer
            parameters = {}
            parameters["CSVFile"] = filePathCSV
            launcherSPV = slicer.modules.launcher
            slicer.cli.run(launcherSPV, None, parameters, wait_for_completion=True)

            # Remove the vtk files previously created in the temporary directory of Slicer
            for value in self.dictVTKFiles.values():
                self.logic.removeDataVTKFiles(value)

    # Function to compute the new Classification Groups
    #    - Remove all the arrays of all the vtk files
    #    - Compute the mean of each group thanks to Statismo
    def onComputeNewClassificationGroups(self):
        for key, value in self.dictVTKFiles.items():
            # Delete all the arrays in vtk file
            self.logic.deleteArrays(key, value)

            # Compute the shape model of each group
            self.logic.buildShapeModel(key, value)

            # Remove the vtk files used to create the shape model of each group
            self.logic.removeDataVTKFiles(value)

            # Storage of the shape model for each group
            self.logic.storeShapeModel(self.dictShapeModels, key)

        # Enable the option to export the new data
        self.directoryButton_exportNewClassification.setEnabled(True)
        self.pushButton_exportNewClassification.setEnabled(True)

    # Function to export the new Classification Groups
    #    - Data saved:
    #           - Save the mean vtk files in the selected directory
    #           - Save the CSV file in the selected directory
    #    - Load automatically the CSV file in the next tab: "Selection of Classification Groups"
    def onExportNewClassificationGroups(self):
        print "--- Export the new Classification Groups ---"

        # Message for the user if files already exist
        directory = self.directoryButton_exportNewClassification.directory.encode('utf-8')
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        filePathExisting = list()

        #   Check if the CSV file exists
        CSVfilePath = directory + "/NewClassificationGroups.csv"
        if os.path.exists(CSVfilePath):
            filePathExisting.append(CSVfilePath)

        #   Check if the shape model exist
        for key, value in self.dictShapeModels.items():
            modelFilename = os.path.basename(value)
            modelFilePath = directory + '/' + modelFilename
            if os.path.exists(modelFilePath):
                filePathExisting.append(modelFilePath)

        #   Write the message for the user
        if len(filePathExisting) > 0:
            if len(filePathExisting) == 1:
                text = 'File ' + filePathExisting[0] + ' already exists!'
                informativeText = 'Do you want to replace it ?'
            elif len(filePathExisting) > 1:
                text = 'These files are already exist: \n'
                for path in filePathExisting:
                    text = text + path + '\n'
                    informativeText = 'Do you want to replace them ?'
            messageBox.setText(text)
            messageBox.setInformativeText(informativeText)
            messageBox.setStandardButtons( messageBox.No | messageBox.Yes)
            choice = messageBox.exec_()
            if choice == messageBox.No:
                return

        # Save the CSV File and the shape model of each group
        self.logic.saveNewClassificationGroups('NewClassificationGroups.csv', directory, self.dictShapeModels)

        # Remove the shape model (GX.h5) of each group
        self.logic.removeDataAfterNCG(self.dictShapeModels)

        # Re-Initialization of the dictionary containing the path of the shape model of each group
        self.dictShapeModels = dict()

        # Message for the user
        slicer.util.delayDisplay("Files Saved")

        # Disable the option to export the new data
        self.directoryButton_exportNewClassification.setDisabled(True)
        self.pushButton_exportNewClassification.setDisabled(True)

        # Load automatically the CSV file in the pathline in the next tab "Selection of Classification Groups"
        self.pathLineEdit_selectionClassificationGroups.setCurrentPath(CSVfilePath)

    # ---------------------------------------------------- #
    #        Tab: Selection of Classification Groups       #
    # ---------------------------------------------------- #

    # Function to select the Classification Groups
    def onSelectionClassificationGroups(self):
        # Re-initialization of the dictionary containing the Classification Groups
        self.dictShapeModels = dict()

        # Check if the path exists:
        if not os.path.exists(self.pathLineEdit_selectionClassificationGroups.currentPath):
            return

        print "------ Selection of a Classification Groups ------"

        # Check if it's a CSV file
        condition1 = self.logic.checkExtension(self.pathLineEdit_selectionClassificationGroups.currentPath, ".csv")
        if not condition1:
            self.pathLineEdit_selectionClassificationGroups.setCurrentPath(" ")
            return

        # Read CSV File:
        self.logic.table = self.logic.readCSVFile(self.pathLineEdit_selectionClassificationGroups.currentPath)
        condition3 = self.logic.creationDictShapeModel(self.dictShapeModels)

        # Check if there is one H5 file per group
        condition4 = self.logic.checkCSVFile(self.dictShapeModels)

        #    If the file is not conformed:
        #    Re-initialization of the dictionary containing the Classification Groups
        if not (condition3 and condition4):
            self.dictShapeModels = dict()
            self.pathLineEdit_selectionClassificationGroups.setCurrentPath(" ")
            return

        # Configuration of the table of the result
        self.initializeResultTable(len(self.dictShapeModels))

        # Enable/disable buttons
        self.spinBox_healthyGroup.setEnabled(True)
        self.pushButton_previewGroups.setEnabled(True)
        self.MRMLTreeView_classificationGroups.setEnabled(True)

        # Configuration of the spinbox specify the healthy group
        #      Set the Maximum value of spinBox_healthyGroup at the maximum number groups
        self.spinBox_healthyGroup.setMaximum(len(self.dictShapeModels))

    # ---------------------------------------------------- #
    #     Tab: Preview of Classification Groups            #
    # ---------------------------------------------------- #

    # Function to preview the Classification Groups in Slicer
    #    - The opacity of all the vtk files is set to 0.8
    #    - The healthy group is white and the others are red
    def onPreviewClassificationGroups(self):
        print "------ Preview of the Classification Groups in Slicer ------"

        for group, h5path in self.dictShapeModels.items():
            # Compute the mean of each group thanks to Statismo
            self.logic.computeMean(group, h5path)

            # Storage of the means for each group
            self.logic.storageMean(self.dictGroups, group)

        # If the user doesn't specify the healthy group
        #     error message for the user
        # Else
        #     load the Classification Groups in Slicer
        if self.spinBox_healthyGroup.value == 0:
            # Error message:
            slicer.util.errorDisplay('Miss the number of the healthy group ')
        else:
            for key in self.dictGroups.keys():
                filename = self.dictGroups.get(key, None)
                loader = slicer.util.loadModel
                loader(filename)

        # Change the color and the opacity for each vtk file
            list = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
            end = list.GetNumberOfItems()
            for i in range(3,end):
                model = list.GetItemAsObject(i)
                disp = model.GetDisplayNode()
                for group in self.dictGroups.keys():
                    filename = self.dictGroups.get(group, None)
                    if os.path.splitext(os.path.basename(filename))[0] == model.GetName():
                        if self.spinBox_healthyGroup.value == group:
                            disp.SetColor(1, 1, 1)
                            disp.VisibilityOn()
                        else:
                            disp.SetColor(1, 0, 0)
                            disp.VisibilityOff()
                        disp.SetOpacity(0.8)
                        break
                    disp.VisibilityOff()

        # Center the 3D view of the scene
        layoutManager = slicer.app.layoutManager()
        threeDWidget = layoutManager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        threeDView.resetFocalPoint()

    # ---------------------------------------------------- #
    #               Tab: Select Input Data                 #
    # ---------------------------------------------------- #

    # Function to select the vtk Input Data
    def onVTKInputData(self):
        # Remove the old vtk file in the temporary directory of slicer if it exists
        if self.patientList:
            print "onVTKInputData remove old vtk file"
            oldVTKPath = slicer.app.temporaryPath + "/" + os.path.basename(self.patientList[0])
            if os.path.exists(oldVTKPath):
                os.remove(oldVTKPath)

        # Re-Initialization of the patient list
        self.patientList = list()

        # Handle checkbox "File already in the groups"
        self.enableOption()

        # Delete the path in CSV file
        currentNode = self.MRMLNodeComboBox_VTKInputData.currentNode()
        if currentNode == None:
            return
        self.pathLineEdit_CSVInputData.setCurrentPath(" ")

        # Adding the vtk file to the list of patient
        currentNode = self.MRMLNodeComboBox_VTKInputData.currentNode()
        if not currentNode == None:
            #     Save the selected node in the temporary directory of slicer
            vtkfilepath = slicer.app.temporaryPath + "/" + self.MRMLNodeComboBox_VTKInputData.currentNode().GetName() + ".vtk"
            self.logic.saveVTKFile(self.MRMLNodeComboBox_VTKInputData.currentNode().GetPolyData(), vtkfilepath)
            #     Adding to the list
            self.patientList.append(vtkfilepath)

    # Function to handle the checkbox "File already in the groups"
    def enableOption(self):
        # Enable or disable the checkbox "File already in the groups" according to the data previously selected
        currentNode = self.MRMLNodeComboBox_VTKInputData.currentNode()
        if currentNode == None:
            if self.checkBox_fileInGroups.isChecked():
                self.checkBox_fileInGroups.setChecked(False)
            self.checkBox_fileInGroups.setDisabled(True)
        elif os.path.exists(self.pathLineEdit_NewGroups.currentPath):
            self.checkBox_fileInGroups.setEnabled(True)

        # Check if the selected file is in the groups used to create the classification groups
        self.onCheckFileInGroups()

    # Function to check if the selected file is in the groups used to create the classification groups
    #    - If it's not the case:
    #           - display of a error message
    #           - deselected checkbox
    def onCheckFileInGroups(self):
        if self.checkBox_fileInGroups.isChecked():
            node = self.MRMLNodeComboBox_VTKInputData.currentNode()
            if not node == None:
                vtkfileToFind = node.GetName() + '.vtk'
                find = self.logic.actionOnDictionary(self.dictVTKFiles, vtkfileToFind, None, 'find')
                if find == False:
                    slicer.util.errorDisplay('The selected file is not a file used to create the Classification Groups!')
                    self.checkBox_fileInGroups.setChecked(False)

    # Function to select the CSV Input Data
    def onCSVInputData(self):
        self.patientList = list()

        # Delete the path in VTK file
        if not os.path.exists(self.pathLineEdit_CSVInputData.currentPath):
            return
        self.MRMLNodeComboBox_VTKInputData.setCurrentNode(None)

        # Adding the name of the node a list
        if os.path.exists(self.pathLineEdit_CSVInputData.currentPath):
            patientTable = vtk.vtkTable
            patientTable = self.logic.readCSVFile(self.pathLineEdit_CSVInputData.currentPath)
            for i in range(0, patientTable.GetNumberOfRows()):
                self.patientList.append(patientTable.GetValue(i,0).ToString())

        # Handle checkbox "File already in the groups"
        self.enableOption()

    # Function to define the OA index type of the patient
    #    *** CROSS VALIDATION:
    #    - If the user specified that the vtk file was in the groups used to create the Classification Groups:
    #           - Save the current classification groups
    #           - Re-compute the new classification groups without this file
    #           - Define the OA index type of a patient
    #           - Recovery the classification groups
    #    *** Define the OA index of a patient:
    #    - Else:
    #           - Compute the ShapeOALoads for each group
    #           - Compute the OA index type of a patient
    def onComputeOAIndex(self):
        print "------ Compute the OA index Type of a patient ------"
        # Check if the user gave all the data used to compute the OA index type of the patient:
        # - VTK input data or CSV input data
        # - CSV file containing the Classification Groups
        if not os.path.exists(self.pathLineEdit_selectionClassificationGroups.currentPath):
            slicer.util.errorDisplay('Miss the CSV file containing the Classification Groups')
            return
        if self.MRMLNodeComboBox_VTKInputData.currentNode() == None and not self.pathLineEdit_CSVInputData.currentPath:
            slicer.util.errorDisplay('Miss the Input Data')
            return

        # **** CROSS VALIDATION ****
        # If the selected file is in the groups used to create the classification groups
        if self.checkBox_fileInGroups.isChecked():
            #      Remove the file in the dictionary used to compute the classification groups
            listSaveVTKFiles = list()
            vtkfileToRemove = self.MRMLNodeComboBox_VTKInputData.currentNode().GetName() + '.vtk'
            listSaveVTKFiles = self.logic.actionOnDictionary(self.dictVTKFiles,
                                                             vtkfileToRemove,
                                                             listSaveVTKFiles,
                                                             'remove')

            #      Copy the Classification Groups
            dictShapeModelsTemp = dict()
            dictShapeModelsTemp = self.dictShapeModels
            self.dictShapeModels = dict()

            #      Re-compute the new classification groups
            self.onComputeNewClassificationGroups()
        # **** **** #

        # *** Define the OA index type of a patient ***
        # For each patient:
        for patient in self.patientList:
            # Compute the ShapeOALoads for each group
            for key, value in self.dictShapeModels.items():
                self.logic.computeShapeOALoads(key, patient, value)

            # Compute the OA index type of a patient
            resultOAIndex = self.logic.computeOAIndex(self.dictShapeModels.keys())

            # Display the result in the next tab "Result/Analysis"
            self.displayResult(resultOAIndex[0], os.path.basename(patient), resultOAIndex[1])

        # Remove the CSV file containing the Shape OA Vector Loads
        self.logic.removeShapeOALoadsCSVFile(self.dictShapeModels.keys())

        # **** CROSS VALIDATION ****
        # If the selected file is in the groups used to create the classification groups
        if self.checkBox_fileInGroups.isChecked():
            #      Add the file previously removed to the dictionary used to create the classification groups
            self.logic.actionOnDictionary(self.dictVTKFiles,
                                          vtkfileToRemove,
                                          listSaveVTKFiles,
                                          'add')

            #      Recovery the Classification Groups previously saved
            self.dictShapeModels = dictShapeModelsTemp

            #      Remove the data previously created
            self.logic.removeDataAfterNCG(self.dictShapeModels)
        # **** **** #



    # ---------------------------------------------------- #
    #               Tab: Result / Analysis                 #
    # ---------------------------------------------------- #

    # Function to configure the table to display the result
    def initializeResultTable(self, numberOfGroups):
        columnTable = numberOfGroups + 2
        self.tableWidget_result.setColumnCount(columnTable)
        hearderLabelList = list()
        hearderLabelList.append(" VTK files ")
        hearderLabelList.append(" Assigned Group ")
        for i in range(1, numberOfGroups + 1):
            hearderLabel = " G" + str(i) + " OA Index "
            hearderLabelList.append(hearderLabel)

        self.tableWidget_result.setHorizontalHeaderLabels(hearderLabelList)
        self.tableWidget_result.setColumnWidth(0, 500)
        horizontalHeader = self.tableWidget_result.horizontalHeader()
        horizontalHeader.setStretchLastSection(False)
        horizontalHeader.setResizeMode(0,qt.QHeaderView.Stretch)
        for i in range(1, numberOfGroups + 2):
            horizontalHeader.setResizeMode(i,qt.QHeaderView.ResizeToContents)
        self.tableWidget_result.verticalHeader().setVisible(False)

    # Function to display the result in a table
    def displayResult(self, assignedGroup, VTKfilename, OAIndexList):
        row = self.tableWidget_result.rowCount
        self.tableWidget_result.setRowCount(row + 1)
        # Column 0: VTK file
        labelVTKFile = qt.QLabel(VTKfilename)
        labelVTKFile.setAlignment(0x84)
        self.tableWidget_result.setCellWidget(row, 0, labelVTKFile)
        # Column 1: Assigned Group
        labelAssignedGroup = qt.QLabel(assignedGroup)
        labelAssignedGroup.setAlignment(0x84)
        self.tableWidget_result.setCellWidget(row, 1, labelAssignedGroup)
        for OAIndex in OAIndexList:
            column = 2 + OAIndexList.index(OAIndex)
            labelOAIndex = qt.QLabel(OAIndex)
            labelOAIndex.setAlignment(0x84)
            self.tableWidget_result.setCellWidget(row, column, labelOAIndex)


    # Function to export the result in a CSV File
    def onExportResult(self):
        # Directory
        directory = self.directoryButton_exportResult.directory.encode('utf-8')
        basename = "OAResult.csv"
        # Message if the csv file already exists
        filepath = directory + "/" + basename
        messageBox = ctk.ctkMessageBox()
        messageBox.setWindowTitle(' /!\ WARNING /!\ ')
        messageBox.setIcon(messageBox.Warning)
        if os.path.exists(filepath):
            messageBox.setText('File ' + filepath + ' already exists!')
            messageBox.setInformativeText('Do you want to replace it ?')
            messageBox.setStandardButtons( messageBox.No | messageBox.Yes)
            choice = messageBox.exec_()
            if choice == messageBox.No:
                return

        # Directory
        directory = self.directoryButton_exportResult.directory.encode('utf-8')

        # Store data in a dictionary
        self.logic.creationCSVFileForResult(self.tableWidget_result, directory, basename)

        # Message in the python console and for the user
        print "Export CSV File: " + filepath
        slicer.util.delayDisplay("Result saved")


# ------------------------------------------------------------------------------------ #
#                                   ALGORITHM                                          #
# ------------------------------------------------------------------------------------ #


class DiagnosticIndexLogic(ScriptedLoadableModuleLogic):
    def __init__(self, interface):
        self.interface = interface
        self.table = vtk.vtkTable
        self.colorBar = {'Point1': [0, 0, 1, 0], 'Point2': [0.5, 1, 1, 0], 'Point3': [1, 1, 0, 0]}

    # Functions to recovery the widget in the .ui file
    def get(self, objectName):
        return self.findWidget(self.interface.widget, objectName)

    def findWidget(self, widget, objectName):
        if widget.objectName == objectName:
            return widget
        else:
            for w in widget.children():
                resulting_widget = self.findWidget(w, objectName)
                if resulting_widget:
                    return resulting_widget
            return None

    # Function to add all the vtk filepaths found in the given directory of a dictionary
    def addGroupToDictionary(self, dictCSVFile, directory, directoryList, group):
        # Fill a dictionary which contains the vtk files for the classification groups sorted by group
        valueList = list()
        for file in os.listdir(directory):
            if file.endswith(".vtk"):
                filepath = directory + '/' + file
                valueList.append(filepath)
        dictCSVFile[group] = valueList

        # Add the path of the directory
        directoryList.insert((group - 1), directory)

    # Function to remove the group of the dictionary
    def removeGroupToDictionary(self, dictCSVFile, directoryList, group):
        # Remove the group from the dictionary
        dictCSVFile.pop(group, None)

        # Remove the path of the directory
        directoryList.pop(group - 1)

    # Check if the path given has the right extension
    def checkExtension(self, filename, extension):
        if os.path.splitext(os.path.basename(filename))[1] == extension:
            return True
        slicer.util.errorDisplay('Wrong extension file, a CSV file is needed!')
        return False

    # Function to read a CSV file
    def readCSVFile(self, filename):
        print "CSV FilePath: " + filename
        CSVreader = vtk.vtkDelimitedTextReader()
        CSVreader.SetFieldDelimiterCharacters(",")
        CSVreader.SetFileName(filename)
        CSVreader.SetHaveHeaders(True)
        CSVreader.Update()

        return CSVreader.GetOutput()

    # Function to create a dictionary containing all the vtk filepaths sorted by group
    #    - the paths are given by a CSV file
    #    - If one paths doesn't exist
    #         Return False
    #      Else if all the path of all vtk file exist
    #         Return True
    def creationDictVTKFiles(self, dict):
        for i in range(0, self.table.GetNumberOfRows()):
            if not os.path.exists(self.table.GetValue(i,0).ToString()):
                slicer.util.errorDisplay('VTK file not found, path not good at lign ' + str(i+2))
                return False
            value = dict.get(self.table.GetValue(i,1).ToInt(), None)
            if value == None:
                dict[self.table.GetValue(i,1).ToInt()] = self.table.GetValue(i,0).ToString()
            else:
                if type(value) is ListType:
                    value.append(self.table.GetValue(i,0).ToString())
                else:
                    tempList = list()
                    tempList.append(value)
                    tempList.append(self.table.GetValue(i,0).ToString())
                    dict[self.table.GetValue(i,1).ToInt()] = tempList

        # Check
        # print "Number of Groups in CSV Files: " + str(len(dict))
        # for key, value in dict.items():
        #     print "Groupe: " + str(key)
        #     print "VTK Files: " + str(value)

        return True

    # Function to check if in each group there is at least more than one mesh
    def checkSeveralMeshInDict(self, dict):
        for key, value in dict.items():
            if type(value) is not ListType or len(value) == 1:
                slicer.util.errorDisplay('The group ' + str(key) + ' must contain more than one mesh.')
                return False
        return True

    # Function to store the shape models for each group in a dictionary
    #    - The function return True if all the paths exist, else False
    def creationDictShapeModel(self, dict):
        for i in range(0, self.table.GetNumberOfRows()):
            if not os.path.exists(self.table.GetValue(i,0).ToString()):
                slicer.util.errorDisplay('H5 file not found, path not good at lign ' + str(i+2))
                return False
            dict[self.table.GetValue(i,1).ToInt()] = self.table.GetValue(i,0).ToString()

        # Check
        # print "Number of Groups in CSV Files: " + str(len(dict))
        # for key, value in dict.items():
        #     print "Groupe: " + str(key)
        #     print "H5 Files: " + str(value)

        return True

    # Function to check the CSV file containing the Classification Groups
    #    - If there isn't one path per group
    #         Return False
    #      Else
    #         Return True
    def checkCSVFile(self, dict):
        for value in dict.values():
            if type(value) is ListType:
                slicer.util.errorDisplay('There are more than one vtk file by groups')
                return False
        return True

    # Function to add a color map "DisplayClassificationGroup" to all the vtk files
    # which allow the user to visualize each group with a different color in ShapePopulationViewer
    def addColorMap(self, table, dictVTKFiles):
        for key, value in dictVTKFiles.items():
            for vtkFile in value:
                # Read VTK File
                reader = vtk.vtkDataSetReader()
                reader.SetFileName(vtkFile)
                reader.ReadAllVectorsOn()
                reader.ReadAllScalarsOn()
                reader.Update()
                polyData = reader.GetOutput()

                # Copy of the polydata
                polyDataCopy = vtk.vtkPolyData()
                polyDataCopy.DeepCopy(polyData)
                pointData = polyDataCopy.GetPointData()

                # Add a New Array "DisplayClassificationGroup" to the polydata copy
                # which will have as the value for all the points the group associated of the mesh
                numPts = polyDataCopy.GetPoints().GetNumberOfPoints()
                arrayName = "DisplayClassificationGroup"
                hasArrayInt = pointData.HasArray(arrayName)
                if hasArrayInt == 1:
                    pointData.RemoveArray(arrayName)
                arrayToAdd = vtk.vtkDoubleArray()
                arrayToAdd.SetName(arrayName)
                arrayToAdd.SetNumberOfComponents(1)
                arrayToAdd.SetNumberOfTuples(numPts)
                for i in range(0, numPts):
                    arrayToAdd.InsertTuple1(i, key)
                pointData.AddArray(arrayToAdd)

                # Save in the temporary directory in Slicer the vtk file with the new array
                # to visualize them in Shape Population Viewer
                writer = vtk.vtkPolyDataWriter()
                filepath = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
                writer.SetFileName(filepath)
                if vtk.VTK_MAJOR_VERSION <= 5:
                    writer.SetInput(polyDataCopy)
                else:
                    writer.SetInputData(polyDataCopy)
                writer.Update()
                writer.Write()

    # Function to create a CSV file containing all the selected vtk files that the user wants to display in SPV
    def creationCSVFileForSPV(self, filename, table, dictVTKFiles):
        # Creation a CSV file with a header 'VTK Files'
        file = open(filename, 'w')
        cw = csv.writer(file, delimiter=',')
        cw.writerow(['VTK Files'])

        # Add the path of the vtk files if the users selected it
        for row in range(0,table.rowCount):
            # check the checkBox
            widget = table.cellWidget(row, 2)
            tuple = widget.children()
            checkBox = qt.QCheckBox()
            checkBox = tuple[1]
            if checkBox.isChecked():
                # Recovery of group fo each vtk file
                widget = table.cellWidget(row, 1)
                tuple = widget.children()
                comboBox = qt.QComboBox()
                comboBox = tuple[1]
                group = comboBox.currentIndex + 1
                # Recovery of the vtk filename
                qlabel = table.cellWidget(row, 0)
                vtkFile = qlabel.text
                pathVTKFile = slicer.app.temporaryPath + '/' + vtkFile
                cw.writerow([pathVTKFile])
        file.close()

    # Function to fill the table of the preview of all VTK files
    #    - Checkable combobox: allow the user to select one or several groups that he wants to display in SPV
    #    - Column 0: filename of the vtk file
    #    - Column 1: combobox with the group corresponding to the vtk file
    #    - Column 2: checkbox to allow the user to choose which models will be displayed in SPV
    #    - Column 3: color that the mesh will have in SPV
    def fillTableForPreviewVTKFilesInSPV(self, dictVTKFiles, checkableComboBox, table):
        row = 0
        for key, value in dictVTKFiles.items():
            # Fill the Checkable Combobox
            checkableComboBox.addItem("Group " + str(key))
            # Table:
            for vtkFile in value:
                table.setRowCount(row + 1)
                # Column 0:
                filename = os.path.basename(vtkFile)
                labelVTKFile = qt.QLabel(filename)
                labelVTKFile.setAlignment(0x84)
                table.setCellWidget(row, 0, labelVTKFile)

                # Column 1:
                widget = qt.QWidget()
                layout = qt.QHBoxLayout(widget)
                comboBox = qt.QComboBox()
                comboBox.addItems(dictVTKFiles.keys())
                comboBox.setCurrentIndex(key - 1)
                layout.addWidget(comboBox)
                layout.setAlignment(0x84)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                table.setCellWidget(row, 1, widget)
                comboBox.connect('currentIndexChanged(int)', self.interface.onGroupValueChanged)

                # Column 2:
                widget = qt.QWidget()
                layout = qt.QHBoxLayout(widget)
                checkBox = qt.QCheckBox()
                layout.addWidget(checkBox)
                layout.setAlignment(0x84)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                table.setCellWidget(row, 2, widget)
                checkBox.connect('stateChanged(int)', self.interface.onCheckBoxTableValueChanged)

                # Column 3:
                table.setItem(row, 3, qt.QTableWidgetItem())
                table.item(row,3).setBackground(qt.QColor(255,255,255))

                row = row + 1

    # Function to change the group of a vtk file
    #     - The user can change the group thanks to the combobox in the table used for the preview in SPV
    def onComboBoxTableValueChanged(self, dictVTKFiles, table):
        # For each row of the table
        for row in range(0,table.rowCount):
            # Recovery of the group associated to the vtk file which is in the combobox
            widget = table.cellWidget(row, 1)
            tuple = widget.children()
            comboBox = qt.QComboBox()
            comboBox = tuple[1]
            group = comboBox.currentIndex + 1
            # Recovery of the filename of vtk file
            qlabel = table.cellWidget(row, 0)
            vtkFile = qlabel.text

            # Update the dictionary if the vtk file has not the same group in the combobox than in the dictionary
            value = dictVTKFiles.get(group, None)
            if not any(vtkFile in s for s in value):
                # Find which list of the dictionary the vtk file is in
                for value in dictVTKFiles.values():
                    if any(vtkFile in s for s in value):
                        pathList = [s for s in value if vtkFile in s]
                        path = pathList[0]
                        # Remove the vtk file from the wrong group
                        value.remove(path)
                        # Add the vtk file in the right group
                        newvalue = dictVTKFiles.get(group, None)
                        newvalue.append(path)
                        break

    # Function to create the same color transfer function than there is in SPV
    def creationColorTransfer(self, groupSelected):
        # Creation of the color transfer function with the updated range
        colorTransferFunction = vtk.vtkColorTransferFunction()
        if len(groupSelected) > 0:
            groupSelectedList = list(groupSelected)
            rangeColorTransfer = [groupSelectedList[0], groupSelectedList[len(groupSelectedList) - 1]]
            colorTransferFunction.AdjustRange(rangeColorTransfer)
            for key, value in self.colorBar.items():
                # postion on the current arrow
                x = (groupSelectedList[len(groupSelectedList) - 1] - groupSelectedList[0]) * value[0] + groupSelectedList[0]
                # color of the current arrow
                r = value[1]
                g = value[2]
                b = value[3]
                colorTransferFunction.AddRGBPoint(x,r,g,b)
        return colorTransferFunction

    # Function to copy and delete all the arrays of all the meshes contained in a list
    def deleteArrays(self, key, value):
        for vtkFile in value:
            # Read VTK File
            reader = vtk.vtkDataSetReader()
            reader.SetFileName(vtkFile)
            reader.ReadAllVectorsOn()
            reader.ReadAllScalarsOn()
            reader.Update()
            polyData = reader.GetOutput()

            # Copy of the polydata
            polyDataCopy = vtk.vtkPolyData()
            polyDataCopy.DeepCopy(polyData)
            pointData = polyDataCopy.GetPointData()

            # Remove all the arrays
            numAttributes = pointData.GetNumberOfArrays()
            for i in range(0, numAttributes):
                pointData.RemoveArray(0)

            # Creation of the path of the vtk file without arrays to save it in the temporary directory of Slicer
            filename = os.path.basename(vtkFile)
            filepath = slicer.app.temporaryPath + '/' + filename

            # Save the vtk file without array in the temporary directory in Slicer
            self.saveVTKFile(polyDataCopy, filepath)

    # Function to save a VTK file to the filepath given
    def saveVTKFile(self, polydata, filepath):
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(filepath)
        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(polydata)
        else:
            writer.SetInputData(polydata)
        writer.Update()
        writer.Write()

    # Function to save in the temporary directory of Slicer a shape model file called GX.h5
    # built with the vtk files contained in the group X
    def buildShapeModel(self, groupnumber, vtkList):
        print "--- Build the shape model of the group " + str(groupnumber) + " ---"

        # Call of saveModel used to build a shape model from a given list of meshes
        # Arguments:
        #  --groupnumber is the number of the group used to create the shape model
        #  --vtkfilelist is a list of vtk paths of one group that will be used to create the shape model
        #  --resultdir is the path where the newly build model should be saved

        #     Creation of the command line
        #scriptedModulesPath = eval('slicer.modules.%s.path' % self.interface.moduleName.lower())
        #scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        #libPath = os.path.join(scriptedModulesPath)
        #sys.path.insert(0, libPath)
        #saveModel = os.path.join(scriptedModulesPath, '../hidden-cli-modules/saveModel')
        saveModel = "/Users/lpascal/Desktop/test/DiagnosticIndexExtension-build/bin/saveModel"
        arguments = list()
        arguments.append("--groupnumber")
        arguments.append(groupnumber)
        arguments.append("--vtkfilelist")
        vtkfilelist = ""
        for vtkFiles in vtkList:
            vtkfilelist = vtkfilelist + vtkFiles + ','
        arguments.append(vtkfilelist)
        arguments.append("--resultdir")
        resultdir = slicer.app.temporaryPath
        arguments.append(resultdir)

        #     Call the CLI
        process = qt.QProcess()
        print "Calling " + os.path.basename(saveModel)
        process.start(saveModel, arguments)
        process.waitForStarted()
        # print "state: " + str(process.state())
        process.waitForFinished()
        # print "error: " + str(process.error())

    # Function to compute the mean between all the mesh-files contained in one group
    def computeMean(self, group, h5path):
        print "--- Compute the mean of the group " + str(group) + " ---"

        # Call of computeMean used to compute a mean from a shape model
        # Arguments:
        #  --groupnumber is the number of the group used to create the shape model
        #  --resultdir is the path where the newly build model should be saved
        #  --shapemodel: Shape model of one group (H5 file path)

        #     Creation of the command line
        #scriptedModulesPath = eval('slicer.modules.%s.path' % self.interface.moduleName.lower())
        #scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        #libPath = os.path.join(scriptedModulesPath)
        #sys.path.insert(0, libPath)
        #computeMean = os.path.join(scriptedModulesPath, '../hidden/cli-modules/computeMean')
        computeMean = "/Users/lpascal/Desktop/test/DiagnosticIndexExtension-build/bin/computeMean"
        arguments = list()
        arguments.append("--groupnumber")
        arguments.append(group)
        arguments.append("--resultdir")
        resultdir = slicer.app.temporaryPath
        arguments.append(resultdir)
        arguments.append("--shapemodel")
        arguments.append(h5path)

        #     Call the executable
        process = qt.QProcess()
        print "Calling " + os.path.basename(computeMean)
        process.start(computeMean, arguments)
        process.waitForStarted()
        # print "state: " + str(process2.state())
        process.waitForFinished()
        # print "error: " + str(process2.error())

    # Function to remove in the temporary directory all the data used to create the mean for each group
    def removeDataVTKFiles(self, value):
        # remove of all the vtk file
        for vtkFile in value:
            filepath = slicer.app.temporaryPath + '/' + os.path.basename(vtkFile)
            if os.path.exists(filepath):
                os.remove(filepath)

    # Function to storage the mean of each group in a dictionary
    def storageMean(self, dictGroups, key):
        filename = "meanGroup" + str(key)
        meanPath = slicer.app.temporaryPath + '/' + filename + '.vtk'
        dictGroups[key] = meanPath

    # Function to storage the shape model of each group in a dictionary
    def storeShapeModel(self, dictShapeModels, key):
        filename = "G" + str(key)
        modelPath = slicer.app.temporaryPath + '/' + filename + '.h5'
        dictShapeModels[key] = modelPath

    # Function to create a CSV file:
    #    - Two columns are always created:
    #          - First column: path of the vtk files
    #          - Second column: group associated to this vtk file
    #    - If saveH5 is True, this CSV file will contain a New Classification Group, a thrid column is then added
    #          - Thrid column: path of the shape model of each group
    def creationCSVFile(self, directory, CSVbasename, dictForCSV, option):
        CSVFilePath = directory + "/" + CSVbasename
        file = open(CSVFilePath, 'w')
        cw = csv.writer(file, delimiter=',')
        if option == "Groups":
            cw.writerow(['VTK Files', 'Group'])
        elif option == "NCG":
            cw.writerow(['H5 Path', 'Group'])
        for key, value in dictForCSV.items():
            if type(value) is ListType:
                for vtkFile in value:
                    if option == "Groups":
                        cw.writerow([vtkFile, str(key)])
            elif option == "NCG":
                cw.writerow([value, str(key)])
        file.close()

    # Function to save the data of the new Classification Groups in the directory given by the user
    #       - The mean vtk files of each groups
    #       - The shape models of each groups
    #       - The CSV file containing:
    #               - First column: the paths of mean vtk file of each group
    #               - Second column: the groups associated
    #               - Third column: the paths of the shape model of each group
    def saveNewClassificationGroups(self, basename, directory, dictShapeModels):
        dictForCSV = dict()
        for key, value in dictShapeModels.items():
            # Save the shape model (h5 file) of each group
            h5Basename = "G" + str(key) + ".h5"
            oldh5path = slicer.app.temporaryPath + "/" + h5Basename
            newh5path = directory + "/" + h5Basename
            shutil.copyfile(oldh5path, newh5path)
            dictForCSV[key] = newh5path

        # Save the CSV file containing all the data useful in order to compute OAIndex of a patient
        self.creationCSVFile(directory, basename, dictForCSV, "NCG")

    # Function to remove in the temporary directory all the data useless after to do a export of the new Classification Groups
    def removeDataAfterNCG(self, dict):
        for key in dict.keys():
            # Remove of the shape model of each group
            h5Path = slicer.app.temporaryPath + "/G" + str(key) + ".h5"
            if os.path.exists(h5Path):
                os.remove(h5Path)

    # Function to make some action on a dictionary
    def actionOnDictionary(self, dict, file, listSaveVTKFiles, action):
        # Action Remove:
        #       Remove the vtk file to the dictionary dict
        #       If the vtk file was found:
        #            Return a list containing the key and the vtk file
        #       Else:
        #            Return False
        # Action Find:
        #       Find the vtk file in the dictionary dict
        #       If the vtk file was found:
        #            Return True
        #       Else:
        #            Return False
        if action == 'remove' or action == 'find':
            if not file == None:
                for key, value in dict.items():
                    for vtkFile in value:
                        filename = os.path.basename(vtkFile)
                        if filename == file:
                            if action == 'remove':
                                value.remove(vtkFile)
                                listSaveVTKFiles.append(key)
                                listSaveVTKFiles.append(vtkFile)
                                return listSaveVTKFiles
                            return True
            return False

        # Action Add:
        #      Add a vtk file to the dictionary dict at the given key contained in the first case of the list
        if action == 'add':
            if not listSaveVTKFiles == None and not file == None:
                value = dict.get(listSaveVTKFiles[0], None)
                value.append(listSaveVTKFiles[1])

    # Function in order to compute the shape OA loads of a sample
    def computeShapeOALoads(self, groupnumber, vtkfilepath, shapemodel):
        # Call of computeShapeOALoads used to compute shape loads of a sample for the current shape model
        # Arguments:
        #  --vtkfile: Sample Input Data (VTK file path)
        #  --resultdir: The path where the newly build model should be saved
        #  --groupnumber: The number of the group used to create the shape model
        #  --shapemodel: Shape model of one group (H5 file path)

        #     Creation of the command line
        #scriptedModulesPath = eval('slicer.modules.%s.path' % self.interface.moduleName.lower())
        #scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        #libPath = os.path.join(scriptedModulesPath)
        #sys.path.insert(0, libPath)
        #computeShapeOALoads = os.path.join(scriptedModulesPath, '../hidden/cli-modules/computeShapeOALoads')
        computeShapeOALoads = "/Users/lpascal/Desktop/test/DiagnosticIndexExtension-build/bin/computeShapeOALoads"
        arguments = list()
        arguments.append("--groupnumber")
        arguments.append(groupnumber)
        arguments.append("--vtkfile")
        arguments.append(vtkfilepath)
        arguments.append("--resultdir")
        resultdir = slicer.app.temporaryPath
        arguments.append(resultdir)
        arguments.append("--shapemodel")
        arguments.append(shapemodel)

        #     Call the CLI
        process = qt.QProcess()
        print "Calling " + os.path.basename(computeShapeOALoads)
        process.start(computeShapeOALoads, arguments)
        process.waitForStarted()
        # print "state: " + str(process.state())
        process.waitForFinished()
        # print "error: " + str(process.error())

    # Function to compute the OA index of a patient
    def computeOAIndex(self, keyList):
        OAIndexList = list()
        for key in keyList:
            ShapeOAVectorLoadsPath = slicer.app.temporaryPath + "/ShapeOAVectorLoadsG" + str(key) + ".csv"
            if not os.path.exists(ShapeOAVectorLoadsPath):
                return
            tableShapeOAVectorLoads = vtk.vtkTable
            tableShapeOAVectorLoads = self.readCSVFile(ShapeOAVectorLoadsPath)
            sum = 0
            for row in range(0, tableShapeOAVectorLoads.GetNumberOfRows()):
                ShapeOALoad = tableShapeOAVectorLoads.GetValue(row, 0).ToDouble()
                sum = sum + math.pow(ShapeOALoad, 2)
            OAIndexList.append(math.sqrt(sum)/tableShapeOAVectorLoads.GetNumberOfRows())
        # print OAIndexList
        result = list()
        asignedGroup = OAIndexList.index(min(OAIndexList)) + 1
        result.append(asignedGroup)
        result.append(OAIndexList)
        return result

    # Function to remove the shape model of each group
    def removeShapeOALoadsCSVFile(self, keylist):
        for key in keylist:
            shapeOALoadsPath = slicer.app.temporaryPath + "/ShapeOAVectorLoadsG" + str(key) + ".csv"
            if os.path.exists(shapeOALoadsPath):
                os.remove(shapeOALoadsPath)

    def creationCSVFileForResult(self, table, directory, CSVbasename):
        CSVFilePath = directory + "/" + CSVbasename
        file = open(CSVFilePath, 'w')
        cw = csv.writer(file, delimiter=',')
        header = list()
        header.append("VTK Files")
        header.append("Assigned Group")
        for column in range(2, table.columnCount):
            headertext = "G" + str(column - 1) + " OA Index"
            header.append(headertext)
        print header
        cw.writerow(header)
        label = list()
        for row in range(0, table.rowCount):
            for column in range(0, table.columnCount):
                # Recovery of the filename of vtk file
                qlabel = table.cellWidget(row, column)
                label.append(qlabel.text)

            # Write the result in the CSV File
            cw.writerow(label)
            label = list()

class DiagnosticIndexTest(ScriptedLoadableModuleTest):
    pass
