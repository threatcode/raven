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
# from https://en.wikipedia.org/wiki/Test_functions_for_optimization
#

def evaluate(x,y):
  """
    Evaluates Beale function.
    @ In, x, float, value
    @ In, y, float, value
    @ Out, evaluate, value at x, y
  """
  return 100 * (x - y)**2 + (x + y)**2

def run(raven, inputs):
  """
    RAVEN API
    @ In, raven, object, RAVEN container
    @ In, inputs, dict, additional inputs
    @ Out, None
  """
  raven.ans = evaluate(raven.x, raven.y)
