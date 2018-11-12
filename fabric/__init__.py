"""
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - Neither the name of prim nor the names of its contributors may be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 *
 * See the NOTICE file distributed with this work for additional information
 * regarding copyright ownership.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

from .Cable import *
from .Router import *
from .Fabric import *

import os
import sys
import importlib

def generate():
  # dynamically find and import modules
  this_dir = os.path.dirname(__file__)
  impl_dir = os.path.join(this_dir, 'impl')
  models = {}
  if os.path.isdir(impl_dir):
    for filename in os.listdir(impl_dir):
      if filename.endswith('.py'):
        model = filename[:-3]
        module = os.path.basename(this_dir) + '.impl.' + model
        module = importlib.import_module(module)
        constructor = getattr(module, model)
        models[filename[:-3]] = constructor

  # create and return a factory function
  def factory(model, **kwargs):
    if model in models:
      return models[model](**kwargs)
    raise ValueError('Fabric model \'{}\' not loaded'.format(model))
  return factory

# set the fabric factory
setattr(sys.modules[__name__], 'factory', generate())
delattr(sys.modules[__name__], 'generate')
