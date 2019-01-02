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
import math
import operator

import layout
import topology
import utils

class Hyperx(topology.Topology):
  """
  This topology is a multi-dimensional HyperX.
  """

  def __init__(self, **kwargs):
    super(Hyperx, self).__init__(**kwargs)

    # mandatory
    self._concentration = None
    self._widths = None
    self._weights = None

    # parse kwargs
    for key in kwargs:
      if key == 'concentration':
        assert self._concentration == None, 'duplicate concentration'
        self._concentration = int(kwargs[key])
      elif key == 'widths':
        assert self._widths == None, 'duplicate widths'
        self._widths = utils.str_to_int_list(kwargs[key])
      elif key == 'weights':
        assert self._weights == None, 'duplicate weights'
        self._weights = utils.str_to_int_list(kwargs[key])
      elif key in super(Hyperx, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # check mandatory were given
    assert (self._concentration != None and self._widths != None and
            self._weights != None), \
            'concentration, widths, and weights must all be specified'

    # check sizes
    if len(self._widths) != len(self._weights) and len(self._widths) > 0:
      raise ValueError('HyperX widths and weight must be equal length')
    for width in self._widths:
      assert width >= 2, 'HyperX widths must be > 1'
    for weight in self._weights:
      assert weight >= 1, 'HyperX weights must be > 0'

    # compute number of routers and nodes
    self._routers = functools.reduce(operator.mul, self._widths)
    self._nodes = self._routers * self._concentration

    # length groups
    self._dims = len(self._widths)
    groups = ['Nodes']
    groups.extend(['Dim{}'.format(d+1) for d in range(self._dims)])
    self._create_cable_groups(groups)

    # compute logical dimensional address distances
    self._router_distances = topology.dim_router_distances(self._widths)
    self._node_distances = topology.dim_node_distances(self._concentration,
                                                       self._widths)

  def structure(self):
    return self._nodes, self._routers

  def interfaces(self):
    yield 1, self._nodes

  def routers(self):
    radix = self._concentration
    for width, weight in zip(self._widths, self._weights):
      radix += ((width - 1) * weight)
    yield radix, self._routers

  def _node_id(self, address):
    return sum(i*j for i,j in zip(address, self._node_distances))

  def _router_id(self, address):
    return sum(i*j for i,j in zip(address, self._router_distances))

  def external_cables(self):
    self._set_cable_group(0)
    for router_address in topology.dim_iter(self._widths):
      router_id = self._router_id(router_address)
      for node in range(self._concentration):
        node_address = [node] + router_address
        node_id = self._node_id(node_address)
        yield node_id, router_id, 1

  def internal_cables(self):
    for dim in range(self._dims):
      self._set_cable_group(dim + 1)
      for source_address in topology.dim_iter(self._widths):
        source_id = self._router_id(source_address)
        for dim_destination in range(source_address[dim] + 1,
                                     self._widths[dim]):
          destination_address = copy.copy(source_address)
          destination_address[dim] = dim_destination
          destination_id = self._router_id(destination_address)
          yield source_id, destination_id, self._weights[dim]
