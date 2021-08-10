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
"""
  Created on Jun 30, 2021

  @author: wangc
  QuadraticDiscriminantAnalysis
  Classifier implementing Discriminant Analysis (Quadratic) classification

"""
#Internal Modules (Lazy Importer)--------------------------------------------------------------------
#Internal Modules (Lazy Importer) End----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
#External Modules End--------------------------------------------------------------------------------

#Internal Modules------------------------------------------------------------------------------------
from SupervisedLearning.ScikitLearn import ScikitLearnBase
#from .. import ScikitLearnBase
from utils import InputData, InputTypes
#Internal Modules End--------------------------------------------------------------------------------

class QuadraticDiscriminantAnalysisClassifier(ScikitLearnBase):
  """
    KNeighborsClassifier
    Classifier implementing the k-nearest neighbors vote.
  """
  info = {'problemtype':'classification', 'normalize':False}

  def __init__(self):
    """
      Constructor that will appropriately initialize a supervised learning object
      @ In, None
      @ Out, None
    """
    super().__init__()
    import sklearn
    import sklearn.discriminant_analysis
    import sklearn.multioutput
    # we wrap the model with the multi output classifier (for multitarget)
    self.model = sklearn.multioutput.MultiOutputClassifier(sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis())

  @classmethod
  def getInputSpecification(cls):
    """
      Method to get a reference to a class that specifies the input data for
      class cls.
      @ In, cls, the class for which we are retrieving the specification
      @ Out, inputSpecification, InputData.ParameterInput, class to use for
        specifying input of cls.
    """
    specs = super(QuadraticDiscriminantAnalysisClassifier, cls).getInputSpecification()
    specs.description = r"""The \xmlNode{QuadraticDiscriminantAnalysisClassifier} is a classifier with a quadratic decision boundary,
    generated by fitting class conditional densities to the data and using Bayes' rule.
    The model fits a Gaussian density to each class"""

    specs.addSub(InputData.parameterInputFactory("priors", contentType=InputTypes.FloatListType,
                                                 descr=r"""The class prior probabilities. By default, the class proportions are inferred from the training data.""", default=None))
    specs.addSub(InputData.parameterInputFactory("reg_param", contentType=InputTypes.FloatType,
                                                 descr=r"""Regularizes the per-class covariance estimates by transforming
                                                 S2 as S2 = (1 - reg\_param) * S2 + reg\_param * np.eye(n\_features), where S2 corresponds to the
                                                 scaling\_ attribute of a given class.""", default=0.0))
    specs.addSub(InputData.parameterInputFactory("store_covariance", contentType=InputTypes.BoolType,
                                                 descr=r"""If True, the class covariance matrices are explicitely computed and stored in the self.covariance\_ attribute.""",
                                                 default=False))
    specs.addSub(InputData.parameterInputFactory("tol", contentType=InputTypes.FloatType,
                                                 descr=r"""Absolute threshold for a singular value to be considered significant, used to estimate
                                                 the rank of Xk where Xk is the centered matrix of samples in class k. This parameter does not affect
                                                 the predictions. It only controls a warning that is raised when features are considered to be colinear.""",
                                                 default=1.0e-4))
    return specs

  def _handleInput(self, paramInput):
    """
      Function to handle the common parts of the distribution parameter input.
      @ In, paramInput, ParameterInput, the already parsed input.
      @ Out, None
    """
    super()._handleInput(paramInput)
    settings, notFound = paramInput.findNodesAndExtractValues(['priors', 'reg_param', 'store_covariance', 'tol'])
    # notFound must be empty
    assert(not notFound)
    self.initializeModel(settings)
