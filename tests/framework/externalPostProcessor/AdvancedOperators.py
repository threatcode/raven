'''
Created on 12/23/14

@author: maljdan
'''
import numpy as np
import math

def Norm(self):
  return np.sqrt(np.power(self.A,2) + np.power(self.B,2))

def Mean(self):
  return (self.A + self.B) / 2.

def Sum(self):
  return self.A + self.B

def Delta(self):
  return self.A - self.B

def Max(self):
  return max(max(self.A),max(self.B))

def Min(self):
  return min(min(self.A),min(self.B))
