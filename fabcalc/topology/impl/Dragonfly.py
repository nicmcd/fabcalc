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

import functools
import math
import operator

import layout
import topology
import utils

class Dragonfly(topology.Topology):
  """
  This topology is a standard Dragonfly (1d-1d).
  """

  def __init__(self, **kwargs):
    super(Dragonfly, self).__init__(**kwargs)

    # mandatory
    self._concentration = None
    self._local_width = None
    self._local_weight = None
    self._global_width = None
    self._global_weight = None

    # parse kwargs
    for key in kwargs:
      if key == 'concentration':
        assert self._concentration == None, 'duplicate concentration'
        self._concentration = int(kwargs[key])
      elif key == 'local_width':
        assert self._local_width == None, 'duplicate local width'
        self._local_width = int(kwargs[key])
      elif key == 'local_weight':
        assert self._local_weight == None, 'duplicate local weight'
        self._local_weight = int(kwargs[key])
      elif key == 'global_width':
        assert self._global_width == None, 'duplicate global width'
        self._global_width = int(kwargs[key])
      elif key == 'global_weight':
        assert self._global_weight == None, 'duplicate global weight'
        self._global_weight = int(kwargs[key])
      elif key in super(Dragonfly, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # check mandatory were given
    assert (self._concentration != None and
            self._local_width != None and
            self._local_weight != None and
            self._global_width != None and
            self._global_weight != None), \
            ('concentration, local_width, local_weight, global_width, '
             'and global weight must all be specified')

    # compute number of routers and nodes
    self._routers = self._local_width * self._global_width
    self._nodes = self._routers * self._concentration

    # determine ports on routers
    self._local_ports = (self._local_width - 1) * self._local_weight
    self._group_ports = (self._global_width - 1) * self._global_weight
    self._global_ports = math.ceil(self._group_ports / self._local_width)

    # length groups
    self._create_cable_groups(['Nodes', 'Local', 'Global'])

    # compute logical dimensional address distances
    self._router_distances = [1, self._local_width]
    self._node_distances = [1, self._concentration, self._local_width *
                            self._concentration]

  def structure(self):
    return self._nodes, self._routers

  def interfaces(self):
    yield 1, self._nodes

  def routers(self):
    radix = self._concentration + self._local_ports + self._global_ports
    yield radix, self._routers

  def _node_id(self, address):
    return sum(i*j for i,j in zip(address, self._node_distances))

  def _router_id(self, address):
    return sum(i*j for i,j in zip(address, self._router_distances))

  def external_cables(self):
    self._set_cable_group(0)
    for router_address in topology.dim_iter(
        [self._local_width, self._global_width]):
      router_id = self._router_id(router_address)
      for node in range(self._concentration):
        node_address = [node] + router_address
        node_id = self._node_id(node_address)
        yield node_id, router_id, 1

  def internal_cables(self):
    # local
    self._set_cable_group(1)
    for group in range(self._global_width):
      for lcl_dist in range(1, self._local_width):
        for lcl_src in range(0, self._local_width - lcl_dist):
          lcl_dst = lcl_src + lcl_dist

          source_address = [lcl_src, group]
          destination_address = [lcl_dst, group]

          source_id = self._router_id(source_address)
          destination_id = self._router_id(destination_address)
          yield source_id, destination_id, self._local_weight

    # global
    self._set_cable_group(2)
    for gbl_dist in range(1, self._global_width):
      for src_grp in range(0, self._global_width - gbl_dist):
        dst_grp = src_grp + gbl_dist
        for weight in range(self._global_weight):
          src_grp_port = ((dst_grp - 1) + ((self._global_width - 1) * weight))
          assert src_grp_port < self._group_ports
          src_lcl = src_grp_port // self._global_ports
          dst_grp_port = (src_grp + ((self._global_width - 1) * weight))
          assert dst_grp_port < self._group_ports
          dst_lcl = dst_grp_port // self._global_ports

          source_address = [src_lcl, src_grp]
          destination_address = [dst_lcl, dst_grp]

          source_id = self._router_id(source_address)
          destination_id = self._router_id(destination_address)
          yield source_id, destination_id, 1
