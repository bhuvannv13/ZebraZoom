import os
import webbrowser

try:
  from PyQt6.QtCore import Qt, QSize
  from PyQt6.QtGui import QCursor, QFont, QIcon, QIntValidator, QPixmap
  from PyQt6.QtWidgets import QApplication, QFrame, QLabel, QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QRadioButton, QLineEdit, QButtonGroup, QSpacerItem
  PYQT6 = True
except ImportError:
  from PyQt5.QtCore import Qt, QSize
  from PyQt5.QtGui import QCursor, QFont, QIcon, QIntValidator, QPixmap
  from PyQt5.QtWidgets import QApplication, QFrame, QLabel, QWidget, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QRadioButton, QLineEdit, QButtonGroup, QSpacerItem
  PYQT6 = False

import zebrazoom.code.util as util


class ChooseVideoToCreateConfigFileFor(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (350, 350)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)
    reloadCheckbox = QCheckBox("Click here to start from a configuration file previously created (instead of from scratch).", self)
    layout.addWidget(reloadCheckbox, alignment=Qt.AlignmentFlag.AlignCenter)

    sublayout1 = QVBoxLayout()
    selectVideoBtn = util.apply_style(QPushButton("Select the video you want to create a configuration file for.", self), background_color=util.LIGHT_YELLOW)
    selectVideoBtn.clicked.connect(lambda: controller.chooseVideoToCreateConfigFileFor(controller, reloadCheckbox.isChecked()) and util.addToHistory(controller.show_frame)("ChooseGeneralExperiment"))
    sublayout1.addWidget(selectVideoBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    sublayout1.addWidget(QLabel("(you will be able to use the configuration file you create for all videos that are similar to that video)", self), alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addLayout(sublayout1)

    sublayout2 = QVBoxLayout()
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    sublayout2.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    sublayout2.addWidget(QLabel('Warning: This procedure to create configuration files is incomplete.', self), alignment=Qt.AlignmentFlag.AlignCenter)
    sublayout2.addWidget(QLabel('You may not succeed at making a good configuration file to analyze your video.', self), alignment=Qt.AlignmentFlag.AlignCenter)
    sublayout2.addWidget(QLabel("If you don't manage to get a good configuration file that fits your needs, email us at info@zebrazoom.org.", self), alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addLayout(sublayout2)

    self.setLayout(layout)


class OptimizeConfigFile(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self._originalBackgroundPreProcessMethod = None
    self._originalBackgroundPreProcessParameters = None
    self._originalPostProcessMultipleTrajectories = None
    self._originalPostProcessMaxDistanceAuthorized = None
    self._originalPostProcessMaxDisapearanceFrames = None
    self._originalOutputValidationVideoContrastImprovement = None
    self._originalRecalculateForegroundImageBasedOnBodyArea = None
    self._originalPlotOnlyOneTailPointForVisu = None

    self._headEmbeddedWidgets = set()
    self._freelySwimmingWidgets = set()
    self._fastCenterOfMassWidgets = set()
    self._centerOfMassWidgets = set()

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Optimize previously created configuration file", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    optimizeButtonsLayout = QHBoxLayout()
    optimizeButtonsLayout.addStretch()
    optimizeFreelySwimmingBtn = util.apply_style(QPushButton("Optimize fish freely swimming tail tracking configuration file parameters", self), background_color=util.LIGHT_YELLOW)
    optimizeFreelySwimmingBtn.clicked.connect(lambda: util.addToHistory(controller.calculateBackgroundFreelySwim)(controller, 0, automaticParameters=True, useNext=False))
    optimizeButtonsLayout.addWidget(optimizeFreelySwimmingBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(optimizeFreelySwimmingBtn)
    optimizeHeadEmbeddedBtn = util.apply_style(QPushButton("Optimize head embedded tracking configuration file parameters", self), background_color=util.LIGHT_YELLOW)
    optimizeHeadEmbeddedBtn.clicked.connect(lambda: util.addToHistory(controller.calculateBackground)(controller, 0, useNext=False))
    optimizeButtonsLayout.addWidget(optimizeHeadEmbeddedBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    self._headEmbeddedWidgets.add(optimizeHeadEmbeddedBtn)
    optimizeBoutBtn = util.apply_style(QPushButton("Optimize/Add bouts detection (only for one animal per well)", self), background_color=util.LIGHT_YELLOW)
    optimizeBoutBtn.clicked.connect(lambda: util.addToHistory(controller.calculateBackgroundFreelySwim)(controller, 0, boutDetectionsOnly=True, useNext=False))
    optimizeButtonsLayout.addWidget(optimizeBoutBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(optimizeBoutBtn)
    self._headEmbeddedWidgets.add(optimizeBoutBtn)
    self._fastCenterOfMassWidgets.add(optimizeBoutBtn)
    optimizeButtonsLayout.addStretch()
    layout.addLayout(optimizeButtonsLayout)

    def updateOutputValidationVideoContrastImprovement(checked):
      if checked:
        controller.configFile["outputValidationVideoContrastImprovement"] = 1
      elif self._originalOutputValidationVideoContrastImprovement is None:
        if "outputValidationVideoContrastImprovement" in controller.configFile:
          del controller.configFile["outputValidationVideoContrastImprovement"]
      else:
        controller.configFile["outputValidationVideoContrastImprovement"] = 0
    self._improveContrastCheckbox = QCheckBox("Improve contrast on validation video", self)
    self._improveContrastCheckbox.toggled.connect(updateOutputValidationVideoContrastImprovement)
    layout.addWidget(self._improveContrastCheckbox, alignment=Qt.AlignmentFlag.AlignCenter)
    self._headEmbeddedWidgets.add(self._improveContrastCheckbox)
    headEmbeddedDocumentationBtn = util.apply_style(QPushButton("Help", self), background_color=util.LIGHT_YELLOW)
    headEmbeddedDocumentationBtn.clicked.connect(lambda: webbrowser.open_new("https://zebrazoom.org/documentation/docs/configurationFile/throughGUI/trackingheadEmbeddedConfigOptimization"))
    layout.addWidget(headEmbeddedDocumentationBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    self._headEmbeddedWidgets.add(headEmbeddedDocumentationBtn)

    advancedOptionsLayout = QGridLayout()
    vframe = QFrame(self)
    vframe.setFrameShape(QFrame.Shape.VLine)
    advancedOptionsLayout.addWidget(vframe, 0, 2, 15, 1)
    self._freelySwimmingWidgets.add(vframe)
    self._fastCenterOfMassWidgets.add(vframe)
    self._centerOfMassWidgets.add(vframe)
    hframe = QFrame(self)
    hframe.setFrameShape(QFrame.Shape.HLine)
    advancedOptionsLayout.addWidget(hframe, 4, 0, 1, 5)
    self._freelySwimmingWidgets.add(hframe)

    solveIssuesLabel = util.apply_style(QLabel("Solve issues near the borders of the wells/tanks/arenas"), font_size='16px')
    advancedOptionsLayout.addWidget(solveIssuesLabel, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(solveIssuesLabel)
    self._fastCenterOfMassWidgets.add(solveIssuesLabel)
    self._centerOfMassWidgets.add(solveIssuesLabel)
    solveIssuesInfoLabel = QLabel("backgroundPreProcessParameters should be an odd positive integer. Higher value filters more pixels on the borders of the wells/tanks/arenas.")
    solveIssuesInfoLabel.setMinimumSize(1, 1)
    solveIssuesInfoLabel.resizeEvent = lambda evt: solveIssuesInfoLabel.setMinimumWidth(evt.size().width()) or solveIssuesInfoLabel.setWordWrap(evt.size().width() <= solveIssuesInfoLabel.sizeHint().width())
    advancedOptionsLayout.addWidget(solveIssuesInfoLabel, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(solveIssuesInfoLabel)
    self._fastCenterOfMassWidgets.add(solveIssuesInfoLabel)
    self._centerOfMassWidgets.add(solveIssuesInfoLabel)
    self._backgroundPreProcessParameters = backgroundPreProcessParameters = QLineEdit(controller.window)
    backgroundPreProcessParameters.setValidator(QIntValidator(backgroundPreProcessParameters))
    backgroundPreProcessParameters.validator().setBottom(0)

    def updateBackgroundPreProcessParameters(text):
      if text:
        controller.configFile["backgroundPreProcessMethod"] = ["erodeThenMin"]
        controller.configFile["backgroundPreProcessParameters"] = [[int(text)]]
      else:
        if self._originalBackgroundPreProcessMethod is not None:
          controller.configFile["backgroundPreProcessParameters"] = self._originalBackgroundPreProcessMethod
        elif "backgroundPreProcessMethod" in controller.configFile:
          del controller.configFile["backgroundPreProcessMethod"]
        if self._originalBackgroundPreProcessParameters is not None:
          controller.configFile["backgroundPreProcessParameters"] = self._originalBackgroundPreProcessParameters
        elif "backgroundPreProcessParameters" in controller.configFile:
          del controller.configFile["backgroundPreProcessParameters"]
    backgroundPreProcessParameters.textChanged.connect(updateBackgroundPreProcessParameters)
    backgroundPreProcessParametersLabel = QLabel("backgroundPreProcessParameters:")
    advancedOptionsLayout.addWidget(backgroundPreProcessParametersLabel, 2, 0, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(backgroundPreProcessParametersLabel)
    self._fastCenterOfMassWidgets.add(backgroundPreProcessParametersLabel)
    self._centerOfMassWidgets.add(backgroundPreProcessParametersLabel)
    advancedOptionsLayout.addWidget(backgroundPreProcessParameters, 2, 1, Qt.AlignmentFlag.AlignLeft)
    self._freelySwimmingWidgets.add(backgroundPreProcessParameters)
    self._fastCenterOfMassWidgets.add(backgroundPreProcessParameters)
    self._centerOfMassWidgets.add(backgroundPreProcessParameters)

    postProcessTrajectoriesLabel = util.apply_style(QLabel("Post-process animal center trajectories"), font_size='16px')
    advancedOptionsLayout.addWidget(postProcessTrajectoriesLabel, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(postProcessTrajectoriesLabel)
    self._fastCenterOfMassWidgets.add(postProcessTrajectoriesLabel)
    self._centerOfMassWidgets.add(postProcessTrajectoriesLabel)
    postProcessTrajectoriesInfoLabel = QLabel("postProcessMaxDistanceAuthorized is the maximum distance in pixels above which it is considered that an animal was detected incorrectly (click on the button to adjust it visually). postProcessMaxDisapearanceFrames is the maximum number of frames for which the post-processing will consider that an animal can be incorrectly detected.")
    postProcessTrajectoriesInfoLabel.setMinimumSize(1, 1)
    postProcessTrajectoriesInfoLabel.resizeEvent = lambda evt: postProcessTrajectoriesInfoLabel.setMinimumWidth(evt.size().width()) or postProcessTrajectoriesInfoLabel.setWordWrap(evt.size().width() <= postProcessTrajectoriesInfoLabel.sizeHint().width())
    advancedOptionsLayout.addWidget(postProcessTrajectoriesInfoLabel, 1, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(postProcessTrajectoriesInfoLabel)
    self._fastCenterOfMassWidgets.add(postProcessTrajectoriesInfoLabel)
    self._centerOfMassWidgets.add(postProcessTrajectoriesInfoLabel)
    self._postProcessMaxDistanceAuthorized = postProcessMaxDistanceAuthorized = QLineEdit(controller.window)
    postProcessMaxDistanceAuthorized.setValidator(QIntValidator(postProcessMaxDistanceAuthorized))
    postProcessMaxDistanceAuthorized.validator().setBottom(0)

    def updatePostProcessMaxDistanceAuthorized(text):
      if text:
        controller.configFile["postProcessMaxDistanceAuthorized"] = int(text)
        controller.configFile["postProcessMultipleTrajectories"] = 1
      else:
        if not postProcessMaxDisapearanceFrames.text():
          if self._originalPostProcessMultipleTrajectories is not None:
            controller.configFile["postProcessMultipleTrajectories"] = self._originalPostProcessMultipleTrajectories
          elif "postProcessMultipleTrajectories" in controller.configFile:
            del controller.configFile["postProcessMultipleTrajectories"]
        if self._originalPostProcessMaxDistanceAuthorized is not None:
          controller.configFile["postProcessMaxDistanceAuthorized"] = self._originalPostProcessMaxDistanceAuthorized
        elif "postProcessMaxDistanceAuthorized" in controller.configFile:
          del controller.configFile["postProcessMaxDistanceAuthorized"]
    postProcessMaxDistanceAuthorized.textChanged.connect(updatePostProcessMaxDistanceAuthorized)
    postProcessMaxDistanceAuthorizedLabel = QPushButton("postProcessMaxDistanceAuthorized:")

    def modifyPostProcessMaxDistanceAuthorized():
      import zebrazoom.videoFormatConversion.zzVideoReading as zzVideoReading
      cap = zzVideoReading.VideoCapture(controller.videoToCreateConfigFileFor)
      cap.set(1, controller.configFile.get("firstFrame", 1))
      ret, frame = cap.read()
      cancelled = False
      def cancel():
        nonlocal cancelled
        cancelled = True
      center, radius = util.getCircle(frame, 'Click on the center of an animal and select the distance which it can realistically travel', cancel)
      if not cancelled:
        postProcessMaxDistanceAuthorized.setText(str(radius))
    postProcessMaxDistanceAuthorizedLabel.clicked.connect(modifyPostProcessMaxDistanceAuthorized)
    advancedOptionsLayout.addWidget(postProcessMaxDistanceAuthorizedLabel, 2, 3, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(postProcessMaxDistanceAuthorizedLabel)
    self._fastCenterOfMassWidgets.add(postProcessMaxDistanceAuthorizedLabel)
    self._centerOfMassWidgets.add(postProcessMaxDistanceAuthorizedLabel)
    advancedOptionsLayout.addWidget(postProcessMaxDistanceAuthorized, 2, 4, Qt.AlignmentFlag.AlignLeft)
    self._freelySwimmingWidgets.add(postProcessMaxDistanceAuthorized)
    self._fastCenterOfMassWidgets.add(postProcessMaxDistanceAuthorized)
    self._centerOfMassWidgets.add(postProcessMaxDistanceAuthorized)

    self._postProcessMaxDisapearanceFrames = postProcessMaxDisapearanceFrames = QLineEdit(controller.window)
    postProcessMaxDisapearanceFrames.setValidator(QIntValidator(postProcessMaxDisapearanceFrames))
    postProcessMaxDisapearanceFrames.validator().setBottom(0)

    def updatePostProcessMaxDisapearanceFrames(text):
      if text:
        controller.configFile["postProcessMaxDisapearanceFrames"] = int(text)
        controller.configFile["postProcessMultipleTrajectories"] = 1
      else:
        if not postProcessMaxDistanceAuthorized.text():
          if self._originalPostProcessMultipleTrajectories is not None:
            controller.configFile["postProcessMultipleTrajectories"] = self._originalPostProcessMultipleTrajectories
          elif "postProcessMultipleTrajectories" in controller.configFile:
            del controller.configFile["postProcessMultipleTrajectories"]
        if self._originalPostProcessMaxDisapearanceFrames is not None:
          controller.configFile["postProcessMaxDisapearanceFrames"] = self._originalPostProcessMaxDisapearanceFrames
        elif "postProcessMaxDisapearanceFrames" in controller.configFile:
          del controller.configFile["postProcessMaxDisapearanceFrames"]
    postProcessMaxDisapearanceFrames.textChanged.connect(updatePostProcessMaxDisapearanceFrames)
    postProcessMaxDisapearanceFramesLabel = QLabel("postProcessMaxDisapearanceFrames:")
    advancedOptionsLayout.addWidget(postProcessMaxDisapearanceFramesLabel, 3, 3, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(postProcessMaxDisapearanceFramesLabel)
    self._fastCenterOfMassWidgets.add(postProcessMaxDisapearanceFramesLabel)
    self._centerOfMassWidgets.add(postProcessMaxDisapearanceFramesLabel)
    advancedOptionsLayout.addWidget(postProcessMaxDisapearanceFrames, 3, 4, Qt.AlignmentFlag.AlignLeft)
    self._freelySwimmingWidgets.add(postProcessMaxDisapearanceFrames)
    self._fastCenterOfMassWidgets.add(postProcessMaxDisapearanceFrames)
    self._centerOfMassWidgets.add(postProcessMaxDisapearanceFrames)

    tailTrackingLabel = util.apply_style(QLabel("Tail tracking quality"), font_size='16px')
    advancedOptionsLayout.addWidget(tailTrackingLabel, 5, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(tailTrackingLabel)
    tailTrackingInfoLabel = QLabel("Checking this increases quality, but makes tracking slower.")
    advancedOptionsLayout.addWidget(tailTrackingInfoLabel, 6, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(tailTrackingInfoLabel)
    self._recalculateForegroundImageBasedOnBodyArea = QCheckBox("recalculateForegroundImageBasedOnBodyArea")

    def updateRecalculateForegroundImageBasedOnBodyArea(checked):
      if checked:
        controller.configFile["recalculateForegroundImageBasedOnBodyArea"] = 1
      elif self._originalRecalculateForegroundImageBasedOnBodyArea is None:
        if "recalculateForegroundImageBasedOnBodyArea" in controller.configFile:
          del controller.configFile["recalculateForegroundImageBasedOnBodyArea"]
      else:
        controller.configFile["recalculateForegroundImageBasedOnBodyArea"] = 0
    self._recalculateForegroundImageBasedOnBodyArea.toggled.connect(updateRecalculateForegroundImageBasedOnBodyArea)
    advancedOptionsLayout.addWidget(self._recalculateForegroundImageBasedOnBodyArea, 7, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(self._recalculateForegroundImageBasedOnBodyArea)

    plotOnlyOneTailPointForVisuLabel = util.apply_style(QLabel("Validation video options"), font_size='16px')
    advancedOptionsLayout.addWidget(plotOnlyOneTailPointForVisuLabel, 5, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(plotOnlyOneTailPointForVisuLabel)
    self._headEmbeddedWidgets.add(plotOnlyOneTailPointForVisuLabel)
    def updatePlotOnlyOneTailPointForVisu(checked):
      if checked:
        controller.configFile["plotOnlyOneTailPointForVisu"] = 1
      elif self._originalPlotOnlyOneTailPointForVisu is None:
        if "plotOnlyOneTailPointForVisu" in controller.configFile:
          del controller.configFile["plotOnlyOneTailPointForVisu"]
      else:
        controller.configFile["plotOnlyOneTailPointForVisu"] = 0
    self._plotOnlyOneTailPointForVisu = QCheckBox("Display tracking point only on the tail tip in validation videos", self)
    self._plotOnlyOneTailPointForVisu.toggled.connect(updatePlotOnlyOneTailPointForVisu)
    advancedOptionsLayout.addWidget(self._plotOnlyOneTailPointForVisu, 6, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(self._plotOnlyOneTailPointForVisu)
    self._headEmbeddedWidgets.add(self._plotOnlyOneTailPointForVisu)

    hframe = QFrame(self)
    hframe.setFrameShape(QFrame.Shape.HLine)
    advancedOptionsLayout.addWidget(hframe, 8, 0, 1, 5)
    self._freelySwimmingWidgets.add(hframe)
    advancedOptionsLabel = util.apply_style(QLabel("Documentation links"), font_size='16px')
    advancedOptionsLayout.addWidget(advancedOptionsLabel, 9, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(advancedOptionsLabel)
    speedUpTrackingBtn = util.apply_style(QPushButton("Speed up tracking for 'Track heads and tails of freely swimming fish'", self), background_color=util.LIGHT_YELLOW)
    speedUpTrackingBtn.clicked.connect(lambda: webbrowser.open_new("https://github.com/oliviermirat/ZebraZoom/blob/master/TrackingSpeedOptimization.md"))
    advancedOptionsLayout.addWidget(speedUpTrackingBtn, 10, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(speedUpTrackingBtn)
    documentationBtn = util.apply_style(QPushButton("Help", self), background_color=util.LIGHT_YELLOW)
    documentationBtn.clicked.connect(lambda: webbrowser.open_new("https://zebrazoom.org/documentation/docs/configurationFile/throughGUI/trackingFreelySwimmingConfigOptimization"))
    advancedOptionsLayout.addWidget(documentationBtn, 11, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    self._freelySwimmingWidgets.add(documentationBtn)

    def updateColumnWidths(setUniform):
      if setUniform:
        for idx in range(advancedOptionsLayout.columnCount()):
          advancedOptionsLayout.setColumnStretch(idx, 1)
      else:
        for idx in range(3):
          advancedOptionsLayout.setColumnStretch(idx, 0)
    self._updateColumnWidths = updateColumnWidths
    self._updateColumnWidths(True)
    self._expander = util.Expander(self, 'Show advanced options', advancedOptionsLayout, showFrame=True, addScrollbars=True)
    layout.addWidget(self._expander)

    frame = QFrame()
    frame.setFrameShadow(QFrame.Shadow.Raised)
    frame.setFrameShape(QFrame.Shape.Box)
    frameLayout = QVBoxLayout()
    testCheckbox = QCheckBox("Test tracking after saving config", self)
    testCheckbox.setChecked(True)
    testCheckbox.clearFocus()
    frameLayout.addWidget(testCheckbox, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
    saveBtn = util.apply_style(QPushButton("Save Config File", self), background_color=util.LIGHT_YELLOW)
    saveBtn.clicked.connect(lambda: controller.finishConfig(testCheckbox.isChecked()))
    frameLayout.addWidget(saveBtn, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
    frame.setLayout(frameLayout)
    layout.addWidget(frame, alignment=Qt.AlignmentFlag.AlignCenter)

    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    layout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(QLabel("If you don't manage to get a good configuration file that fits your needs, email us at info@zebrazoom.org.", self), alignment=Qt.AlignmentFlag.AlignCenter)

    centralWidget = QWidget()
    centralWidget.sizeHint = lambda *args: QSize(1152, 768)
    centralWidget.setLayout(layout)
    wrapperLayout = QVBoxLayout()
    wrapperLayout.addWidget(centralWidget, alignment=Qt.AlignmentFlag.AlignCenter)
    self.setLayout(wrapperLayout)

  def refresh(self):
    app = QApplication.instance()
    trackingMethod = app.configFile.get("trackingMethod", None)
    if not trackingMethod:
      if app.configFile.get("headEmbeded", False):
        visibleWidgets = self._headEmbeddedWidgets
      else:
        visibleWidgets = self._freelySwimmingWidgets
    elif trackingMethod == "fastCenterOfMassTracking_KNNbackgroundSubtraction" or \
        trackingMethod == "fastCenterOfMassTracking_ClassicalBackgroundSubtraction":
      visibleWidgets = self._fastCenterOfMassWidgets
    else:
      assert trackingMethod == "classicCenterOfMassTracking"
      visibleWidgets = self._centerOfMassWidgets
    for widget in self._freelySwimmingWidgets | self._headEmbeddedWidgets | self._fastCenterOfMassWidgets | self._centerOfMassWidgets:
      if widget in visibleWidgets:
        widget.show()
      else:
        widget.hide()
    self._updateColumnWidths(visibleWidgets is not self._headEmbeddedWidgets)
    self._expander.hide()
    maximumHeight = self._expander.maximumHeight()
    self._expander.setMaximumHeight(self.height())
    layout = self.layout().itemAt(0).widget().layout()
    layout.setStretchFactor(self._expander, 1)
    self._expander.show()
    availableHeight = self._expander.size().height()
    layout.setStretchFactor(self._expander, 0)
    self._expander.setMaximumHeight(maximumHeight)
    self._expander.refresh(availableHeight=availableHeight)

    self._originalBackgroundPreProcessMethod = app.configFile.get("backgroundPreProcessMethod")
    self._originalBackgroundPreProcessParameters = app.configFile.get("backgroundPreProcessParameters")
    if self._originalBackgroundPreProcessParameters is not None:
      self._backgroundPreProcessParameters.setText(str(self._originalBackgroundPreProcessParameters[0][0]))
    else:
      self._backgroundPreProcessParameters.setText('')
    self._originalPostProcessMultipleTrajectories = app.configFile.get("postProcessMultipleTrajectories")
    self._originalPostProcessMaxDistanceAuthorized = app.configFile.get("postProcessMaxDistanceAuthorized")
    if self._originalPostProcessMaxDistanceAuthorized is not None:
      self._postProcessMaxDistanceAuthorized.setText(str(self._originalPostProcessMaxDistanceAuthorized))
    else:
      self._postProcessMaxDistanceAuthorized.setText('')
    self._originalPostProcessMaxDisapearanceFrames = app.configFile.get("postProcessMaxDisapearanceFrames")
    if self._originalPostProcessMaxDisapearanceFrames is not None:
      self._postProcessMaxDisapearanceFrames.setText(str(self._originalPostProcessMaxDisapearanceFrames))
    else:
      self._postProcessMaxDisapearanceFrames.setText('')
    self._originalOutputValidationVideoContrastImprovement = app.configFile.get("outputValidationVideoContrastImprovement")
    if self._originalOutputValidationVideoContrastImprovement is not None:
      self._improveContrastCheckbox.setChecked(bool(self._originalOutputValidationVideoContrastImprovement))
    else:
      self._improveContrastCheckbox.setChecked(False)
    self._originalRecalculateForegroundImageBasedOnBodyArea = app.configFile.get("recalculateForegroundImageBasedOnBodyArea")
    if self._originalRecalculateForegroundImageBasedOnBodyArea is not None:
      self._recalculateForegroundImageBasedOnBodyArea.setChecked(bool(self._originalRecalculateForegroundImageBasedOnBodyArea))
    else:
      self._recalculateForegroundImageBasedOnBodyArea.setChecked(False)
    self._originalPlotOnlyOneTailPointForVisu = app.configFile.get("plotOnlyOneTailPointForVisu")
    if self._originalPlotOnlyOneTailPointForVisu is not None:
      self._plotOnlyOneTailPointForVisu.setChecked(bool(self._originalPlotOnlyOneTailPointForVisu))
    else:
      self._plotOnlyOneTailPointForVisu.setChecked(False)


class _ClickableImageLabel(QLabel):
  def __init__(self, parent, pixmap, clickedCallback):
    super().__init__(parent)
    self._originalPixmap = pixmap
    self._clickedCallback = clickedCallback
    self.setMinimumSize(1, 1)

  def resizeEvent(self, evt):
    scaling = self.devicePixelRatio() if PYQT6 else self.devicePixelRatioF()
    size = self._originalPixmap.size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
    img = self._originalPixmap.scaled(int(size.width() * scaling), int(size.height() * scaling))
    img.setDevicePixelRatio(scaling)
    self.setPixmap(img)
    blocked = self.blockSignals(True)
    self.resize(size)
    self.blockSignals(blocked)

  def mousePressEvent(self, evt):
    QApplication.restoreOverrideCursor()
    self._clickedCallback()

  def enterEvent(self, evt):
    QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)

  def leaveEvent(self, evt):
    QApplication.restoreOverrideCursor()


class ChooseGeneralExperiment(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QGridLayout()
    layout.setSpacing(2)
    layout.setRowStretch(3, 1)
    layout.setRowStretch(7, 1)
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(2, 1)
    layout.addItem(QSpacerItem(16, 16), 4, 1, 1, 1)
    curDirPath = os.path.dirname(os.path.realpath(__file__))

    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
    freelySwimmingTitleLabel = util.apply_style(QLabel("Head and tail tracking of freely swimming fish", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    freelySwimmingTitleLabel.setWordWrap(True)
    layout.addWidget(freelySwimmingTitleLabel, 1, 0)
    freelySwimmingLabel = QLabel("Multiple fish can be tracked in the same well but the tail tracking can be mediocre when fish collide. Each well should contain the same number of fish.", self)
    freelySwimmingLabel.setWordWrap(True)
    layout.addWidget(freelySwimmingLabel, 2, 0)
    freelySwimmingImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'freelySwimming.png')), lambda: controller.chooseGeneralExperimentFirstStep(controller, True, False, False, False, False, False))
    layout.addWidget(freelySwimmingImage, 3, 0)

    headEmbeddedTitleLabel = util.apply_style(QLabel("Tail tracking of head-embedded fish", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    headEmbeddedTitleLabel.setWordWrap(True)
    layout.addWidget(headEmbeddedTitleLabel, 1, 2)
    headEmbeddedImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'headEmbedded.png')), lambda: controller.chooseGeneralExperimentFirstStep(controller, False, True, False, False, False, False))
    layout.addWidget(headEmbeddedImage, 3, 2)

    fastCenterOfMassTitleLabel = util.apply_style(QLabel("Fast center of mass tracking for any kind of animal", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    fastCenterOfMassTitleLabel.setWordWrap(True)
    layout.addWidget(fastCenterOfMassTitleLabel, 5, 0)
    fastCenterOfMassLabel = QLabel("Only one animal per well, very useful for videos acquired at low frequency", self)
    fastCenterOfMassLabel.setWordWrap(True)
    layout.addWidget(fastCenterOfMassLabel, 6, 0)
    fastCenterOfMassImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'screen.png')), lambda: controller.chooseGeneralExperimentFirstStep(controller, False, False, False, False, False, True))
    layout.addWidget(fastCenterOfMassImage, 7, 0)

    centerOfMassTitleLabel = util.apply_style(QLabel("Center of mass tracking for any kind of animal", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    centerOfMassTitleLabel.setWordWrap(True)
    layout.addWidget(centerOfMassTitleLabel, 5, 2)
    centerOfMassLabel = QLabel("Several animals can be tracked in the same well/tank/arena. Each well should contain the same number of animals.", self)
    centerOfMassLabel.setWordWrap(True)
    layout.addWidget(centerOfMassLabel, 6, 2)
    centerOfMassImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'centerOfMassAnyAnimal.png')), lambda: controller.chooseGeneralExperimentFirstStep(controller, False, False, False, False, True, False))
    layout.addWidget(centerOfMassImage, 7, 2)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout, 8, 0, 1, 3)

    self.setLayout(layout)


class FreelySwimmingExperiment(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (750, 500)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File for Freely Swimming Fish:", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Choose only one of the options below:", self), font=QFont("Helvetica", 12)), alignment=Qt.AlignmentFlag.AlignCenter)
    freeZebra2RadioButton = QRadioButton("Recommended method: Automatic Parameters Setting", self)
    freeZebra2RadioButton.setChecked(True)
    layout.addWidget(freeZebra2RadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(QLabel("This method will work well on most videos. One exception can be for fish of very different sizes.", self), alignment=Qt.AlignmentFlag.AlignCenter)
    advancedOptionsLayout = QVBoxLayout()
    freeZebraRadioButton = QRadioButton("Alternative method: Manual Parameters Setting", self)
    advancedOptionsLayout.addWidget(freeZebraRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    advancedOptionsLayout.addWidget(QLabel("It's more difficult to create a configuration file with this method, but it can sometimes be useful as an alternative.", self), alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.Expander(self, "Show advanced options", advancedOptionsLayout))

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    nextBtn = util.apply_style(QPushButton("Next", self), background_color=util.LIGHT_YELLOW)
    nextBtn.clicked.connect(lambda: util.addToHistory(controller.chooseGeneralExperiment)(controller, freeZebraRadioButton.isChecked(), 0, 0, 0, 0, freeZebra2RadioButton.isChecked()))
    buttonsLayout.addWidget(nextBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class WellOrganisation(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QGridLayout()
    layout.setSpacing(2)
    layout.setRowStretch(3, 1)
    layout.setRowStretch(6, 1)
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(2, 1)
    layout.addItem(QSpacerItem(16, 16), 4, 1, 1, 1)
    curDirPath = os.path.dirname(os.path.realpath(__file__))

    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("General methods:", self), font=util.TITLE_FONT), 1, 0)
    layout.addWidget(util.apply_style(QLabel("Manually defined regions of interest:", self), font=util.TITLE_FONT), 1, 2)

    def labelResized(label, evt):
      scaling = label.devicePixelRatio() if PYQT6 else label.devicePixelRatioF()
      size = label.originalPixmap.size().scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio)
      img = label.originalPixmap.scaled(int(size.width() * scaling), int(size.height() * scaling))
      img.setDevicePixelRatio(scaling)
      label.setPixmap(img)

    gridSystemTitleLabel = util.apply_style(QLabel("Grid system (recommended in many cases)", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    gridSystemTitleLabel.setWordWrap(True)
    layout.addWidget(gridSystemTitleLabel, 2, 0)
    gridSystemImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'gridSystem.png')), lambda: controller.wellOrganisation(controller, False, False, False, False, False, True))
    layout.addWidget(gridSystemImage, 3, 0)

    multipleROITitleLabel = util.apply_style(QLabel("Chosen at runtime, right before tracking starts (multiple regions possible)", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    multipleROITitleLabel.setWordWrap(True)
    layout.addWidget(multipleROITitleLabel, 2, 2)
    multipleROIImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'runtimeROI.png')), lambda: controller.wellOrganisation(controller, False, False, False, False, True, False))
    layout.addWidget(multipleROIImage, 3, 2)

    wholeVideoTitleLabel = util.apply_style(QLabel("Whole video", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    wholeVideoTitleLabel.setWordWrap(True)
    layout.addWidget(wholeVideoTitleLabel, 5, 0)
    wholeVideoImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'wholeVideo.png')), lambda: controller.wellOrganisation(controller, False, False, False, True, False, False))
    layout.addWidget(wholeVideoImage, 6, 0)

    singleROITitleLabel = util.apply_style(QLabel("Fixed in the configuration file (only one region)", self), font=QFont('Helvetica', 14, QFont.Weight.Bold))
    singleROITitleLabel.setWordWrap(True)
    layout.addWidget(singleROITitleLabel, 5, 2)
    singleROIImage = _ClickableImageLabel(self, QPixmap(os.path.join(curDirPath, 'configFileROI.png')), lambda: controller.wellOrganisation(controller, False, False, True, False, False, False))
    layout.addWidget(singleROIImage, 6, 2)

    advancedOptionsLayout = QHBoxLayout()
    advancedOptionsLayout.addStretch()
    circularWellsBtn = QPushButton("Circular wells (beta version, unstable)")
    circularWellsBtn.clicked.connect(lambda: controller.wellOrganisation(controller, True, False, False, False, False, False))
    advancedOptionsLayout.addWidget(circularWellsBtn)
    rectangularWellsBtn = QPushButton("Rectangular wells (beta version, unstable)")
    rectangularWellsBtn.clicked.connect(lambda: controller.wellOrganisation(controller, False, True, False, False, False, False))
    advancedOptionsLayout.addWidget(rectangularWellsBtn)
    advancedOptionsLayout.addStretch()
    layout.addWidget(util.Expander(self, 'Show advanced options', advancedOptionsLayout), 7, 0, 1, 3)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout, 8, 0, 1, 3)

    self.setLayout(layout)


class NbRegionsOfInterest(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (450, 300)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("How many regions of interest / wells are there in your video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbwells = QLineEdit(controller.window)
    nbwells.setValidator(QIntValidator(nbwells))
    nbwells.validator().setBottom(0)
    layout.addWidget(nbwells, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    nextBtn = util.apply_style(QPushButton("Next", self), background_color=util.LIGHT_YELLOW)
    nextBtn.clicked.connect(lambda: controller.regionsOfInterest(controller, int(nbwells.text())))
    buttonsLayout.addWidget(nextBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class HomegeneousWellsLayout(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (1152, 768)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("How many wells are there in your video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbwells = QLineEdit(controller.window)
    nbwells.setValidator(QIntValidator(nbwells))
    nbwells.validator().setBottom(0)
    layout.addWidget(nbwells, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("How many rows of wells are there in your video? (leave blank for default of 1)", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbRowsOfWells = QLineEdit(controller.window)
    nbRowsOfWells.setValidator(QIntValidator(nbRowsOfWells))
    nbRowsOfWells.validator().setBottom(0)
    layout.addWidget(nbRowsOfWells, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("How many wells are there per row on your video? (leave blank for default of 4)", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbWellsPerRows = QLineEdit(controller.window)
    nbWellsPerRows.setValidator(QIntValidator(nbWellsPerRows))
    nbWellsPerRows.validator().setBottom(0)
    layout.addWidget(nbWellsPerRows, alignment=Qt.AlignmentFlag.AlignCenter)

    finishBtn = util.apply_style(QPushButton("Finish now", self), background_color=util.LIGHT_YELLOW)
    finishBtn.clicked.connect(lambda: controller.homegeneousWellsLayout(controller, nbwells.text(), nbRowsOfWells.text(), nbWellsPerRows.text()))
    layout.addWidget(finishBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(QLabel('The tracking will work nicely in many cases when choosing this option.', self), alignment=Qt.AlignmentFlag.AlignCenter)

    adjustBtn = util.apply_style(QPushButton("Adjust Parameters futher", self), background_color=util.LIGHT_YELLOW)
    adjustBtn.clicked.connect(lambda: controller.morePreciseFastScreen(controller, nbwells.text(), nbRowsOfWells.text(), nbWellsPerRows.text()))
    layout.addWidget(adjustBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(QLabel('Choosing this option will lead to a higher probability that the tracking will work well.', self), alignment=Qt.AlignmentFlag.AlignCenter)

    linkBtn1 = util.apply_style(QPushButton("Alternative", self), background_color=util.GOLD)
    linkBtn1.clicked.connect(lambda: webbrowser.open_new("https://github.com/oliviermirat/ZebraZoom/blob/master/FastScreenTrackingGuidlines.md"))
    layout.addWidget(linkBtn1, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class CircularOrRectangularWells(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (750, 500)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("How many wells are there in your video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbwells = QLineEdit(controller.window)
    nbwells.setValidator(QIntValidator(nbwells))
    nbwells.validator().setBottom(0)
    layout.addWidget(nbwells, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("How many rows of wells are there in your video? (leave blank for default of 1)", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbRowsOfWells = QLineEdit(controller.window)
    nbRowsOfWells.setValidator(QIntValidator(nbRowsOfWells))
    nbRowsOfWells.validator().setBottom(0)
    layout.addWidget(nbRowsOfWells, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("How many wells are there per row on your video? (leave blank for default of 4)", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbWellsPerRows = QLineEdit(controller.window)
    nbWellsPerRows.setValidator(QIntValidator(nbWellsPerRows))
    nbWellsPerRows.validator().setBottom(0)
    layout.addWidget(nbWellsPerRows, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    nextBtn = util.apply_style(QPushButton("Next", self), background_color=util.LIGHT_YELLOW)
    nextBtn.clicked.connect(lambda: controller.circularOrRectangularWells(controller, nbwells.text(), nbRowsOfWells.text(), nbWellsPerRows.text()))
    buttonsLayout.addWidget(nextBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class ChooseCircularWellsLeft(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    button = QPushButton("Click on the left inner border of the top left well", self)
    button.clicked.connect(lambda: controller.chooseCircularWellsLeft(controller))
    layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Example:", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    image = QLabel(self)
    image.setPixmap(QPixmap(os.path.join(cur_dir_path, 'leftborder.png')))
    layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class ChooseCircularWellsRight(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    button = QPushButton("Click on the right inner border of the top left well", self)
    button.clicked.connect(lambda: controller.chooseCircularWellsRight(controller))
    layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Example:", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    image = QLabel(self)
    image.setPixmap(QPixmap(os.path.join(cur_dir_path, 'rightborder.png')))
    layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class NumberOfAnimals(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (750, 500)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("What's the total number of animals in your video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbanimals = QLineEdit(controller.window)
    nbanimals.setValidator(QIntValidator(nbanimals))
    nbanimals.validator().setBottom(0)
    layout.addWidget(nbanimals, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("Are all of those animals ALWAYS visible throughout the video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    yesRadioButton = QRadioButton("Yes", self)
    yesRadioButton.setChecked(True)
    layout.addWidget(yesRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    noRadioButton = QRadioButton("No", self)
    layout.addWidget(noRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)

    forceBlobMethodForHeadTrackingCheckbox = QCheckBox("Blob method for head tracking of fish", self)
    layout.addWidget(forceBlobMethodForHeadTrackingCheckbox, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Only click the box above if you tried the tracking without this option and the head tracking was suboptimal (an eye was detected instead of the head for example).", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    nextBtn = util.apply_style(QPushButton("Next", self), background_color=util.LIGHT_YELLOW)
    nextBtn.clicked.connect(lambda: controller.numberOfAnimals(controller, nbanimals.text(), yesRadioButton.isChecked(), noRadioButton.isChecked(), forceBlobMethodForHeadTrackingCheckbox.isChecked(), 0, 0, 0, 0, 0, 0, 0))
    buttonsLayout.addWidget(nextBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class NumberOfAnimals2(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (1152, 768)

    layout = QGridLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("What's the total number of animals in your video?", self), font_size='16px'), 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
    nbanimals = QLineEdit(controller.window)
    nbanimals.setValidator(QIntValidator(nbanimals))
    nbanimals.validator().setBottom(0)
    layout.addWidget(nbanimals, 2, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("Are all of those animals ALWAYS visible throughout the video?", self), font_size='16px'), 3, 1, Qt.AlignmentFlag.AlignCenter)
    yesNoLayout1 = QHBoxLayout()
    yesNoLayout1.addStretch()
    btnGroup1 = QButtonGroup(self)
    yesRadioButton = QRadioButton("Yes", self)
    btnGroup1.addButton(yesRadioButton)
    yesRadioButton.setChecked(True)
    yesNoLayout1.addWidget(yesRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    noRadioButton = QRadioButton("No", self)
    btnGroup1.addButton(noRadioButton)
    yesNoLayout1.addWidget(noRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    yesNoLayout1.addStretch()
    layout.addLayout(yesNoLayout1, 5, 1, Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("Do you want bouts of movement to be detected?", self), font_size='16px'), 3, 0, Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(QLabel("Warning: at the moment, the parameters related to the bouts detection are a little challenging to set.", self), 4, 0, Qt.AlignmentFlag.AlignCenter)
    yesNoLayout2 = QHBoxLayout()
    yesNoLayout2.addStretch()
    btnGroup2 = QButtonGroup(self)
    yesBoutsRadioButton = QRadioButton("Yes", self)
    btnGroup2.addButton(yesBoutsRadioButton)
    yesBoutsRadioButton.setChecked(True)
    yesNoLayout2.addWidget(yesBoutsRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    noBoutsRadioButton = QRadioButton("No", self)
    btnGroup2.addButton(noBoutsRadioButton)
    yesNoLayout2.addWidget(noBoutsRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    yesNoLayout2.addStretch()
    layout.addLayout(yesNoLayout2, 5, 0, Qt.AlignmentFlag.AlignCenter)

    advancedOptionsLayout = QGridLayout()
    advancedOptionsLayout.addWidget(util.apply_style(QLabel("Do you want bends and associated paramaters to be calculated?", self), font_size='16px'), 0, 1, Qt.AlignmentFlag.AlignCenter)
    advancedOptionsLayout.addWidget(QLabel("Bends are the local minimum and maximum of the tail angle.", self), 1, 1, Qt.AlignmentFlag.AlignCenter)
    advancedOptionsLayout.addWidget(QLabel("Bends are used to calculate parameters such as tail beat frequency.", self), 2, 1, Qt.AlignmentFlag.AlignCenter)

    linkBtn1 = QPushButton("You may need to further adjust these parameters afterwards: see documentation.", self)

    linkBtn1.clicked.connect(lambda: webbrowser.open_new("https://zebrazoom.org/documentation/docs/configurationFile/advanced/angleSmoothBoutsAndBendsDetection"))
    advancedOptionsLayout.addWidget(linkBtn1, 3, 1, Qt.AlignmentFlag.AlignCenter)
    yesNoLayout3 = QHBoxLayout()
    yesNoLayout3.addStretch()

    btnGroup3 = QButtonGroup(self)
    yesBendsRadioButton = QRadioButton("Yes", self)
    btnGroup3.addButton(yesBendsRadioButton)
    yesBendsRadioButton.setChecked(True)
    yesNoLayout3.addWidget(yesBendsRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    noBendsRadioButton = QRadioButton("No", self)
    btnGroup3.addButton(noBendsRadioButton)
    yesNoLayout3.addWidget(noBendsRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    yesNoLayout3.addStretch()
    advancedOptionsLayout.addLayout(yesNoLayout3, 4, 1, Qt.AlignmentFlag.AlignCenter)

    advancedOptionsLayout.addWidget(util.apply_style(QLabel("Tail tracking: Choose an option below:", self), font_size='16px'), 0, 0, Qt.AlignmentFlag.AlignCenter)
    btnGroup4 = QButtonGroup(self)
    recommendedMethodRadioButton = QRadioButton("Recommended Method: Fast Tracking but tail tip might be detected too soon along the tail", self)
    btnGroup4.addButton(recommendedMethodRadioButton)
    recommendedMethodRadioButton.setChecked(True)
    advancedOptionsLayout.addWidget(recommendedMethodRadioButton, 1, 0, Qt.AlignmentFlag.AlignCenter)
    alternativeMethodRadioButton = QRadioButton("Alternative Method: Slower Tracker but tail tip MIGHT be detected more acurately", self)
    btnGroup4.addButton(alternativeMethodRadioButton)
    advancedOptionsLayout.addWidget(alternativeMethodRadioButton, 2, 0, Qt.AlignmentFlag.AlignCenter)
    label = util.apply_style(QLabel("Once your configuration is created, you can switch from one method to the other "
                                    "by changing the value of the parameter recalculateForegroundImageBasedOnBodyArea "
                                    "in your config file between 0 and 1.", self), font=QFont("Helvetica", 10))
    label.setWordWrap(True)
    advancedOptionsLayout.addWidget(label, 3, 0, 2, 1)

    advancedOptionsLayout.addWidget(util.apply_style(QLabel("Tracking: Choose an option below:", self), font_size='16px'), 5, 1, Qt.AlignmentFlag.AlignCenter)
    btnGroup5 = QButtonGroup(self)
    recommendedTrackingMethodRadioButton = QRadioButton("Recommended Method in most cases: Slower Tracking but often more accurate.", self)
    btnGroup5.addButton(recommendedTrackingMethodRadioButton)
    recommendedTrackingMethodRadioButton.setChecked(True)
    advancedOptionsLayout.addWidget(recommendedTrackingMethodRadioButton, 6, 1, Qt.AlignmentFlag.AlignCenter)
    alternativeTrackingMethodRadioButton = QRadioButton("Alternative Method: Faster tracking, sometimes less accurate.", self)
    btnGroup5.addButton(alternativeTrackingMethodRadioButton)
    advancedOptionsLayout.addWidget(alternativeTrackingMethodRadioButton, 7, 1, Qt.AlignmentFlag.AlignCenter)
    advancedOptionsLayout.addWidget(util.apply_style(QLabel("The alternative method can also work better for animals of different sizes.", self), font=QFont("Helvetica", 10)), 9, 1, Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.Expander(self, "Show advanced options", advancedOptionsLayout), 6, 0, 1, 2)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    nextBtn = util.apply_style(QPushButton("Ok, next step", self), background_color=util.LIGHT_YELLOW)
    nextBtn.clicked.connect(lambda: controller.numberOfAnimals(controller, nbanimals.text(), yesRadioButton.isChecked(), noRadioButton.isChecked(), 0, yesBoutsRadioButton.isChecked(), noBoutsRadioButton.isChecked(), recommendedMethodRadioButton.isChecked(), alternativeMethodRadioButton.isChecked(), yesBendsRadioButton.isChecked(), noBendsRadioButton.isChecked(), recommendedTrackingMethodRadioButton.isChecked()))
    buttonsLayout.addWidget(nextBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout, 7, 0, 1, 2)

    self.setLayout(layout)


class NumberOfAnimalsCenterOfMass(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (1152, 768)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("What's the total number of animals in your video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    nbanimals = QLineEdit(controller.window)
    nbanimals.setValidator(QIntValidator(nbanimals))
    nbanimals.validator().setBottom(0)
    layout.addWidget(nbanimals, alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("Are all of those animals ALWAYS visible throughout the video?", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    yesRadioButton = QRadioButton("Yes", self)
    yesRadioButton.setChecked(True)
    layout.addWidget(yesRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    noRadioButton = QRadioButton("No", self)
    layout.addWidget(noRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)

    method1Btn = QPushButton("Automatic Parameters Setting, Method 1: Slower tracking but often more accurate", self)
    method1Btn.clicked.connect(lambda: controller.numberOfAnimals(controller, nbanimals.text(), yesRadioButton.isChecked(), noRadioButton.isChecked(), 0, 0, 0, 1, 0, 0, 0, 1))
    layout.addWidget(method1Btn, alignment=Qt.AlignmentFlag.AlignCenter)
    method2Btn = QPushButton("Automatic Parameters Setting, Method 2: Faster tracking but often less accurate", self)
    method2Btn.clicked.connect(lambda: controller.numberOfAnimals(controller, nbanimals.text(), yesRadioButton.isChecked(), noRadioButton.isChecked(), 0, 0, 0, 1, 0, 0, 0, 0))
    layout.addWidget(method2Btn, alignment=Qt.AlignmentFlag.AlignCenter)
    manualBtn = QPushButton("Manual Parameters Setting: More control over the choice of parameters", self)
    manualBtn.clicked.connect(lambda: controller.numberOfAnimals(controller, nbanimals.text(), yesRadioButton.isChecked(), noRadioButton.isChecked(), 0, 0, 0, 0, 1, 0, 0, 0))
    layout.addWidget(manualBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Try the 'Automatic Parameters Setting, Method 1' first. If it doesn't work, try the other methods.", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("The 'Manual Parameter Settings' makes setting parameter slightly more challenging but offers more control over the choice of parameters.", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class IdentifyHeadCenter(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    button = QPushButton("Click on the center of the head of a zebrafish", self)
    button.clicked.connect(lambda: controller.chooseHeadCenter(controller))
    layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Example:", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    image = QLabel(self)
    image.setPixmap(QPixmap(os.path.join(cur_dir_path, 'blobCenter.png')))
    layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class IdentifyBodyExtremity(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    button = QPushButton("Click on the tip of the tail of the same zebrafish.", self)
    button.clicked.connect(lambda: controller.chooseBodyExtremity(controller))
    layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(util.apply_style(QLabel("Example:", self), font=QFont("Helvetica", 10)), alignment=Qt.AlignmentFlag.AlignCenter)
    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    image = QLabel(self)
    image.setPixmap(QPixmap(os.path.join(cur_dir_path, 'blobExtremity.png')))
    layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class GoToAdvanceSettings(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (450, 300)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Prepare Config File", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(util.apply_style(QLabel("Do you want to detect bouts movements and/or further adjust tracking parameters?", self), font=QFont("Helvetica", 12)), alignment=Qt.AlignmentFlag.AlignCenter)
    yesRadioButton = QRadioButton("Yes", self)
    yesRadioButton.setChecked(True)
    layout.addWidget(yesRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)
    noRadioButton = QRadioButton("No", self)
    layout.addWidget(noRadioButton, alignment=Qt.AlignmentFlag.AlignCenter)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    nextBtn = util.apply_style(QPushButton("Next", self), background_color=util.LIGHT_YELLOW)
    nextBtn.clicked.connect(lambda: controller.goToAdvanceSettings(controller, yesRadioButton.isChecked(), noRadioButton.isChecked()))
    buttonsLayout.addWidget(nextBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)


class FinishConfig(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller

    layout = QVBoxLayout()
    layout.addStretch()
    testCheckbox = QCheckBox("Test tracking after saving config", self)
    testCheckbox.setChecked(True)
    testCheckbox.clearFocus()
    layout.addWidget(testCheckbox, alignment=Qt.AlignmentFlag.AlignCenter)
    saveBtn = util.apply_style(QPushButton("Save Config File", self), background_color=util.LIGHT_YELLOW)
    saveBtn.clicked.connect(lambda: controller.finishConfig(testCheckbox.isChecked()))
    layout.addWidget(saveBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    backBtn = util.apply_style(QPushButton("Back", self), background_color=util.LIGHT_YELLOW)
    backBtn.setObjectName("back")
    buttonsLayout.addWidget(backBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    startPageBtn = util.apply_style(QPushButton("Go to the start page", self), background_color=util.LIGHT_CYAN)
    startPageBtn.clicked.connect(lambda: controller.show_frame("StartPage"))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)
