from ._openResultsFile import openResultsFile


def getKinematicParametersPerBout(videoName: str, numWell: int, numAnimal: int, numBout: int) -> dict:
  with openResultsFile(videoName, 'r') as results:
    animalPath = f'dataForWell{numWell}/dataForAnimal{numAnimal}'
    if animalPath not in results:
      raise ValueError(f"data for animal {numAnimal} in well {numWell} doesn't exist")
    animalGroup = results[animalPath]
    if 'kinematicParametersPerBout' not in animalGroup:
      raise ValueError(f"kinematic parameters were not calculated during tracking")
    dataset = animalGroup['kinematicParametersPerBout']
    numberOfBouts, = dataset.shape
    if numBout >= numberOfBouts:
      raise ValueError(f"cannot get data for bout {numBout}, total number of detected bouts is {numberOfBouts}")
    return {col: dataset[col][numBout] for col in dataset.attrs['columns']}
