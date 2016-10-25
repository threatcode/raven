"""
  This module contains the Sobol indexes sampling strategy

  Created on May 21, 2016
  @author: alfoa
  supercedes Samplers.py from talbpw
"""
#for future compatibility with Python 3--------------------------------------------------------------
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
#if not 'xrange' in dir(__builtins__): xrange = range
#End compatibility block for Python 3----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
import sys
import os
import copy
import abc
import numpy as np
import json
from operator import mul,itemgetter
from collections import OrderedDict
from functools import reduce
from scipy import spatial
from scipy.interpolate import InterpolatedUnivariateSpline
import xml.etree.ElementTree as ET
import itertools
from math import ceil
from collections import OrderedDict
from sklearn import neighbors
from sklearn.utils.extmath import cartesian

if sys.version_info.major > 2: import pickle
else: import cPickle as pickle
#External Modules End--------------------------------------------------------------------------------

#Internal Modules------------------------------------------------------------------------------------
from .SparseGridCollocation import SparseGridCollocation
from .Grid import Grid
import utils
import mathUtils
from BaseClasses import BaseType
from Assembler import Assembler
import Distributions
import DataObjects
import SupervisedLearning
import pyDOE as doe
import Quadratures
import OrthoPolynomials
import IndexSets
import Models
import PostProcessors
import MessageHandler
import GridEntities
from AMSC_Object import AMSC_Object
distribution1D = utils.find_distribution1D()
#Internal Modules End--------------------------------------------------------------------------------

class Sobol(SparseGridCollocation):
  """
    Sobol indexes sampling strategy
  """
  def __init__(self):
    """
      Default Constructor that will initialize member variables with reasonable
      defaults or empty lists/dictionaries where applicable.
      @ In, None
      @ Out, None
    """
    Grid.__init__(self)
    self.type           = 'SobolSampler'
    self.printTag       = 'SAMPLER SOBOL'
    self.assemblerObjects={}    #dict of external objects required for assembly
    self.maxPolyOrder   = None  #L, the relative maximum polynomial order to use in any dimension
    self.sobolOrder     = None  #S, the order of the HDMR expansion (1,2,3), queried from the sobol ROM
    self.indexSetType   = None  #the type of index set to use, queried from the sobol ROM
    self.polyDict       = {}    #varName-indexed dict of polynomial types
    self.quadDict       = {}    #varName-indexed dict of quadrature types
    self.importanceDict = {}    #varName-indexed dict of importance weights
    self.references     = {}    #reference (mean) values for distributions, by var
    self.solns          = None  #pointer to output dataObjects object
    self.ROM            = None  #pointer to sobol ROM
    self.jobHandler     = None  #pointer to job handler for parallel runs
    self.doInParallel   = True  #compute sparse grid in parallel flag, recommended True
    self.distinctPoints = set() #tracks distinct points used in creating this ROM
    self.sparseGridType = 'smolyak'
    self.addAssemblerObject('ROM','1',True)

  def _localWhatDoINeed(self):
    """
      Used to obtain necessary objects.
      @ In, None
      @ Out, gridDict, dict, the dict listing the needed objects
    """
    gridDict = Grid._localWhatDoINeed(self)
    gridDict['internal'] = [(None,'jobHandler')]
    return gridDict

  def _localGenerateAssembler(self,initDict):
    """
      Used to obtain necessary objects.
      @ In, initDict, dict, dictionary of objects required to initialize
      @ Out, None
    """
    Grid._localGenerateAssembler(self, initDict)
    self.jobHandler = initDict['internal']['jobHandler']
    self.dists = self.transformDistDict()
    for dist in self.dists.values():
      if isinstance(dist,Distributions.NDimensionalDistributions): self.raiseAnError(IOError,'ND Distributions containing the variables in the original input space are  not supported for this sampler!')

  def localInitialize(self):
    """
      Will perform all initialization specific to this Sampler.
      @ In, None
      @ Out, None
    """
    SVL = self.readFromROM()
    #make combination of ROMs that we need
    self.targets  = self.ROM.SupervisedEngine.keys()
    SVLs = self.ROM.SupervisedEngine.values()
    self.sobolOrder = SVL.sobolOrder
    self._generateQuadsAndPolys(SVL)
    self.features = SVL.features
    needCombos = itertools.chain.from_iterable(itertools.combinations(self.features,r) for r in range(self.sobolOrder+1))
    self.SQs={}
    self.ROMs={} #keys are [target][combo]
    for t in self.targets: self.ROMs[t]={}
    for combo in needCombos:
      if len(combo)==0:
        continue
      distDict={}
      quadDict={}
      polyDict={}
      imptDict={}
      limit=0
      for c in combo:
        distDict[c]=self.dists[c]
        quadDict[c]=self.quadDict[c]
        polyDict[c]=self.polyDict[c]
        imptDict[c]=self.importanceDict[c]
      iset=IndexSets.returnInstance(SVL.indexSetType,self)
      iset.initialize(combo,imptDict,SVL.maxPolyOrder)
      self.SQs[combo] = Quadratures.returnInstance(self.sparseGridType,self)
      self.SQs[combo].initialize(combo,iset,distDict,quadDict,self.jobHandler,self.messageHandler)
      # initDict is for SVL.__init__()
      initDict={'IndexSet'       :iset.type,        # type of index set
                'PolynomialOrder':SVL.maxPolyOrder, # largest polynomial
                'Interpolation'  :SVL.itpDict,      # polys, quads per input
                'Features'       :','.join(combo),  # input variables
                'Target'         :None}             # set below, per-case basis
      #initializeDict is for SVL.initialize()
      initializeDict={'SG'   :self.SQs[combo],      # sparse grid
                      'dists':distDict,             # distributions
                      'quads':quadDict,             # quadratures
                      'polys':polyDict,             # polynomials
                      'iSet' :iset}                 # index set
      for name,SVL in self.ROM.SupervisedEngine.items():
        initDict['Target']     = SVL.target
        self.ROMs[name][combo] = SupervisedLearning.returnInstance('GaussPolynomialRom',self,**initDict)
        self.ROMs[name][combo].initialize(initializeDict)
        self.ROMs[name][combo].messageHandler = self.messageHandler
    #make combined sparse grids
    self.references={}
    for var in self.features:
      self.references[var]=self.dists[var].untruncatedMean()
    self.pointsToRun=[]
    #make sure reference case gets in there
    newpt = np.zeros(len(self.features))
    for v,var in enumerate(self.features):
      newpt[v] = self.references[var]
    self.pointsToRun.append(tuple(newpt))
    self.distinctPoints.add(tuple(newpt))
    #now do the rest
    for combo,rom in utils.first(self.ROMs.values()).items(): #each target is the same, so just for each combo
      SG = rom.sparseGrid #they all should have the same sparseGrid
      SG._remap(combo)
      for l in range(len(SG)):
        pt,wt = SG[l]
        newpt = np.zeros(len(self.features))
        for v,var in enumerate(self.features):
          if var in combo: newpt[v] = pt[combo.index(var)]
          else: newpt[v] = self.references[var]
        newpt=tuple(newpt)
        self.distinctPoints.add(newpt)
        if newpt not in self.pointsToRun:
          self.pointsToRun.append(newpt)
    self.limit = len(self.pointsToRun)
    self.raiseADebug('Needed points: %i' %self.limit)
    initdict={'ROMs':None,
              'SG':self.SQs,
              'dists':self.dists,
              'quads':self.quadDict,
              'polys':self.polyDict,
              'refs':self.references,
              'numRuns':len(self.distinctPoints)}
    for target in self.targets:
      initdict['ROMs'] = self.ROMs[target]
      self.ROM.SupervisedEngine[target].initialize(initdict)

  def localGenerateInput(self,model,myInput):
    """
      Function to select the next most informative point
      @ In, model, model instance, an instance of a model
      @ In, myInput, list, a list of the original needed inputs for the model (e.g. list of files, etc.)
      @ Out, None
    """
    try: pt = self.pointsToRun[self.counter-1]
    except IndexError:
      self.raiseADebug('All sparse grids are complete!  Moving on...')
      raise utils.NoMoreSamplesNeeded
    for v,varName in enumerate(self.features):
      # compute the SampledVarsPb for 1-D distribution
      if self.variables2distributionsMapping[varName]['totDim'] == 1:
        for key in varName.strip().split(','):
          self.values[key] = pt[v]
        self.inputInfo['SampledVarsPb'][varName] = self.distDict[varName].pdf(pt[v])
        self.inputInfo['ProbabilityWeight-'+varName.replace(",","-")] = self.inputInfo['SampledVarsPb'][varName]
      # compute the SampledVarsPb for N-D distribution
      elif self.variables2distributionsMapping[varName]['totDim'] > 1 and self.variables2distributionsMapping[varName]['reducedDim'] == 1:
        dist = self.variables2distributionsMapping[varName]['name']
        ndCoordinates = np.zeros(len(self.distributions2variablesMapping[dist]))
        positionList = self.distributions2variablesIndexList[dist]
        for varDict in self.distributions2variablesMapping[dist]:
          var = utils.first(varDict.keys())
          position = utils.first(varDict.values())
          location = -1
          for key in var.strip().split(','):
            if key in self.features:
              location = self.features.index(key)
              break
          if location > -1:
            ndCoordinates[positionList.index(position)] = pt[location]
          else:
            self.raiseAnError(IOError,'The variables ' + var + ' listed in sobol sampler, but not used in the ROM!' )
          for key in var.strip().split(','):
            self.values[key] = pt[location]
        self.inputInfo['SampledVarsPb'][varName] = self.distDict[varName].pdf(ndCoordinates)
        self.inputInfo['ProbabilityWeight-'+varName.replace(",","!")] = self.inputInfo['SampledVarsPb'][varName]

    self.inputInfo['PointProbability'] = reduce(mul,self.inputInfo['SampledVarsPb'].values())
    self.inputInfo['SamplerType'] = 'Sparse Grids for Sobol'
