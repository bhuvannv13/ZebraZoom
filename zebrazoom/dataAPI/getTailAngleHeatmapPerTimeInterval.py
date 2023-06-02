import numpy as np

from ._calculateAndStoreTailAngleHeatmap import calculateAndStoreTailAngleHeatmap
from ._openResultsFile import openResultsFile


def getTailAngleHeatmapPerTimeInterval(videoName: str, numWell: int, numAnimal: int, startTimeInSeconds: float, endTimeInSeconds: float) -> tuple:
  if startTimeInSeconds >= endTimeInSeconds:
    raise ValueError('end time must be larger than start time')
  with openResultsFile(videoName, 'r+') as results:
    firstFrame = results.attrs['firstFrame']
    firstFrameInSeconds = firstFrame / results.attrs['videoFPS']
    lastFrameInSeconds = results.attrs['lastFrame'] / results.attrs['videoFPS']
    if startTimeInSeconds < firstFrameInSeconds or endTimeInSeconds > lastFrameInSeconds:
      raise ValueError(f'Tracking was performed from {firstFrameInSeconds}s to {lastFrameInSeconds}s, start and end times must be within this interval.')
    if 'videoFPS' not in results.attrs:
      raise ValueError(f'videoFPS not found in the results, cannot convert seconds to frames')
    boutsPath = f'dataForWell{numWell}/dataForAnimal{numAnimal}/listOfBouts'
    if boutsPath not in results:
      raise ValueError(f"bouts not found for animal {numAnimal} in well {numWell}")
    boutsGroup = results[boutsPath]
    intervalStart = int(startTimeInSeconds * results.attrs['videoFPS']) - firstFrame
    intervalEnd = int(endTimeInSeconds * results.attrs['videoFPS']) - firstFrame
    dataGroup = results[f'dataForWell{numWell}/dataForAnimal{numAnimal}/dataPerFrame']
    if 'tailAngleHeatmap' in dataGroup:
      tailAngleHeatmap = dataGroup['tailAngleHeatmap']
    else:
      tailAngleHeatmap = calculateAndStoreTailAngleHeatmap(results, dataGroup, boutsGroup)
    return [tailAngleHeatmap[col][intervalStart:intervalEnd] for col in tailAngleHeatmap.dtype.names], int(startTimeInSeconds * results.attrs['videoFPS']), dataGroup['TailLength'][0]
