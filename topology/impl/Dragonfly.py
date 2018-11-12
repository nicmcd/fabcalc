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
  This topology is a standard Dragonfly (1d-1d). The concentration just assumes
  all nodes sit next to the switch chassis.
  """

  def __init__(self, **kwargs):
    super(Dragonfly, self).__init__(**kwargs)

    # mandatory
    self._concentration = None
    self._local_width = None
    self._local_weight = None
    self._global_width = None
    self._global_weight = None
    self._chassis = None  # chassis per rack

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
      elif key == 'chassis':
        assert self._chassis == None, 'duplicate chassis'
        self._chassis = int(kwargs[key])
      elif key in super(Dragonfly, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # check mandatory were given
    assert (self._concentration != None and
            self._local_width != None and
            self._local_weight != None and
            self._global_width != None and
            self._global_weight != None and
            self._chassis != None), \
            ('concentration, local_width, local_weight, global_width, '
             'global weight, and chassis must all be specified')

    # compute number of routers and nodes
    self._routers = self._local_width * self._global_width
    self._nodes = self._routers * self._concentration

    # determine ports on routers
    self._local_ports = ((self._local_width - 1) * self._local_weight)
    self._group_ports = ((self._global_width - 1) * self._global_weight)
    self._global_ports = math.ceil(self._group_ports / self._local_width)

    # make sure groups fit into an integer number of racks
    assert self._local_width % self._chassis == 0, \
      ('groups must fit into an integer number of racks, i.e.,\n'
       '"chassis" must evenly divide "local width"')
    self._racks_per_group = self._local_width // self._chassis

    # determine total number of racks
    self._racks = math.ceil((self._global_width * self._local_width) /
                            self._chassis)

    # lengths
    self._len_fsm = -1
    self._cable_lens = [
      # max, min, lencnt, cblcnt
      [0, 99999999, 0, 0],
      [0, 99999999, 0, 0],
      [0, 99999999, 0, 0],
      [0, 99999999, 0, 0]
    ]

  def structure(self):
    return self._nodes, self._chassis, self._racks

  def routers(self):
    radix = self._concentration + self._local_ports + self._global_ports
    yield radix, self._routers

  def _location(self, lcl, gbl):
    chassis = lcl % self._chassis
    rack = gbl * self._racks_per_group + lcl // self._chassis
    return chassis, rack

  def notify_length(self, length, count):
    # specific dimension
    if length > self._cable_lens[self._len_fsm][0]:
      self._cable_lens[self._len_fsm][0] = length
    if length < self._cable_lens[self._len_fsm][1]:
      self._cable_lens[self._len_fsm][1] = length
    self._cable_lens[self._len_fsm][2] += (length * count)
    self._cable_lens[self._len_fsm][3] += count

    # all cables
    if length > self._cable_lens[0][0]:
      self._cable_lens[0][0] = length
    if length < self._cable_lens[0][1]:
      self._cable_lens[0][1] = length
    self._cable_lens[0][2] += (length * count)
    self._cable_lens[0][3] += count

  def cables(self):
    # connect group
    self._len_fsm = 1
    for group in range(self._global_width):
      for lcl_dist in range(1, self._local_width):
        for lcl_src in range(0, self._local_width - lcl_dist):
          lcl_dst = lcl_src + lcl_dist
          src_chassis, src_rack = self._location(lcl_src, group)
          dst_chassis, dst_rack = self._location(lcl_dst, group)
          source = layout.Coordinate(src_chassis, src_rack)
          destination = layout.Coordinate(dst_chassis, dst_rack)
          yield source, destination, self._local_weight

    # connect groups
    self._len_fsm = 2
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
          src_chassis, src_rack = self._location(src_lcl, src_grp)
          dst_chassis, dst_rack = self._location(dst_lcl, dst_grp)
          source = layout.Coordinate(src_chassis, src_rack)
          destination = layout.Coordinate(dst_chassis, dst_rack)
          yield source, destination, 1

  def info_file(self, filename):
    with open(filename, 'w') as fd:
      for idx, label in enumerate(['all', 'local', 'global']):
        print('{}: ave={:.02f} min={:.02f} max={:.02f}'.format(
          label, self._cable_lens[0][2] / self._cable_lens[idx][3],
          self._cable_lens[idx][1],
          self._cable_lens[idx][0]), file=fd)
