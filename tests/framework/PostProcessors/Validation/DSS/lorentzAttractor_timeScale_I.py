# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from wikipedia: dx/dt = sigma*(y-x)  ; dy/dt = x*(rho-z)-y  dz/dt = x*y-beta*z

import numpy as np

def initialize(self,runInfoDict,inputFiles):
  """
    Constructor
    @ In, runInfoDict, dict, dictionary of input file names, file location, and other parameters
          RAVEN run.
    @ In, inputFiles, list, data objects required for external model initialization.
    @ Out, None
  """
  self.sigma = 10.0
  self.rho   = 28.0
  self.beta  = 8.0/3.0
  return

def run(self,Input):
  """
    Constructor
    @ In, Input, dict, dictionary of input values for each feature.
    @ Out, None
  """
  disc = 2.0
  maxTime = 0.5
  tStep = 0.005
  self.sigma = 10.0
  self.rho   = 28.0
  self.beta  = 8.0/3.0

  numberTimeSteps = int(maxTime/tStep)

  self.x1    = np.zeros(numberTimeSteps)
  self.y1    = np.zeros(numberTimeSteps)
  self.z1    = np.zeros(numberTimeSteps)
  self.time1 = np.zeros(numberTimeSteps)

  self.x0 = Input['x0']
  self.y0 = Input['y0']
  self.z0 = Input['z0']

  self.x1[0] = Input['x0']
  self.y1[0] = Input['y0']
  self.z1[0] = Input['z0']
  self.time1[0]= 0.0

  for t in range (numberTimeSteps-1):
    self.time1[t+1] = self.time1[t] + tStep
    self.x1[t+1]    = self.x1[t] + disc*self.sigma*(self.y1[t]-self.x1[t]) * tStep
    self.y1[t+1]    = self.y1[t] + disc*(self.x1[t]*(self.rho-self.z1[t])-self.y1[t]) * tStep
    self.z1[t+1]    = self.z1[t] + disc*(self.x1[t]*self.y1[t]-self.beta*self.z1[t]) * tStep
