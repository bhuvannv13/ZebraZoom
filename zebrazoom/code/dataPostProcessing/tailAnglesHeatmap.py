import h5py
import cv2
import os
import shutil
import math
import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
import pickle
import scipy as sp

def tailAnglesHeatMap(superStruct, hyperparameters, videoName):
  
  # Creation of the sub-folder "anglesHeatMap" 
  outputPath = os.path.join(os.path.join(hyperparameters["outputFolder"], videoName), "anglesHeatMap")
  if os.path.exists(outputPath):
    shutil.rmtree(outputPath)
  while True:
    try:
      os.mkdir(outputPath)
      break
    except OSError as e:
      print("waiting inside except")
      time.sleep(0.1)
    else:
      print("waiting")
      time.sleep(0.1)
  
  # Video frame start and end
  firstFrame = hyperparameters["firstFrame"]
  lastFrame  = hyperparameters["lastFrame"]
  nbFrames   = lastFrame - firstFrame + 1
  perBoutOutputVideoStartStopFrameMargin = hyperparameters["perBoutOutputVideoStartStopFrameMargin"]
  
  plotTailAngleRaw      = False
  plotTailAngleSmoothed = False
  plotTailAngleHeatmap  = True
  
  pointsToTakeIntoAccountStart = 9 - int(hyperparameters["tailAnglesHeatMapNbPointsToTakeIntoAccount"])
  
  # Going through each well, each fish and each bout
  for i in range(0, len(superStruct["wellPoissMouv"])):
    for j in range(0, len(superStruct["wellPoissMouv"][i])):
      if hyperparameters["saveAllDataEvenIfNotInBouts"]:
        tailAngleHeatmaps = {}
        fname = os.path.join(hyperparameters["outputFolder"], hyperparameters["videoName"], f'allData_{hyperparameters["videoName"]}_wellNumber{i}_animal{j}.csv')
        startLines = []
        with open(fname) as f:
          line = f.readline()
          while ',' not in line:
            startLines.append(line)
            line = f.readline()
        df = pd.read_csv(fname, skiprows=len(startLines))
      for k in range(0, len(superStruct["wellPoissMouv"][i][j])):
        
        # Creation of tail angles raw graph for bout k
        if plotTailAngleRaw:
          bStart = superStruct["wellPoissMouv"][i][j][k]["BoutStart"]
          bEnd   = superStruct["wellPoissMouv"][i][j][k]["BoutEnd"]
          tailAngles = superStruct["wellPoissMouv"][i][j][k]["allTailAngles"][pointsToTakeIntoAccountStart:]
          plt.figure(1)
          for tailAngle in tailAngles:
            if bEnd - bStart + 1 == len(tailAngle):
              plt.plot([i for i in range(bStart, bEnd + 1)], [t*(180/math.pi) for t in tailAngle])
              if hyperparameters["perBoutOutputYaxis"]:
                plt.axis([bStart, bEnd + 1, hyperparameters["perBoutOutputYaxis"][0], hyperparameters["perBoutOutputYaxis"][1]])
          plt.savefig(os.path.join(outputPath, hyperparameters["videoName"] + "_angles_bout" + str(i) + '_' + str(j) + '_' + str(k) + '.png'))
          plt.close(1)
        
        # Creation of tail angles smoothed graph and tail angle heatmap for bout k
        bStart = superStruct["wellPoissMouv"][i][j][k]["BoutStart"]
        bEnd   = superStruct["wellPoissMouv"][i][j][k]["BoutEnd"]
        tailAngles = superStruct["wellPoissMouv"][i][j][k]["allTailAnglesSmoothed"][pointsToTakeIntoAccountStart:]
        tailAngleHeatmap = []
        if plotTailAngleSmoothed:
          plt.figure(1)
        for tailAngle in tailAngles:
          if bEnd - bStart + 1 == len(tailAngle):
            tailAngleHeatmap.append([t*(180/math.pi) for t in tailAngle])
            if plotTailAngleSmoothed:
              plt.plot([i for i in range(bStart, bEnd + 1)], [t*(180/math.pi) for t in tailAngle])
              if hyperparameters["perBoutOutputYaxis"]:
                plt.axis([bStart, bEnd + 1, hyperparameters["perBoutOutputYaxis"][0], hyperparameters["perBoutOutputYaxis"][1]])
        if plotTailAngleSmoothed:
          plt.savefig(os.path.join(outputPath, hyperparameters["videoName"] + "_anglesSmoothed_bout" + str(i) + '_' + str(j) + '_' + str(k) + '.png'))
          plt.close(1)

        if hyperparameters["saveAllDataEvenIfNotInBouts"]:
          tailAngleHeatmaps[(bStart - firstFrame, bEnd + 1 - firstFrame)] = tailAngleHeatmap
        
        # Creation of tail angle heatmap
        if plotTailAngleHeatmap:
          fig = plt.figure(1)
          maxAngle = np.max(np.abs(tailAngleHeatmap))
          # plt.pcolor(tailAngleHeatmap)
          plt.pcolor(tailAngleHeatmap[::-1], vmin=-maxAngle, vmax=maxAngle)
          ax = fig.axes
          ax[0].set_xlabel('Frame number')
          ax[0].set_ylabel('Tail angle: Tail base to tail extremity')
          plt.colorbar()
          plt.savefig(os.path.join(outputPath, hyperparameters["videoName"] + "_tailAngleHeatmap_bout" + str(i) + '_' + str(j) + '_' + str(k) + '.png'))
          plt.close(1)

      if hyperparameters["saveAllDataEvenIfNotInBouts"]:
        angleCount = max(map(len, tailAngleHeatmaps.values())) if tailAngleHeatmaps else 0
        tailAngleHeatmapData = [[float('nan')] * nbFrames for _ in range(angleCount)]
        for (start, end), values in tailAngleHeatmaps.items():
          for data, vals in zip(tailAngleHeatmapData, values):
            data[start:end] = vals
        for idx, data in enumerate(tailAngleHeatmapData):
          df[f'tailAngleHeatmap{idx + 1}'] = data
        with open(fname, 'w+', newline='') as f:
          f.write(''.join(startLines))
          df.convert_dtypes().to_csv(f)
        if angleCount and hyperparameters['storeH5']:
          with h5py.File(hyperparameters['H5filename'], 'a') as results:
            arr = np.empty(nbFrames, dtype=[(f'Pos{idx}', float) for idx in range(1, angleCount + 1)])
            for idx, data in enumerate(tailAngleHeatmapData):
              arr[f'Pos{idx + 1}'] = data
            dataset = results.create_dataset(f"dataForWell{i}/dataForAnimal{j}/dataPerFrame/tailAngleHeatmap", data=arr)
            dataset.attrs['columns'] = arr.dtype.names
