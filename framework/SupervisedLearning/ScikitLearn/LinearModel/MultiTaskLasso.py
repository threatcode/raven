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
  Created on Jan 21, 2020

  @author: alfoa
  Multi-task Lasso model trained with L1/L2 mixed-norm as regularizer

"""
#Internal Modules (Lazy Importer)--------------------------------------------------------------------
#Internal Modules (Lazy Importer) End----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
#External Modules End--------------------------------------------------------------------------------

#Internal Modules------------------------------------------------------------------------------------
from SupervisedLearning.ScikitLearn import ScikitLearnBase
from utils import InputData, InputTypes
#Internal Modules End--------------------------------------------------------------------------------

class MultiTaskLasso(ScikitLearnBase):
  """
    Multi-task Lasso model
  """
  info = {'problemtype':'regression', 'normalize':False}

  def __init__(self):
    """
      Constructor that will appropriately initialize a supervised learning object
      @ In, None
      @ Out, None
    """
    super().__init__()
    import sklearn
    import sklearn.linear_model
    import sklearn.multioutput
    # we wrap the model with the multi output regressor (for multitarget)
    self.model = sklearn.multioutput.MultiOutputRegressor(sklearn.linear_model.MultiTaskLasso())

  @classmethod
  def getInputSpecification(cls):
    """
      Method to get a reference to a class that specifies the input data for
      class cls.
      @ In, cls, the class for which we are retrieving the specification
      @ Out, inputSpecification, InputData.ParameterInput, class to use for
        specifying input of cls.
    """
    specs = super(MultiTaskLasso, cls).getInputSpecification()
    specs.description = r"""The \\xmlNode{MultiTaskLasso} (\\textit{Multi-task Lasso model trained
                        with L1/L2 mixed-norm as regularizer}) is an algorithm for regression problem
                        where the optimization objective for Lasso is:
                        $(1 / (2 * n\_samples)) * ||Y - XW||^2_{Fro} + alpha * ||W||_{21}$
                        \\Where:
                        $||W||_{21} = \sum_i \sqrt{\sum_j w_{ij}^2}$
                        i.e. the sum of norm of each row.
                        """
    specs.addSub(InputData.parameterInputFactory("alpha", contentType=InputTypes.FloatType,
                                                 descr=r"""Constant that multiplies the L1 term. Defaults to 1.0.
                                                 $alpha = 0$ is equivalent to an ordinary least square, solved by
                                                 the LinearRegression object. For numerical reasons, using $alpha = 0$
                                                 with the Lasso object is not advised.""", default=1.0))
    specs.addSub(InputData.parameterInputFactory("tol", contentType=InputTypes.FloatType,
                                                 descr=r"""The tolerance for the optimization: if the updates are smaller
                                                 than tol, the optimization code checks the dual gap for optimality and
                                                 continues until it is smaller than tol..""", default=1.e-4))
    specs.addSub(InputData.parameterInputFactory("fit_intercept", contentType=InputTypes.BoolType,
                                                 descr=r"""Whether the intercept should be estimated or not. If False,
                                                  the data is assumed to be already centered.""", default=True))
    specs.addSub(InputData.parameterInputFactory("normalize", contentType=InputTypes.BoolType,
                                                 descr=r"""This parameter is ignored when fit_intercept is set to False. If True,
                                                 the regressors X will be normalized before regression by subtracting the mean and
                                                 dividing by the l2-norm.""", default=False))
    specs.addSub(InputData.parameterInputFactory("max_iter", contentType=InputTypes.IntegerType,
                                                 descr=r"""The maximum number of iterations.""", default=1000))
    specs.addSub(InputData.parameterInputFactory("selection", contentType=InputTypes.makeEnumType("selection", "selectionType",['cyclic', 'random']),
                                                 descr=r"""If set to ``random'', a random coefficient is updated every iteration
                                                 rather than looping over features sequentially by default. This setting
                                                 often leads to significantly faster convergence especially when tol is higher than $1e-4$""", default='cyclic'))

    return specs

  def _handleInput(self, paramInput):
    """
      Function to handle the common parts of the distribution parameter input.
      @ In, paramInput, ParameterInput, the already parsed input.
      @ Out, None
    """
    super()._handleInput(paramInput)
    settings, notFound = paramInput.findNodesAndExtractValues(['alpha','tol', 'fit_intercept',
                                                               'normalize','max_iter','selection'])
    # notFound must be empty
    assert(not notFound)
    self.initializeModel(settings)
