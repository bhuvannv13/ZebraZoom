import contextlib
import copy
import json
import os

import pandas as pd

from PyQt5.QtCore import pyqtSignal, Qt, QAbstractTableModel, QDir, QEvent, QItemSelection, QItemSelectionModel, QModelIndex, QObject, QPoint, QPointF, QRect, QRectF, QSize, QSizeF, QSortFilterProxyModel, QUrl
from PyQt5.QtGui import QColor, QDesktopServices, QFont, QPainter, QPixmap, QPolygon, QPolygonF, QTransform
from PyQt5.QtWidgets import QAbstractItemView, QApplication, QFileDialog, QFileSystemModel, QFrame, QHBoxLayout, QHeaderView, QLabel, QListView, QMessageBox, QPushButton, QScrollArea, QSlider, QSpacerItem, QStyleOptionSlider, QTableView, QTextEdit, QTreeView, QToolTip, QVBoxLayout, QWidget

import zebrazoom.code.paths as paths
import zebrazoom.code.util as util
from zebrazoom.code.readValidationVideo import getFramesCallback


class RolloverAnalysis(QWidget):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self.preferredSize = (900, 450)

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Zebrafish rollover analysis", self), font=controller.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    detectionBtn = util.apply_style(QPushButton("Rollover detection", self), background_color=util.LIGHT_YELLOW)
    detectionBtn.clicked.connect(_showTemporaryPage)
    layout.addWidget(detectionBtn, alignment=Qt.AlignmentFlag.AlignCenter)

    classificationBtn = util.apply_style(QPushButton("Manual rollover classification", self), background_color=util.LIGHT_YELLOW)
    classificationBtn.clicked.connect(lambda: controller.showManualRolloverClassification())
    layout.addWidget(classificationBtn, alignment=Qt.AlignmentFlag.AlignCenter)

    start_page_btn = QPushButton("Go to the start page", self)
    start_page_btn.clicked.connect(lambda: controller.show_frame("StartPage"))
    layout.addWidget(start_page_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    self.setLayout(layout)


class _ConfigurationsModel(QFileSystemModel):
  def __init__(self):
    super().__init__()
    self.setReadOnly(False)
    self.setNameFilterDisables(False)
    self.setNameFilters(("*.csv",))

  def data(self, index, role=Qt.ItemDataRole.DisplayRole):
    data = super().data(index, role=role)
    if role == Qt.ItemDataRole.EditRole:
      return os.path.splitext(data)[0]
    return data

  def setData(self, index, value, role=None):
    extension = os.path.splitext(self.data(index))[1]
    return super().setData(index, "%s%s" % (value, extension), role=role)


class _ConfigurationsTreeView(QTreeView):
  def __init__(self):
    super().__init__()
    self.sizeHint = lambda: QSize(150, 1)
    self.header().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    self.setRootIsDecorated(False)

  def resizeEvent(self, evt):
    super().resizeEvent(evt)
    self.setColumnWidth(0, evt.size().width())

  def flags(self, index):
    return super().flags(index) | Qt.ItemFlag.ItemIsEditable


class _ResultsModel(QAbstractTableModel):
  _COLUMN_TITLES = ["Video", "Config"]
  _DEFAULT_ZZOUTPUT = paths.getDefaultZZoutputFolder()

  def __init__(self, filename):
    super().__init__()
    data = pd.read_csv(filename).fillna('')
    self._videos = data['Video'].tolist()
    self._configs = data['Config'].tolist()

  def rowCount(self, parent=None):
    return len(self._videos)

  def columnCount(self, parent=None):
    return len(self._COLUMN_TITLES)

  def data(self, index, role=Qt.ItemDataRole.DisplayRole):
    if index.isValid() and role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.ToolTipRole):
      return self._videos[index.row()] if index.column() == 0 else self._configs[index.row()]
    return None

  def headerData(self, col, orientation, role):
    if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
      return self._COLUMN_TITLES[col]
    return None

  def addVideos(self, videos):
    if videos is None:
      return
    videos = [video for video in videos if video not in self._videos]
    self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + len(videos) - 1)
    self._videos.extend(videos)
    self._configs.extend([''] * len(videos))
    self.endInsertRows()

  def setConfigs(self, idxs, config):
    if config is None:
      return
    self.beginResetModel()
    for idx in idxs:
      self._configs[idx] = config
    self.endResetModel()

  def removeSelectedRows(self, idxs):
    self.beginResetModel()
    for idx in reversed(sorted(idxs)):
      del self._videos[idx]
      del self._configs[idx]
    self.endResetModel()

  def getData(self):
    return self._videos, self._configs

  def hasUnsavedChanges(self, filename):
    if not os.path.exists(filename):  # file was deleted
      return False
    fileData = pd.read_csv(filename).fillna('')
    return not (fileData['Video'].tolist() == self._videos and fileData['Config'].tolist() == self._configs)

  def saveFile(self, filename):
    pd.DataFrame(columns=_ResultsModel._COLUMN_TITLES, data=zip(self._videos, self._configs)).to_csv(filename, index=False)


class _ConfigurationsSelectionModel(QItemSelectionModel):
  def __init__(self, window, table, *args):
    super().__init__(*args)
    self._window = window
    self._table = table
    self._blockSelection = False

  def setCurrentIndex(self, index, command):
    if index != self.currentIndex() and self._table.model() is not None and self._table.model().hasUnsavedChanges(self.model().filePath(self.currentIndex())) and \
        QMessageBox.question(self._window, "Unsaved changes", "Are you sure you want to proceed? Unsaved changes will be lost.",
                             defaultButton=QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
      self._blockSelection = True
      return None
    return super().setCurrentIndex(index, command)

  def select(self, index, command):
    if self._blockSelection:
      self._blockSelection = False
      return None
    return super().select(index, command)


class _ResultsSelectionPage(QWidget):
  def __init__(self):
    super().__init__()

    app = QApplication.instance()

    layout = QVBoxLayout()
    layout.addWidget(util.apply_style(QLabel("Select results and corresponding rollover config files"), font=app.title_font), alignment=Qt.AlignmentFlag.AlignCenter)

    folderPath = os.path.join(paths.getRootDataFolder(), 'rolloverConfigurations')
    if not os.path.exists(folderPath):
      os.makedirs(folderPath)
    model = _ConfigurationsModel()
    model.setRootPath(folderPath)
    self._tree = tree = _ConfigurationsTreeView()
    tree.setModel(model)
    for idx in range(1, model.columnCount()):
      tree.hideColumn(idx)
    tree.setRootIndex(model.index(model.rootPath()))
    self._table = QTableView()
    selectionModel = _ConfigurationsSelectionModel(app.window, self._table, model)
    tree.setSelectionModel(selectionModel)
    selectionModel.currentRowChanged.connect(lambda current, previous: current.row() == -1 or self._fileSelected(model.filePath(current)))

    treeLayout = QVBoxLayout()
    self._newConfigurationBtn = QPushButton("New configuration")
    self._newConfigurationBtn.clicked.connect(self._newConfiguration)
    treeLayout.addWidget(self._newConfigurationBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    treeLayout.addWidget(tree, stretch=1)
    treeWidget = QWidget()
    treeLayout.setContentsMargins(0, 0, 0, 0)
    treeWidget.setLayout(treeLayout)
    horizontalSplitter = util.CollapsibleSplitter()
    horizontalSplitter.addWidget(treeWidget)

    tableLayout = QVBoxLayout()
    tableButtonsLayout = QHBoxLayout()
    self._addMultipleFoldersBtn = QPushButton("Add results folders")
    self._addMultipleFoldersBtn.clicked.connect(self._addMultipleFolders)
    tableButtonsLayout.addWidget(self._addMultipleFoldersBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    chooseConfigsBtn = QPushButton("Choose config for selected results")
    chooseConfigsBtn.clicked.connect(lambda: self._table.model().setConfigs(sorted(set(map(lambda idx: idx.row(), self._table.selectionModel().selectedIndexes()))),
                                                                           QFileDialog.getOpenFileName(app.window, 'Select config file', paths.getConfigurationFolder(), "JSON (*.json)")[0]))
    tableButtonsLayout.addWidget(chooseConfigsBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    removeVideosBtn = QPushButton("Remove selected results")
    removeVideosBtn.clicked.connect(lambda: self._table.model().removeSelectedRows(sorted(set(map(lambda idx: idx.row(), self._table.selectionModel().selectedIndexes())))))
    tableButtonsLayout.addWidget(removeVideosBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    saveChangesBtn = QPushButton("Save changes")
    saveChangesBtn.clicked.connect(lambda: self._table.model().saveFile(self._tree.model().filePath(selectionModel.currentIndex())) or QMessageBox.information(app.window, "Configuration saved", "Changes made to the configuration were saved."))
    tableButtonsLayout.addWidget(saveChangesBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    deleteConfigurationBtn = QPushButton("Delete configuration")
    deleteConfigurationBtn.clicked.connect(self._removeConfiguration)
    tableButtonsLayout.addWidget(deleteConfigurationBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    openConfigurationsFolderBtn = QPushButton("Open configurations folder")
    openConfigurationsFolderBtn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(folderPath)))
    tableButtonsLayout.addWidget(openConfigurationsFolderBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    self._runTrackingBtn = util.apply_style(QPushButton("Run tracking"), background_color=util.DEFAULT_BUTTON_COLOR)
    self._runTrackingBtn.clicked.connect(self._unsavedChangesWarning(lambda *_: self._runTracking(), forceSave=True))
    tableButtonsLayout.addWidget(self._runTrackingBtn, alignment=Qt.AlignmentFlag.AlignLeft)
    tableButtonsLayout.addStretch()
    tableLayout.addLayout(tableButtonsLayout)
    tableLayout.addWidget(self._table, stretch=1)

    self._mainWidget = QWidget()
    tableLayout.setContentsMargins(0, 0, 0, 0)
    self._mainWidget.setLayout(tableLayout)

    scrollArea = QScrollArea()
    scrollArea.setFrameShape(QFrame.Shape.NoFrame)
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(self._mainWidget)
    horizontalSplitter.addWidget(scrollArea)
    horizontalSplitter.setStretchFactor(1, 1)
    horizontalSplitter.setChildrenCollapsible(False)
    layout.addWidget(horizontalSplitter, stretch=1)

    buttonsLayout = QHBoxLayout()
    buttonsLayout.addStretch()
    startPageBtn = QPushButton("Go to the start page")
    startPageBtn.clicked.connect(self._unsavedChangesWarning(lambda *_: app.show_frame("StartPage")))
    buttonsLayout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)
    buttonsLayout.addStretch()
    layout.addLayout(buttonsLayout)

    self.setLayout(layout)
    self._mainWidget.hide()

  def _findResultsFile(self, path):
    if not os.path.exists(path):
      return None
    folder = os.path.basename(path)
    reference = os.path.join(path, 'results_' + folder + '.txt')
    if os.path.exists(reference):
      return reference
    resultsFile = next((f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) if f.startswith('results_')), None)
    if resultsFile is None:
      return None
    return os.path.join(path, resultsFile)

  def _getMultipleFolders(self):
    app = QApplication.instance()
    dialog = QFileDialog()
    dialog.setWindowTitle('Select one or more results folders (use Ctrl or Shift key to select multiple folders)')
    dialog.setDirectory(app.ZZoutputLocation)
    dialog.setFileMode(QFileDialog.FileMode.Directory)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
    listView = dialog.findChild(QListView, 'listView')
    if listView:
      listView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    treeView = dialog.findChild(QTreeView)
    if treeView:
      treeView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    if not dialog.exec():
      return None
    return dialog.selectedFiles()

  @contextlib.contextmanager
  def __selectAddedRows(self):
    app = QApplication.instance()
    model = self._table.model()
    firstNewRow = model.rowCount()
    yield
    if firstNewRow == model.rowCount():
      return  # no videos added
    addedRows = QItemSelection()
    addedRows.select(model.index(firstNewRow, 0), model.index(model.rowCount() - 1, 0))
    self._table.selectionModel().setCurrentIndex(model.index(firstNewRow, 0), QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
    self._table.selectionModel().select(addedRows, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)
    self._table.setFocus()

  def _addMultipleFolders(self):
    selectedFolders = self._getMultipleFolders()
    if selectedFolders is None:
      return
    invalidFolders = []
    for selectedFolder in selectedFolders:
      if self._findResultsFile(selectedFolder) is None:
        invalidFolders.append(selectedFolder)
        continue
    with self.__selectAddedRows():
      self._table.model().addVideos([os.path.normpath(path) for path in selectedFolders if path not in invalidFolders])
    if invalidFolders:
      app = QApplication.instance()
      warning = QMessageBox(app.window)
      warning.setIcon(QMessageBox.Icon.Warning)
      warning.setWindowTitle("Invalid folders selected")
      warning.setText("Some of the selected folders were ignored because they are not valid results folders.")
      warning.setDetailedText("\n".join(invalidFolders))
      warning.exec()

  def _unsavedChangesWarning(self, fn, forceSave=False):
    app = QApplication.instance()
    def inner(*args, **kwargs):
      if forceSave:
        text = "Do you want to save the changes and proceed?"
      else:
        text = "Are you sure you want to proceed? Unsaved changes will be lost."
      filename = self._tree.model().filePath(self._tree.selectionModel().currentIndex())
      if self._table.model() is not None and self._table.model().hasUnsavedChanges(filename):
        if QMessageBox.question(app.window, "Unsaved changes", text, defaultButton=QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
          return
        elif forceSave:
          self._table.model().saveFile(filename)
      return fn(*args, **kwargs)
    return inner

  def _newConfiguration(self):
    number = 1
    while os.path.exists(os.path.join(self._tree.model().rootPath(), 'Configuration %d.csv' % number)):
      number += 1
    path = os.path.join(self._tree.model().rootPath(), 'Configuration %d.csv' % number)
    pd.DataFrame(columns=_ResultsModel._COLUMN_TITLES).to_csv(path, index=False)
    index = self._tree.model().index(path)
    self._tree.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
    self._tree.edit(index)

  def _removeConfiguration(self):
    app = QApplication.instance()
    if QMessageBox.question(app.window, "Delete configuration", "Are you sure you want to delete the configuration? This action removes the file from disk and cannot be undone.",
                            defaultButton=QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
      return
    pathToRemove = self._tree.model().filePath(self._tree.selectionModel().currentIndex())
    self._tree.model().remove(self._tree.selectionModel().currentIndex())
    if pathToRemove == self._tree.model().filePath(self._tree.selectionModel().currentIndex()):  # last valid file removed
      self._mainWidget.hide()

  def _fileSelected(self, filename):
    self._mainWidget.show()
    self._table.setModel(_ResultsModel(filename))
    self._table.horizontalHeader().resizeSections(QHeaderView.ResizeMode.Stretch)

  @util.showInProgressPage('Detecting rollover')
  def __run(self, results, configs):
    from zzdeeprollover.detectRolloverFrames import detectRolloverFrames
    app = QApplication.instance()
    for resultsFolder, config in zip(results, configs):
      comparePredictedWithManual = os.path.exists(os.path.join(resultsFolder, 'rolloverManualClassification.json'))
      detectRolloverFrames(os.path.basename(resultsFolder), os.path.dirname(resultsFolder), config['medianRollingMean'], config['resizeCropDimension'], comparePredictedWithManual, 1, config['imagesToClassifyHalfDiameter'], config['modelPath'])
    QMessageBox.information(app.window, "Rollover detection done", "Rollover detection was completed successfully.")

  def _runTracking(self):
    app = QApplication.instance()
    results, configs = self._table.model().getData()
    errors = []
    loadedConfigs = []
    for resultsFolder, config in zip(results, configs):
      if not config:
        errors.append('Config is not specified for video %s.' % video)
      elif not os.path.exists(config):
        errors.append('Config %s does not exist.' % config)
      else:
        with open(config) as f:
          loadedConfig = json.load(f)
          loadedConfigs.append(loadedConfig)
        expectedKeys = {'medianRollingMean', 'resizeCropDimension', 'imagesToClassifyHalfDiameter', 'modelPath'}
        if set(loadedConfig) != expectedKeys:
          errors.append(f'Config {config} contains invalid keys. Expected keys are {", ".join(expectedKeys)}.')
      if not os.path.exists(resultsFolder):
        errors.append(f'Folder {resultsFolder} does not exist.')
      if self._findResultsFile(resultsFolder) is None:
        errors.append(f'Folder {resultsFolder} is not a valid results folder.')
    if errors:
      error = QMessageBox(app.window)
      error.setIcon(QMessageBox.Icon.Critical)
      error.setWindowTitle("Specification contains some errors")
      error.setText("Cannot detect rollovers because the specified results and config combinations contain some errors:")
      error.setDetailedText("\n".join(errors))
      textEdit = error.findChild(QTextEdit)
      textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
      layout = error.layout()
      layout.addItem(QSpacerItem(600, 0), layout.rowCount(), 0, 1, layout.columnCount())
      error.exec()
      return
    self.__run(results, loadedConfigs)


def _showTemporaryPage():
  app = QApplication.instance()
  layout = app.window.centralWidget().layout()
  page = _ResultsSelectionPage()
  layout.addWidget(page)
  layout.setCurrentWidget(page)
  def cleanup():
    layout.removeWidget(page)
    layout.currentChanged.disconnect(cleanup)
  layout.currentChanged.connect(cleanup)


class _TooltipHelper(QObject):
  def eventFilter(self, obj, evt):
    if evt.type() != QEvent.Type.ToolTip:
      return False
    view = obj.parent()
    if view is None:
      return False

    index = view.indexAt(evt.pos())
    if not index.isValid():
      return False
    rect = view.visualRect(index)
    if view.sizeHintForColumn(index.column()) > rect.width():
      QToolTip.showText(evt.globalPos(), view.model().data(index), view, rect)
      return True
    else:
      QToolTip.hideText()
      return True
    return False


class _WellSelectionLabel(QLabel):
  wellChanged = pyqtSignal(int)

  def __init__(self):
    super().__init__()
    self._well = None
    self._hoveredWell = None
    self._wellPositions = None
    self._size = None
    self._originalPixmap = None
    self.wellShape = None

  def setWellPositions(self, wellPositions):
    self.setMouseTracking(wellPositions is not None)
    self._wellPositions = wellPositions
    self._well = 0
    self.wellChanged.emit(self._well)
    self.update()

  def setOriginalPixmap(self, pixmap, update=True):
    self._originalPixmap = pixmap
    if update:
      self._well = 0
      if pixmap is not None:
        self.setMaximumSize(pixmap.size())
        self.setMinimumSize(300, 300)
        self.setPixmap(pixmap)
        self.hide()
        self.show()
    self._updateImage()

  def mouseMoveEvent(self, evt):
    app = QApplication.instance()
    if not self._wellPositions:
      return
    oldHovered = self._hoveredWell
    if self.wellShape == 'rectangle':
      def test_func(shape, x, y, width, height):
        if isinstance(shape, QPoint):
          return QRect(x, y, width, height).contains(shape)
        else:
          assert isinstance(shape, QRect)
          return QRect(x, y, width, height).intersects(shape)
    else:
      assert self.wellShape == 'circle'
      def test_func(shape, x, y, width, height):
        if isinstance(shape, QPoint):
          radius = width / 2
          centerX = x + radius
          centerY = y + radius
          dx = abs(shape.x() - centerX)
          if dx > radius:
            return False
          dy = abs(shape.y() - centerY)
          if dy > radius:
            return False
          if dx + dy <= radius:
            return True
          return dx * dx + dy * dy <= radius * radius
        else:
          radius = width / 2
          centerX = x + radius
          centerY = y + radius
          Dx = max(shape.x(), min(centerX, shape.x() + shape.width())) - centerX
          Dy = max(shape.y(), min(centerY, shape.y() + shape.height())) - centerY
          return (Dx ** 2 + Dy ** 2) <= radius ** 2

    self._hoveredWell = None
    for idx, positions in enumerate(self._wellPositions):
      point = self._transformToOriginal.map(evt.pos())
      if test_func(point, *positions):
        self._hoveredWell = idx
        break
    if self._hoveredWell != oldHovered:
      self.update()

  def mousePressEvent(self, evt):
    if not self._wellPositions or self._hoveredWell is None:
      return
    if self._well != self._hoveredWell:
      self._well = self._hoveredWell
      self.wellChanged.emit(self._well)
      self.update()

  def enterEvent(self, evt):
    QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)

  def leaveEvent(self, evt):
    QApplication.restoreOverrideCursor()
    self._hoveredWell = None
    self.update()

  def paintEvent(self, evt):
    super().paintEvent(evt)
    app = QApplication.instance()
    if not self._wellPositions:
      return
    qp = QPainter()
    qp.begin(self)
    factory = qp.drawRect if self.wellShape == 'rectangle' else qp.drawEllipse
    for idx, positions in enumerate(self._wellPositions):
      if idx == self._well:
        qp.setPen(QColor(255, 0, 0))
      elif idx == self._hoveredWell:
        qp.setPen(QColor(0, 255, 0))
      else:
        qp.setPen(QColor(0, 0, 255))
      rect = self._transformFromOriginal.map(QPolygon(QRect(*positions))).boundingRect()
      font = QFont()
      font.setPointSize(16)
      font.setWeight(QFont.Weight.Bold)
      qp.setFont(font)
      qp.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(idx))
      factory(rect)
    qp.end()

  def _updateImage(self):
    self._size = self.size()
    if self._originalPixmap is None:
      self.clear()
      return
    originalRect = QRectF(QPointF(0, 0), QSizeF(self._originalPixmap.size()))
    currentRect = QRectF(QPointF(0, 0), QSizeF(self._size))
    self._transformToOriginal = QTransform()
    QTransform.quadToQuad(QPolygonF((currentRect.topLeft(), currentRect.topRight(), currentRect.bottomLeft(), currentRect.bottomRight())),
                          QPolygonF((originalRect.topLeft(), originalRect.topRight(), originalRect.bottomLeft(), originalRect.bottomRight())),
                          self._transformToOriginal)
    self._transformFromOriginal = QTransform()
    QTransform.quadToQuad(QPolygonF((originalRect.topLeft(), originalRect.topRight(), originalRect.bottomLeft(), originalRect.bottomRight())),
                          QPolygonF((currentRect.topLeft(), currentRect.topRight(), currentRect.bottomLeft(), currentRect.bottomRight())),
                          self._transformFromOriginal)
    scaling = self.devicePixelRatioF()
    size = self._originalPixmap.size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
    img = self._originalPixmap.scaled(int(size.width() * scaling), int(size.height() * scaling))
    img.setDevicePixelRatio(scaling)
    self.setPixmap(img)
    blocked = self.blockSignals(True)
    self.setMinimumSize(size)
    self.setMaximumSize(size)
    self.blockSignals(blocked)

  def resizeEvent(self, evt):
    super().resizeEvent(evt)
    self._updateImage()

  def getWell(self):
    return self._well if self._wellPositions is not None else 0

  def totalWells(self):
    return len(self._wellPositions) if self._wellPositions is not None else 1


class RolloverSlider(QSlider):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.rolloverRanges = []
    self.inBetweenRanges = []

  def paintEvent(self, event):
    style = self.style()
    opt = QStyleOptionSlider()
    self.initStyleOption(opt)
    available = style.pixelMetric(style.PM_SliderSpaceAvailable, opt, self)
    minimum = self.minimum()
    maximum = self.maximum()
    qp = QPainter(self)
    qp.translate(opt.rect.x(), opt.rect.y())
    for color, frameRange in zip((QColor('red'), QColor('blue')), (self.rolloverRanges, self.inBetweenRanges)):
      for start, end in frameRange:
        start = style.sliderPositionFromValue(minimum, maximum, start, available, opt.upsideDown)
        end = style.sliderPositionFromValue(minimum, maximum, end, available, opt.upsideDown)
        qp.fillRect(start, 0, end - start + 1, event.rect().height(), color)
    super().paintEvent(event)


class ManualRolloverClassification(util.CollapsibleSplitter):
  def __init__(self, controller):
    super().__init__(controller.window)
    self.controller = controller
    self._rolloverClassification = {}

    model = QFileSystemModel()
    model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.Dirs)
    model.setRootPath(self.controller.ZZoutputLocation)
    model.setReadOnly(True)
    proxyModel = QSortFilterProxyModel()

    def filterModel(row, parent):
      index = model.index(row, 0, parent)
      if os.path.normpath(model.filePath(index)) == os.path.normpath(self.controller.ZZoutputLocation):
        return True
      return bool(self._findResultsFile(model.fileName(index)))
    proxyModel.filterAcceptsRow = filterModel
    proxyModel.setSourceModel(model)
    self._tree = tree = QTreeView()
    tree.viewport().installEventFilter(_TooltipHelper(tree))
    tree.sizeHint = lambda: QSize(150, 1)
    tree.setModel(proxyModel)
    tree.setRootIsDecorated(False)
    tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    for idx in range(1, model.columnCount()):
      tree.hideColumn(idx)
    tree.resizeEvent = lambda evt: tree.setColumnWidth(0, evt.size().width())
    selectionModel = tree.selectionModel()
    selectionModel.currentRowChanged.connect(lambda current, previous: current.row() == -1 or self.setFolder(model.fileName(current)))

    layout = QVBoxLayout()
    self._title_label = util.apply_style(QLabel('', self), font_size='16px')
    layout.addWidget(self._title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    self._frame = frame = _WellSelectionLabel()
    frame.wellChanged.connect(self._wellSelected)
    layout.addWidget(frame, stretch=1)
    self._slider = slider = RolloverSlider(Qt.Orientation.Horizontal)
    slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    slider.setPageStep(50)
    self._getFrame = lambda *args: None
    slider.valueChanged.connect(lambda: frame.setOriginalPixmap(QPixmap(util._cvToPixmap(self._getFrame(slider))), update=False))
    layout.addWidget(slider)

    layout.addWidget(QLabel('<span style="color:red">Rollover ranges are marked with red,</span> <span style="color:blue">in between are marked with blue.</span>'), alignment=Qt.AlignmentFlag.AlignCenter)

    self._currentRange = None
    currentRangeIdx = None
    slider.valueChanged.connect(lambda value: updateRollover(value))
    rolloverLayout = QHBoxLayout()

    def getRange(frame, ranges):
      for idx, (start, end) in enumerate(ranges):
        if start <= frame <= end:
          return (start, end), idx
      return None, None

    def updateRollover(frame):
      nonlocal currentRangeIdx
      if self._currentRange is not None:
        self._currentRange[1] = frame
        return
      rolloverButton.setEnabled(True)
      inBetweenButton.setEnabled(True)
      rolloverRange, currentRangeIdx = getRange(frame, slider.rolloverRanges)
      if rolloverRange is not None:
        start, end = rolloverRange
        rolloverButton.setText(f'Unmark rollover range [{start}, {end}]')
        inBetweenButton.setEnabled(False)
        return
      else:
        rolloverButton.setText('Start marking rollover')
      inBetweenRange, currentRangeIdx = getRange(frame, slider.inBetweenRanges)
      if inBetweenRange is not None:
        start, end = inBetweenRange
        inBetweenButton.setText(f'Unmark in between range [{start}, {end}]')
        rolloverButton.setEnabled(False)
      else:
        inBetweenButton.setText('Start marking in between')

    def btnClicked(btn, data):
      currentFrame = slider.value()
      if currentRangeIdx is not None:
        del data[currentRangeIdx]
        slider.update()
        saveButton.setEnabled(self._originalRolloverClassification != self._rolloverClassification)
      elif self._currentRange is None:
        btn.setText(btn.text().replace('Start', 'Stop'))
        self._currentRange = [currentFrame, currentFrame]
        data.append(self._currentRange)
      else:
        self._currentRange.sort()
        data.sort()
        self._currentRange = None
        saveButton.setEnabled(self._originalRolloverClassification != self._rolloverClassification)
      updateRollover(currentFrame)

    rolloverButton = QPushButton('Start marking rollover')
    rolloverButton.clicked.connect(lambda: btnClicked(rolloverButton, slider.rolloverRanges))
    rolloverLayout.addWidget(rolloverButton, alignment=Qt.AlignmentFlag.AlignCenter)
    inBetweenButton = QPushButton('Start marking in between')
    inBetweenButton.clicked.connect(lambda: btnClicked(inBetweenButton, slider.inBetweenRanges))
    rolloverLayout.addWidget(inBetweenButton, alignment=Qt.AlignmentFlag.AlignCenter)

    def saveRolloverClassification():
      with open(self._rolloverClassificationPath, 'w') as f:
        json.dump(self._rolloverClassification, f, indent=2)
      saveButton.setEnabled(False)

    self._saveButton = saveButton = QPushButton('Save changes')
    saveButton.setEnabled(False)
    saveButton.clicked.connect(saveRolloverClassification)
    rolloverLayout.addWidget(saveButton, alignment=Qt.AlignmentFlag.AlignCenter)
    rolloverWidget = QWidget()
    rolloverWidget.setLayout(rolloverLayout)
    layout.addWidget(rolloverWidget, alignment=Qt.AlignmentFlag.AlignCenter)

    startPageBtn = QPushButton("Go to the start page", self)
    startPageBtn.clicked.connect(lambda: self.setFolder(None) or controller.show_frame("StartPage"))
    layout.addWidget(startPageBtn, alignment=Qt.AlignmentFlag.AlignCenter)

    centralWidget = QWidget()
    centralWidget.setLayout(layout)
    self.addWidget(tree)
    self._centralWidget = wrapperWidget = QWidget()
    wrapperLayout = QHBoxLayout()
    wrapperLayout.addWidget(centralWidget, alignment=Qt.AlignmentFlag.AlignCenter)
    wrapperWidget.setLayout(wrapperLayout)
    wrapperWidget.showChildren = lambda: [child.show() for child in centralWidget.findChildren(QWidget) if child is not startPageBtn]
    wrapperWidget.hideChildren = lambda: [child.hide() for child in centralWidget.findChildren(QWidget) if child is not startPageBtn]
    scrollArea = QScrollArea()
    scrollArea.setFrameShape(QFrame.Shape.NoFrame)
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(wrapperWidget)
    self.addWidget(scrollArea)
    self.setStretchFactor(1, 1)
    self.setChildrenCollapsible(False)
    wrapperWidget.hideChildren()

  def _wellSelected(self, idx):
    self._slider.rolloverRanges = self._rolloverClassification[f'{idx + 1}']['rollover']
    self._slider.inBetweenRanges = self._rolloverClassification[f'{idx + 1}']['inBetween']
    self._slider.valueChanged.emit(self._slider.value())
    self._slider.update()

  def _findResultsFile(self, folder):
    reference = os.path.join(self.controller.ZZoutputLocation, os.path.join(folder, 'results_' + folder + '.txt'))
    if os.path.exists(reference):
      return reference
    mypath = os.path.join(self.controller.ZZoutputLocation, folder)
    if not os.path.exists(mypath):
      return None
    resultsFile = next((f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f)) and f.startswith('results_')), None)
    if resultsFile is None:
      return None
    return os.path.join(self.controller.ZZoutputLocation, os.path.join(folder, resultsFile))

  def setFolder(self, name):
    self._currentRange = None
    self._title_label.setText(name)
    if name is None:
      self._tree.hide()
      filesystemModel = self._tree.model().sourceModel()
      filesystemModel.setRootPath(None)
      filesystemModel.setRootPath(self.controller.ZZoutputLocation)  # force refresh of the model
      self._tree.setRootIndex(self._tree.model().mapFromSource(filesystemModel.index(filesystemModel.rootPath())))
      self._centralWidget.hideChildren()
      self._tree.selectionModel().reset()
      self._tree.show()
      return
    else:
      self._getFrame, frameRange, _, toggleTrackingPoints, wellPositions, wellShape = getFramesCallback('', name, '', -1, 0, False, 0, ZZoutputLocation=self.controller.ZZoutputLocation)

      self._rolloverClassificationPath = os.path.join(self.controller.ZZoutputLocation, name, 'rolloverManualClassification.json')
      if os.path.exists(self._rolloverClassificationPath):
        with open(self._rolloverClassificationPath) as f:
          self._rolloverClassification = json.load(f)
        self._saveButton.setEnabled(False)
      else:
        self._rolloverClassification = {str(wellIdx + 1): {"rollover": [], "inBetween": []} for wellIdx in range(len(wellPositions))}
        self._saveButton.setEnabled(True)
      self._originalRolloverClassification = copy.deepcopy(self._rolloverClassification)

      self._centralWidget.hideChildren()

      self._slider.setRange(*frameRange)
      self._slider.setValue(self._slider.minimum())

      self._frame.setOriginalPixmap(QPixmap(util._cvToPixmap(self._getFrame(self._slider))))
      if wellShape is None:
        self._frame.wellShape = None
        self._frame.setWellPositions(None)
      else:
        self._frame.wellShape = wellShape
        self._frame.setWellPositions([(position['topLeftX'], position['topLeftY'], position['lengthX'], position['lengthY'])
                                      for idx, position in enumerate(wellPositions)])

      self._centralWidget.showChildren()
