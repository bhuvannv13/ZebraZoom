import os

import h5py
import numpy as np

from zebrazoom.code.paths import getDefaultZZoutputFolder
from ._calculateAndStoreCurvature import calculateAndStoreCurvature


def getCurvaturePerBout(videoName: str, numWell: int, numAnimal: int, numBout: int) -> [np.array, np.array, np.array]:
  
  ZZoutputPath = getDefaultZZoutputFolder()
  resultsPath = os.path.join(ZZoutputPath, f'{videoName}.h5')
  
  if not os.path.exists(resultsPath):
    raise ValueError(f'video {videoName} not found in the default ZZoutput folder ({ZZoutputPath})')
  
  with h5py.File(resultsPath, 'r+') as results:
    if not('videoFPS' in results.attrs) or not('videoPixelSize' in results.attrs):
      raise ValueError(f'You must set the videoFPS and videoPixelSize for the video {videoName}')
    videoFPS       = results.attrs['videoFPS']
    videoPixelSize = results.attrs['videoPixelSize']
    
    boutPath     = f'dataForWell{numWell}/dataForAnimal{numAnimal}/listOfBouts/bout{numBout}'
    perFramePath = f'dataForWell{numWell}/dataForAnimal{numAnimal}/dataPerFrame'
    if boutPath not in results:
      raise ValueError(f"bout {numBout} for animal {numAnimal} in well {numWell} doesn't exist")
    boutGroup = results[boutPath]
    firstFrame = results.attrs['firstFrame']
    start = boutGroup.attrs['BoutStart'] - firstFrame
    end = boutGroup.attrs['BoutEnd'] - firstFrame + 1
    dataGroup = results[perFramePath]
    
    if 'curvature' in dataGroup:
      curvature = np.array([dataGroup['curvature'][column][start:end] for column in dataGroup['curvature'].attrs['columns']])
    else:
      curvature = np.array([data[start:end] for data in calculateAndStoreCurvature(results, dataGroup)])

    # Getting x time values for each curvature point
    xTimeValues = curvature.copy()
    for i in range(0, len(xTimeValues[0])):
      xTimeValues[:, i] = int(100*((i + boutGroup.attrs['BoutStart'])/videoFPS))/100
    
    # Getting y distance along the tail values for each curvature point
    tailX = np.transpose(np.concatenate((np.array([results[perFramePath+"/HeadPos"]['X'][start:end]]).reshape((-1, 1)), results[perFramePath+"/TailPosX"][start:end].view((float, len(results[perFramePath+"/TailPosX"][start:end].dtype.names)))), axis=1))
    tailY = np.transpose(np.concatenate((np.array([results[perFramePath+"/HeadPos"]['Y'][start:end]]).reshape((-1, 1)), results[perFramePath+"/TailPosY"][start:end].view((float, len(results[perFramePath+"/TailPosX"][start:end].dtype.names)))), axis=1))
    nbLinesTail = len(tailX)
    yDistanceAlongTheTail = curvature.copy()
    yDistanceAlongTheTail[:, :] = np.sqrt(np.square(tailX[2:nbLinesTail, :] - tailX[1:nbLinesTail-1, :]) + np.square(tailY[2:nbLinesTail, :] - tailY[1:nbLinesTail-1, :])) * videoPixelSize
    for i in range(len(yDistanceAlongTheTail)-2, -1, -1):
      yDistanceAlongTheTail[i, :] += yDistanceAlongTheTail[i+1, :]

    return [curvature, xTimeValues, yDistanceAlongTheTail]
