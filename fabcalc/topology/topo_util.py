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

import copy
import functools
import operator

def dim_iter(widths):
  """
  This iterates over all addresses in dimension order
  """

  for width in widths:
    assert width >= 2, 'widths must be >= 2'

  dims = len(widths)
  state = [0] * dims
  more = True

  while more:
    address = copy.copy(state)
    for dim in range(dims):
      if state[dim] == widths[dim] - 1:
        if dim == dims - 1:
          more = False
          break
        else:
          state[dim] = 0
      else:
        state[dim] += 1
        break
    yield address

def dim_router_distances(widths):
  """
  This generates dimensional router distances
  """
  router_distances = [0] * len(widths)
  for idx in range(len(widths)):
    if idx == 0:
      router_distances[idx] = 1
    else:
      router_distances[idx] = functools.reduce(operator.mul, widths[0:idx])
  return router_distances

def dim_node_distances(concentration, widths):
  """
  This generates dimensional node distances
  """
  node_distances = [0] * (len(widths) + 1)
  nwidths = [concentration] + widths
  for idx in range(len(widths) + 1):
    if idx == 0:
      node_distances[idx] = 1
    else:
      node_distances[idx] = functools.reduce(operator.mul, nwidths[0:idx])
  return node_distances
