import tkinter as tk
from tkinter import font  as tkfont
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import re
import os
import json
import subprocess
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import scipy.io as sio
from pathlib import Path
from zebrazoom.code.readValidationVideo import readValidationVideo
from zebrazoom.code.vars import getGlobalVariables
globalVariables = getGlobalVariables()

from zebrazoom.mainZZ import mainZZ
from zebrazoom.getTailExtremityFirstFrame import getTailExtremityFirstFrame
import zebrazoom.code.popUpAlgoFollow as popUpAlgoFollow

LARGE_FONT= ("Verdana", 12)

def chooseVideoToAnalyze(self, justExtractParams, noValidationVideo):
    
    if globalVariables["mac"]:
        tk.videoName =  filedialog.askopenfilename(initialdir = os.path.expanduser("~"),title = "Select file")
    else:
        tk.videoName =  filedialog.askopenfilename(initialdir = os.path.expanduser("~"),title = "Select file",filetypes = (("video","*.*"),("all files","*.*")))
    tk.folderName = ''
    tk.headEmbedded = 0
    
    tk.justExtractParams = int(justExtractParams)
    tk.noValidationVideo = int(noValidationVideo)
    
    self.show_frame("ConfigFilePromp")

def chooseFolderToAnalyze(self, justExtractParams, noValidationVideo):
    tk.folderName =  filedialog.askdirectory(initialdir = os.path.expanduser("~"),title = "Select folder")
    tk.headEmbedded = 0
    tk.justExtractParams = int(justExtractParams)
    tk.noValidationVideo = int(noValidationVideo)
    self.show_frame("ConfigFilePromp")
    
def chooseFolderForTailExtremityHE(self):
    tk.folderName =  filedialog.askdirectory(initialdir = os.path.expanduser("~"),title = "Select folder")
    tk.headEmbedded = 1
    self.show_frame("ConfigFilePromp")

def chooseConfigFile(self):
    
    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    path = Path(cur_dir_path)
    path = path.parent.parent
    path = os.path.join(path, 'configuration')
    
    if globalVariables["mac"]:
        tk.configFile =  filedialog.askopenfilename(initialdir = path, title = "Select file")
    else:
        tk.configFile =  filedialog.askopenfilename(initialdir = path, title = "Select file", filetypes = (("json files","*.json"),("all files","*.*")))
    if globalVariables["mac"] or globalVariables["lin"]:
        self.show_frame("Patience")
    else:
        self.launchZebraZoom()

def launchZebraZoom(self):
  
  last = 0
  allVideos = []
  
  if len(tk.folderName):
    for name in os.listdir(tk.folderName):
      if len(name) > 3:
        allDotsPositions = [m.start() for m in re.finditer('\.', name)]
        pointPos = allDotsPositions[len(allDotsPositions)-1]
        ext = name[pointPos:]
        if (ext in ['.264', '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.3mm', '.3p2', '.60d', '.787', '.89', '.aaf', '.aec', '.aep', '.aepx', '.aet', '.aetx', '.ajp', '.ale', '.am', '.amc', '.amv', '.amx', '.anim', '.aqt', '.arcut', '.arf', '.asf', '.asx', '.avb', '.avc', '.avd', '.avi', '.avp', '.avs', '.avs', '.avv', '.axm', '.bdm', '.bdmv', '.bdt2', '.bdt3', '.bik', '.bin', '.bix', '.bmk', '.bnp', '.box', '.bs4', '.bsf', '.bvr', '.byu', '.camproj', '.camrec', '.camv', '.ced', '.cel', '.cine', '.cip', '.clpi', '.cmmp', '.cmmtpl', '.cmproj', '.cmrec', '.cpi', '.cst', '.cvc', '.cx3', '.d2v', '.d3v', '.dat', '.dav', '.dce', '.dck', '.dcr', '.dcr', '.ddat', '.dif', '.dir', '.divx', '.dlx', '.dmb', '.dmsd', '.dmsd3d', '.dmsm', '.dmsm3d', '.dmss', '.dmx', '.dnc', '.dpa', '.dpg', '.dream', '.dsy', '.dv', '.dv-avi', '.dv4', '.dvdmedia', '.dvr', '.dvr-ms', '.dvx', '.dxr', '.dzm', '.dzp', '.dzt', '.edl', '.evo', '.eye', '.ezt', '.f4p', '.f4v', '.fbr', '.fbr', '.fbz', '.fcp', '.fcproject', '.ffd', '.flc', '.flh', '.fli', '.flv', '.flx', '.gfp', '.gl', '.gom', '.grasp', '.gts', '.gvi', '.gvp', '.h264', '.hdmov', '.hkm', '.ifo', '.imovieproj', '.imovieproject', '.ircp', '.irf', '.ism', '.ismc', '.ismv', '.iva', '.ivf', '.ivr', '.ivs', '.izz', '.izzy', '.jss', '.jts', '.jtv', '.k3g', '.kmv', '.ktn', '.lrec', '.lsf', '.lsx', '.m15', '.m1pg', '.m1v', '.m21', '.m21', '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v', '.m75', '.mani', '.meta', '.mgv', '.mj2', '.mjp', '.mjpg', '.mk3d', '.mkv', '.mmv', '.mnv', '.mob', '.mod', '.modd', '.moff', '.moi', '.moov', '.mov', '.movie', '.mp21', '.mp21', '.mp2v', '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg4', '.mpf', '.mpg', '.mpg2', '.mpgindex', '.mpl', '.mpl', '.mpls', '.mpsub', '.mpv', '.mpv2', '.mqv', '.msdvd', '.mse', '.msh', '.mswmm', '.mts', '.mtv', '.mvb', '.mvc', '.mvd', '.mve', '.mvex', '.mvp', '.mvp', '.mvy', '.mxf', '.mxv', '.mys', '.ncor', '.nsv', '.nut', '.nuv', '.nvc', '.ogm', '.ogv', '.ogx', '.osp', '.otrkey', '.pac', '.par', '.pds', '.pgi', '.photoshow', '.piv', '.pjs', '.playlist', '.plproj', '.pmf', '.pmv', '.pns', '.ppj', '.prel', '.pro', '.prproj', '.prtl', '.psb', '.psh', '.pssd', '.pva', '.pvr', '.pxv', '.qt', '.qtch', '.qtindex', '.qtl', '.qtm', '.qtz', '.r3d', '.rcd', '.rcproject', '.rdb', '.rec', '.rm', '.rmd', '.rmd', '.rmp', '.rms', '.rmv', '.rmvb', '.roq', '.rp', '.rsx', '.rts', '.rts', '.rum', '.rv', '.rvid', '.rvl', '.sbk', '.sbt', '.scc', '.scm', '.scm', '.scn', '.screenflow', '.sec', '.sedprj', '.seq', '.sfd', '.sfvidcap', '.siv', '.smi', '.smi', '.smil', '.smk', '.sml', '.smv', '.spl', '.sqz', '.srt', '.ssf', '.ssm', '.stl', '.str', '.stx', '.svi', '.swf', '.swi', '.swt', '.tda3mt', '.tdx', '.thp', '.tivo', '.tix', '.tod', '.tp', '.tp0', '.tpd', '.tpr', '.trp', '.ts', '.tsp', '.ttxt', '.tvs', '.usf', '.usm', '.vc1', '.vcpf', '.vcr', '.vcv', '.vdo', '.vdr', '.vdx', '.veg','.vem', '.vep', '.vf', '.vft', '.vfw', '.vfz', '.vgz', '.vid', '.video', '.viewlet', '.viv', '.vivo', '.vlab', '.vob', '.vp3', '.vp6', '.vp7', '.vpj', '.vro', '.vs4', '.vse', '.vsp', '.w32', '.wcp', '.webm', '.wlmp', '.wm', '.wmd', '.wmmp', '.wmv', '.wmx', '.wot', '.wp3', '.wpl', '.wtv', '.wve', '.wvx', '.xej', '.xel', '.xesc', '.xfl', '.xlmv', '.xmv', '.xvid', '.y4m', '.yog', '.yuv', '.zeg', '.zm1', '.zm2', '.zm3', '.zmv']):
          allVideos.append(tk.folderName+'/'+name)
  else:
    allVideos = [tk.videoName]
  
  for idx, text in enumerate(allVideos):
    for m in re.finditer('/', text):
      last = m.start()
    path        = text[:last+1]
    nameWithExt = text[last+1:]
    allDotsPositions = [m.start() for m in re.finditer('\.', nameWithExt)]
    pointPos = allDotsPositions[len(allDotsPositions)-1]
    name     = nameWithExt[:pointPos]
    videoExt = nameWithExt[pointPos+1:]
    
    if tk.headEmbedded == 0:
      tabParams = ["mainZZ", path, name, videoExt, tk.configFile, "freqAlgoPosFollow", 100, "popUpAlgoFollow", 1]
      if tk.justExtractParams == 1:
        tabParams = tabParams + ["reloadWellPositions", 1, "reloadBackground", 1, "debugPauseBetweenTrackAndParamExtract", "justExtractParamFromPreviousTrackData"]
      if tk.noValidationVideo == 1:
          tabParams = tabParams + ["createValidationVideo", 0]
      mainZZ(path, name, videoExt, tk.configFile, tabParams)
    else:
      getTailExtremityFirstFrame(path, name, videoExt, tk.configFile, [])
  
  self.show_frame("ZZoutro")


def showValidationVideo(self, numWell, zoom, deb):

    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    path = Path(cur_dir_path)
    path = path.parent.parent
    filepath = os.path.join(path, os.path.join('ZZoutput', os.path.join(self.currentResultFolder, 'pathToVideo.txt')))
    
    if os.path.exists(filepath):
        with open(filepath) as fp:
           videoPath = fp.readline()
        videoPath = videoPath[:len(videoPath)-1]
    else:
        videoPath = ""
    
    readValidationVideo(videoPath, self.currentResultFolder, '.txt', int(numWell), int(zoom), int(deb))
    

def exploreResultFolder(self, currentResultFolder):
    
    self.currentResultFolder = currentResultFolder
    self.superstructmodified = 0
    self.justEnteredViewParameter = 1
    self.printSomeResults(0, 0, 0)


def printNextResults(self, numWell, numPoiss, numMouv, nbWells, nbPoiss, nbMouv):

    numWell  = int(numWell)
    numPoiss = int(numPoiss)
    numMouv  = int(numMouv)
    nbWells  = int(nbWells)
    nbPoiss  = int(nbPoiss)
    nbMouv   = int(nbMouv)
    
    if numMouv + 1 >= nbMouv:
        if numPoiss + 1 >= nbPoiss:
            if numWell + 1 < nbWells:
              numWell  = numWell + 1
              numPoiss = 0
              numMouv  = 0
        else:
            numPoiss = numPoiss + 1
            numMouv  = 0
    else:
        numMouv = numMouv + 1

    self.printSomeResults(numWell, numPoiss, numMouv)


def printPreviousResults(self, numWell, numPoiss, numMouv, nbWells, nbPoiss, nbMouv):

    numWell  = int(numWell)
    numPoiss = int(numPoiss)
    numMouv  = int(numMouv)
    nbWells  = int(nbWells)
    nbPoiss  = int(nbPoiss)
    nbMouv   = int(nbMouv)
    
    if numMouv - 1 < 0:
        if numPoiss - 1 < 0:
            if numWell - 1 >= 0:
                numWell = numWell - 1
                numPoiss = 100000
                numMouv = 10000000
        else:
            numPoiss = numPoiss - 1
            numMouv  = 0
    else:
        numMouv = numMouv - 1

    self.printSomeResults(numWell, numPoiss, numMouv)


def flagMove(self, numWell, numPoiss, numMouv):

    self.superstructmodified = 1

    name = self.currentResultFolder

    dataRef = self.dataRef
    
    if "flag" in dataRef["wellPoissMouv"][int(numWell)][int(numPoiss)][int(numMouv)]:
      dataRef["wellPoissMouv"][int(numWell)][int(numPoiss)][int(numMouv)]["flag"] = int(not(dataRef["wellPoissMouv"][int(numWell)][int(numPoiss)][int(numMouv)]["flag"]));
    else:
      dataRef["wellPoissMouv"][int(numWell)][int(numPoiss)][int(numMouv)]["flag"] = 1;
    
    self.dataRef = dataRef
    
    self.printSomeResults(numWell, numPoiss, numMouv)


def saveSuperStruct(self, numWell, numPoiss, numMouv):
    
    self.superstructmodified = 0
    
    name = self.currentResultFolder
    dataRef = self.dataRef
    
    cur_dir_path = os.path.dirname(os.path.realpath(__file__))
    path = Path(cur_dir_path)
    path = path.parent.parent
    reference = os.path.join(path, os.path.join('ZZoutput', os.path.join(name, 'results_' + name + '.txt')))
    print("reference:", reference)
    
    with open(reference,'w') as out:
       json.dump(dataRef, out)
    
    self.dataRef = dataRef
    
    self.printSomeResults(numWell, numPoiss, numMouv)


def openConfigurationFileFolder(self, homeDirectory):
  dir_path = os.path.join(homeDirectory,'configuration')
  if sys.platform == "win32":
    os.startfile(dir_path)
  else:
    opener ="open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, dir_path])


def openZZOutputFolder(self, homeDirectory):
  dir_path = os.path.join(homeDirectory,'ZZoutput')
  if sys.platform == "win32":
    os.startfile(dir_path)
  else:
    opener ="open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, dir_path])  
