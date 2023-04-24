import argparse
import os
import sys
import multiprocessing
multiprocessing.freeze_support()  # documentation mistakenly states this is required only on Windows; it's also required on Mac and does nothing on Linux

import zebrazoom.code.paths as paths


class _Subcommands:
  @staticmethod
  def launchZebraZoom(args):
      from zebrazoom.GUIAllPy import ZebraZoomApp
      print("The data produced by ZebraZoom can be found in the folder: " + paths.getDefaultZZoutputFolder())
      app = ZebraZoomApp(sys.argv)
      sys.exit(app.exec())

  @staticmethod
  def selectZZoutput(args):
    from zebrazoom.GUIAllPy import ZebraZoomApp
    app = ZebraZoomApp(sys.argv)
    print("The data produced by ZebraZoom can be found in the folder: " + paths.getDefaultZZoutputFolder())
    app.askForZZoutputLocation()
    sys.exit(app.exec())

  @staticmethod
  def getTailExtremityFirstFrame(args):
    from zebrazoom.getTailExtremityFirstFrame import getTailExtremityFirstFrame
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    getTailExtremityFirstFrame(args.pathToVideo, args.videoName, args.videoExt, args.configFile, args.hyperparameters)

  @staticmethod
  def recreateSuperStruct(args):
    from zebrazoom.recreateSuperStruct import recreateSuperStruct
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    recreateSuperStruct(args.pathToVideo, args.videoName, args.videoExt, args.configFile, args.hyperparameters)

  @staticmethod
  def convertSeqToAvi(args):
    from zebrazoom.videoFormatConversion.seq_to_avi import sqb_convert_to_avi
    sqb_convert_to_avi(args.path, args.videoName, args.codec, args.lastFrame)

  @staticmethod
  def convertSeqToAviThenLaunchTracking(args):
    from zebrazoom.videoFormatConversion.seq_to_avi import sqb_convert_to_avi
    from zebrazoom.mainZZ import ZebraZoomVideoAnalysis
    from pathlib import Path
    import time
    path2      = Path(args.path).parent
    print("Launching the convertion from seq to avi")
    sqb_convert_to_avi(args.path, args.videoName, args.codec, args.lastFrame)
    print("small break start")
    time.sleep(2)
    print("Launching the tracking, the data produced by ZebraZoom can be found in the folder: " + paths.getDefaultZZoutputFolder())
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    ZebraZoomVideoAnalysis(path2, args.videoName, 'avi', args.configFile, args.hyperparameters, useGUI=False).run()

  @staticmethod
  def DL_createMask(args):
    from zebrazoom.code.deepLearningFunctions.labellingFunctions import createMask
    pathToImgFolder = args.pathToImgFolder
    if not(os.path.exists(pathToImgFolder)):
      pathToImgFolder = os.path.join(paths.getDefaultZZoutputFolder(), args.pathToImgFolder, 'PNGImages')
    createMask(pathToImgFolder)

  @staticmethod
  def sleepVsMoving(args):
    from zebrazoom.code.dataPostProcessing.findSleepVsMoving import calculateSleepVsMovingPeriods
    calculateSleepVsMovingPeriods(paths.getDefaultZZoutputFolder(), args.videoName, args.speedThresholdForMoving, args.notMovingNumberOfFramesThresholdForSleep,
                                  args.maxDistBetweenTwoPointsInsideSleepingPeriod, args.specifiedStartTime, args.distanceTravelledRollingMedianFilter,
                                  args.videoPixelSize, args.videoFPS)

  @staticmethod
  def firstSleepingTimeAfterSpecifiedTime(args):
    from zebrazoom.code.dataPostProcessing.findSleepVsMoving import firstSleepingTimeAfterSpecifiedTime
    pathToZZoutput = paths.getDefaultZZoutputFolder()
    firstSleepingTimeAfterSpecifiedTime(args.pathToZZoutput, args.videoName, args.specifiedTime, args.wellNumber)

  @staticmethod
  def numberOfSleepingAndMovingTimesInTimeRange(args):
    from zebrazoom.code.dataPostProcessing.findSleepVsMoving import numberOfSleepingAndMovingTimesInTimeRange
    numberOfSleepingAndMovingTimesInTimeRange(paths.getDefaultZZoutputFolder(), args.videoName, args.specifiedStartTime, args.specifiedEndTime, args.wellNumber)

  @staticmethod
  def numberOfSleepBoutsInTimeRange(args):
    from zebrazoom.code.dataPostProcessing.findSleepVsMoving import numberOfSleepBoutsInTimeRange
    numberOfSleepBoutsInTimeRange(paths.getDefaultZZoutputFolder(), args.videoName, args.minSleepLenghtDurationThreshold, args.wellNumber,
                                  args.specifiedStartTime, args.specifiedEndTime)

  @staticmethod
  def calculateNumberOfSfsVsTurnsBasedOnMaxAmplitudeThreshod(args):
    from zebrazoom.dataAnalysis.postProcessingFromCommandLine.postProcessingFromCommandLine import calculateNumberOfSfsVsTurnsBasedOnMaxAmplitudeThreshold
    calculateNumberOfSfsVsTurnsBasedOnMaxAmplitudeThreshold(paths.getRootDataFolder(), args.experimentName, args.thresholdInDegrees)

  @staticmethod
  def kinematicParametersAnalysis(args):
    from zebrazoom.kinematicParametersAnalysis import kinematicParametersAnalysis
    kinematicParametersAnalysis(sys)

  @staticmethod
  def kinematicParametersAnalysisWithMedianPerGenotype(args):
    from zebrazoom.kinematicParametersAnalysis import kinematicParametersAnalysis
    kinematicParametersAnalysis(sys, 1)

  @staticmethod
  def clusteringAnalysis(args):
    from zebrazoom.clusteringAnalysis import clusteringAnalysis
    clusteringAnalysis(sys)

  @staticmethod
  def clusteringAnalysisPerFrame(args):
    from zebrazoom.clusteringAnalysisPerFrame import clusteringAnalysisPerFrame
    clusteringAnalysisPerFrame(sys)

  @staticmethod
  def kinematicParametersAnalysisCenterOfMassOnlyNoBoutsDetection(args):
    from zebrazoom.kinematicParametersAnalysisCenterOfMassOnlyNoBoutsDetection import kinematicParametersAnalysisCenterOfMassOnlyNoBoutsDetection
    kinematicParametersAnalysisCenterOfMassOnlyNoBoutsDetection(sys)

  @staticmethod
  def visualizeMovingAndSleepingTime(args):
    from zebrazoom.code.readValidationVideo import readValidationVideo
    import pandas as pd
    df = pd.read_excel(os.path.join(paths.getDefaultZZoutputFolder(), args.videoName, "sleepVsMoving_" + args.videoName + ".xlsx"))
    nbWells = int(len(df.columns)/3)

    if args.movingOrSleeping == "movingTime":
      framesToShow = df[["moving_" + str(i) for i in range(0, nbWells)]].to_numpy()
    else:
      assert arg.movingOrSleeping == "sleepingTime"
      framesToShow = df[["sleep_" + str(i) for i in range(0, nbWells)]].to_numpy()
    readValidationVideo("", args.videoName, "", -1, -1, 0, 1, framesToShow)

  @staticmethod
  def createDistanceBetweenFramesExcelFile(args):
    from zebrazoom.dataAnalysis.createCustomDataStructure.createDistanceBetweenFramesExcelFile import createDistanceBetweenFramesExcelFile
    from zebrazoom.GUIAllPy import PlainApplication
    app = PlainApplication(sys.argv)
    createDistanceBetweenFramesExcelFile(paths.getDefaultZZoutputFolder(), sys.argv) # fps, pixelSize

  @staticmethod
  def removeLargeInstantaneousDistanceData(args):
    from zebrazoom.dataAnalysis.createCustomDataStructure.removeLargeInstantaneousDistanceData import removeLargeInstantaneousDistanceData
    from zebrazoom.GUIAllPy import PlainApplication
    app = PlainApplication(sys.argv)
    removeLargeInstantaneousDistanceData(paths.getDefaultZZoutputFolder(), sys.argv)

  @staticmethod
  def filterLatencyAndMergeBoutsInSameTrials(args):
    from zebrazoom.dataAnalysis.createCustomDataStructure.filterLatencyAndMergeBoutsInSameTrials import filterLatencyAndMergeBoutsInSameTrials
    filterLatencyAndMergeBoutsInSameTrials(args.nameOfExperiment, args.minFrameNumberBoutStart, args.maxFrameNumberBoutStart, args.calculationMethod,
                                           paths.getDefaultZZoutputFolder(), args.dropDuplicates)

  @staticmethod
  def launchActiveLearning(args):
    from zebrazoom.otherScripts.launchActiveLearning import launchActiveLearning
    launchActiveLearning()

  @staticmethod
  def launchOptimalClusterNumberSearch(args):
    from zebrazoom.otherScripts.launchOptimalClusterNumberSearch import launchOptimalClusterNumberSearch
    launchOptimalClusterNumberSearch()

  @staticmethod
  def launchReapplyClustering(args):
    from zebrazoom.otherScripts.launchReapplyClustering import launchReapplyClustering
    launchReapplyClustering()

  @staticmethod
  def createSmallValidationVideosForFlagged(args):
    from zebrazoom.code.createValidationVideo import createSmallValidationVideosForFlagged
    createSmallValidationVideosForFlagged(args.videoName.rstrip(r'\/'), args.offset)

  @staticmethod
  def exit(args):
    from PyQt5.QtCore import QTimer
    from zebrazoom.GUIAllPy import ZebraZoomApp
    app = ZebraZoomApp(sys.argv)
    QTimer.singleShot(0, app.window.close)
    sys.exit(app.exec())

  @staticmethod
  def runVideoAnalysis(args):
    print("The data produced by ZebraZoom can be found in the folder: " + paths.getDefaultZZoutputFolder())
    from zebrazoom.mainZZ import ZebraZoomVideoAnalysis

    if args.useGUI:
      try:
        from zebrazoom.GUIAllPy import PlainApplication
        app = PlainApplication(sys.argv)
      except ImportError:
        args.useGUI = False
        print("GUI not available")
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    ZebraZoomVideoAnalysis(args.pathToVideo, args.videoName, args.videoExt, args.configFile, args.hyperparameters, useGUI=args.useGUI).run()


def _ensureFolderPermissions():
  requiredFolders = (paths.getDefaultZZoutputFolder(), paths.getConfigurationFolder(),
                     os.path.join(paths.getDataAnalysisFolder(), 'data'),
                     os.path.join(paths.getDataAnalysisFolder(), 'experimentOrganizationExcel'),
                     os.path.join(paths.getDataAnalysisFolder(), 'resultsClustering'),
                     os.path.join(paths.getDataAnalysisFolder(), 'resultsKinematic'))
  errors = []
  for folder in requiredFolders:
    try:
      os.makedirs(folder, exist_ok=True)
    except OSError:
      errors.append(folder)
  if not errors:
    return
  errorMessage = "Some of the folders required by ZebraZoom are missing and could not be created:\n" \
                 "%s\n\nZebraZoom cannot work without these folders, please make sure you have adequate " \
                 "write permissions or try an alternative installation method." % '\n'.join(errors)
  try:
    from PyQt5.QtWidgets import QMessageBox
    from zebrazoom.GUIAllPy import PlainApplication
    app = PlainApplication(sys.argv)
    QMessageBox.critical(None, "Required folders missing", errors)
  except ImportError:
    print(errors)
  sys.exit(1)


def _createLegacyVideoAnalysisParser():
  parser = argparse.ArgumentParser(prog=None if getattr(sys, 'frozen', False) else 'python -m zebrazoom',
                                   epilog='Text after help')
  parser.set_defaults(subcommand='runVideoAnalysis')
  parser.add_argument('--use-gui', action='store_true', dest='useGUI', help='Whether to use GUI.')
  parser.add_argument('pathToVideo', help='Help for pathToVideo')
  parser.add_argument('videoName', help='Help for videoName')
  parser.add_argument('videoExt', help='Help for videoExt')
  parser.add_argument('configFile', help='Help for configFile')
  parser.add_argument('hyperparameters', nargs='*', help='Help for hyperparameters')
  return parser


def _createParser():
  parser = argparse.ArgumentParser(prog=None if getattr(sys, 'frozen', False) else 'python -m zebrazoom',
                                   description='Text before help',
                                   epilog='Text after help')
  subparsers = parser.add_subparsers(dest='subcommand', help='Help message for subcommand')
  subparsers.default = 'launchZebraZoom'

  subparsers.add_parser('selectZZoutput', help='Help for selectZZoutput')

  for subcommand in ('getTailExtremityFirstFrame', 'recreateSuperStruct'):
    subparser = subparsers.add_parser('getTailExtremityFirstFrame', help='Help for getTailExtremityFirstFrame')
    subparser.add_argument('pathToVideo', help='Help for pathToVideo')
    subparser.add_argument('videoName', help='Help for videoName')
    subparser.add_argument('videoExt', help='Help for videoExt')
    subparser.add_argument('configFile', help='Help for configFile')
    subparser.add_argument('hyperparameters', nargs=argparse.REMAINDER, help='Help for hyperparameters')

  subparser = subparsers.add_parser('convertSeqToAvi', help='Help for convertSeqToAvi', description='Description for convertSeqToAvi')
  subparser.add_argument('path', help='Help for path')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('codec', help='Help for codec', nargs='?', default='HFYU')
  subparser.add_argument('lastFrame', help='Help for lastFrame', type=int, nargs='?', default=-1)

  subparser = subparsers.add_parser('convertSeqToAviThenLaunchTracking', help='Help for convertSeqToAviThenLaunchTracking')
  subparser.add_argument('path', help='Help for path')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('configFile', help='Help for configFile')
  subparser.add_argument('codec', help='Help for codec', nargs='?', default='HFYU')
  subparser.add_argument('lastFrame', help='Help for lastFrame', type=int, nargs='?', default=-1)
  subparser.add_argument('hyperparameters', nargs=argparse.REMAINDER, help='Help for hyperparameters')

  subparser = subparsers.add_parser('DL_createMask', help='Help for DL_createMask')
  subparser.add_argument('pathToImgFolder', help='Help for pathToImgFolder')

  subparser = subparsers.add_parser('dataPostProcessing', help='Help for dataPostProcessing')
  postProcessingSubparsers = subparser.add_subparsers(dest='subcommand', help='Help message for postProcessingSubcommand')

  subparser = postProcessingSubparsers.add_parser('sleepVsMoving', help='Help for sleepVsMoving')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('speedThresholdForMoving', help='Help for speedThresholdForMoving', type=float)
  subparser.add_argument('notMovingNumberOfFramesThresholdForSleep', help='Help for notMovingNumberOfFramesThresholdForSleep', type=int)
  subparser.add_argument('maxDistBetweenTwoPointsInsideSleepingPeriod', help='Help for maxDistBetweenTwoPointsInsideSleepingPeriod', type=float, nargs='?', default=-1)
  subparser.add_argument('specifiedStartTime', help='Help for specifiedStartTime', nargs='?', default=0)
  subparser.add_argument('distanceTravelledRollingMedianFilter', help='Help for distanceTravelledRollingMedianFilter', type=int, nargs='?', default=0)
  subparser.add_argument('videoPixelSize', help='Help for videoPixelSize', type=float, nargs='?', default=-1)
  subparser.add_argument('videoFPS', help='Help for videoFPS', type=float, nargs='?', default=-1)

  subparser = postProcessingSubparsers.add_parser('firstSleepingTimeAfterSpecifiedTime', help='Help for firstSleepingTimeAfterSpecifiedTime')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('specifiedTime', help='Help for specifiedTime')
  subparser.add_argument('wellNumber', help='Help for wellNumber')

  subparser = postProcessingSubparsers.add_parser('numberOfSleepingAndMovingTimesInTimeRange', help='Help for numberOfSleepingAndMovingTimesInTimeRange')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('specifiedStartTime', help='Help for specifiedStartTime')
  subparser.add_argument('specifiedEndTime', help='Help for specifiedEndTime')
  subparser.add_argument('wellNumber', help='Help for wellNumber')

  subparser = postProcessingSubparsers.add_parser('numberOfSleepBoutsInTimeRange', help='Help for numberOfSleepBoutsInTimeRange')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('minSleepLenghtDurationThreshold', help='Help for minSleepLenghtDurationThreshold', type=int)
  subparser.add_argument('wellNumber', help='Help for wellNumber', nargs='?', default='-1')
  subparser.add_argument('specifiedStartTime', help='Help for specifiedStartTime', nargs='?', default=-1)
  subparser.add_argument('specifiedEndTime', help='Help for specifiedEndTime', nargs='?', default=-1)

  subparser = postProcessingSubparsers.add_parser('calculateNumberOfSfsVsTurnsBasedOnMaxAmplitudeThreshod', help='Help for calculateNumberOfSfsVsTurnsBasedOnMaxAmplitudeThreshod')
  subparser.add_argument('experimentName', help='Help for experimentName')
  subparser.add_argument('thresholdInDegrees', help='Help for thresholdInDegrees', type=int)

  subparser = postProcessingSubparsers.add_parser('kinematicParametersAnalysis', help='Help for kinematicParametersAnalysis')

  subparser = postProcessingSubparsers.add_parser('kinematicParametersAnalysisWithMedianPerGenotype', help='Help for kinematicParametersAnalysisWithMedianPerGenotype')

  subparser = postProcessingSubparsers.add_parser('clusteringAnalysis', help='Help for clusteringAnalysis')

  subparser = postProcessingSubparsers.add_parser('clusteringAnalysisPerFrame', help='Help for clusteringAnalysisPerFrame')

  subparser = postProcessingSubparsers.add_parser('kinematicParametersAnalysisCenterOfMassOnlyNoBoutsDetection', help='Help for kinematicParametersAnalysisCenterOfMassOnlyNoBoutsDetection')

  subparser = subparsers.add_parser('visualizeMovingAndSleepingTime', help='Help for visualizeMovingAndSleepingTime')
  subparser.add_argument('movingOrSleeping', help='Help message for movingOrSleeping', choices=('movingTime', 'sleepingTime'))
  subparser.add_argument('videoName', help='Help for videoName')

  subparser = subparsers.add_parser('createDistanceBetweenFramesExcelFile', help='Help for createDistanceBetweenFramesExcelFile')

  subparser = subparsers.add_parser('removeLargeInstantaneousDistanceData', help='Help for removeLargeInstantaneousDistanceData')

  subparser = subparsers.add_parser('filterLatencyAndMergeBoutsInSameTrials', help='Help for filterLatencyAndMergeBoutsInSameTrials')
  subparser.add_argument('nameOfExperiment', help='Help message for nameOfExperiment')
  subparser.add_argument('minFrameNumberBoutStart', help='Help for minFrameNumberBoutStart', type=int)
  subparser.add_argument('maxFrameNumberBoutStart', help='Help for maxFrameNumberBoutStart', type=int)
  subparser.add_argument('calculationMethod', help='Help for calculationMethod', nargs='?', default='median', choices=('mean', 'median'))
  subparser.add_argument('dropDuplicates', help='Help for dropDuplicates', nargs='?', type=int, default=0, choices=(0, 1))

  subparser = subparsers.add_parser('otherScripts', help='Help for otherScripts')
  otherScriptsSubparsers = subparser.add_subparsers(dest='subcommand', help='Help message for otherScripts subcommand')

  subparser = otherScriptsSubparsers.add_parser('launchActiveLearning', help='Help for launchActiveLearning')

  subparser = otherScriptsSubparsers.add_parser('launchOptimalClusterNumberSearch', help='Help for launchOptimalClusterNumberSearch')

  subparser = otherScriptsSubparsers.add_parser('launchReapplyClustering', help='Help for launchReapplyClustering')

  subparser = subparsers.add_parser('createSmallValidationVideosForFlagged', help='Help for createSmallValidationVideosForFlagged')
  subparser.add_argument('videoName', help='Help for videoName')
  subparser.add_argument('offset', help='Help for offset', type=int)

  subparser = subparsers.add_parser('exit', help='Run ZebraZoom and immediately exit.')

  if len(sys.argv) > 1 and sys.argv[1] not in subparsers.choices and os.path.exists(sys.argv[1]):
    # XXX: add this format to help somewhere?
    # the first argument is a path, use the old generic format for running video analysis
    return _createLegacyVideoAnalysisParser()

  return parser


if __name__ == '__main__':
  _ensureFolderPermissions()
  args = _createParser().parse_args()
  getattr(_Subcommands, args.subcommand)(args)
