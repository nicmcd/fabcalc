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

class Hyperx(topology.Topology):
  """
  This topology is a multi-dimensional HyperX. The topology works with 1D, 2D,
  and 3D specifications. The concentration just assumes all nodes sit next to
  the switch chassis.
  """

  def __init__(self, **kwargs):
    super(Hyperx, self).__init__(**kwargs)

    # mandatory
    self._concentration = None
    self._widths = None
    self._weights = None
    self._chassis = None  # chassis per rack

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
      elif key == 'chassis':
        assert self._chassis == None, 'duplicate chassis'
        self._chassis = int(kwargs[key])
      elif key in super(HyperxD1Rack, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # check mandatory were given
    assert (self._concentration != None and self._widths != None and
            self._weights != None and self._chassis != None), \
            'concentration, widths, weights, and chassis must all be specified'

    # check sizes
    if len(self._widths) != len(self._weights) and len(self._widths) > 0:
      raise ValueError('HyperX widths and weight must be equal length')
    assert len(self._widths) <= 3, 'This topology supports up to 3 dimensions'
    for width in self._widths:
      assert width >= 2, 'HyperX widths must be > 1'
    for weight in self._weights:
      assert weight >= 1, 'HyperX weights must be > 0'

    # compute number of routers and nodes
    self._routers = functools.reduce(operator.mul, self._widths)
    self._nodes = self._routers * self._concentration

    # make sure groups fit into an integer number of racks
    assert self._widths[0] % self._chassis == 0, \
      ('The first dimension must fit into an integer number of racks, i.e.,\n'
       '"chassis" must evenly divide "widths[0]')
    self._racks_per_d1 = self._widths[0] // self._chassis

    # determine total number of racks
    assert self._routers % self._chassis == 0, "PROGRAMMER ERROR"
    self._racks = math.ceil(self._routers / self._chassis)

    # adjust the topology into a 3D topology even if it isn't
    dims = len(self._widths)
    for more_dims in range(dims, 3):
      self._widths.append(1)
      self._weights.append(0)
    assert len(self._widths) == 3

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
    radix = self._concentration
    for width, weight in zip(self._widths, self._weights):
      radix += ((width - 1) * weight)
    yield radix, self._routers

  def _location(self, d1, d2, d3):
    chassis = d1 % self._chassis
    rack = (((self._widths[1] * d3 + d2) * self._racks_per_d1) +
            (d1 // self._chassis))
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
    # connect dimension 1
    self._len_fsm = 1
    for d3 in range(self._widths[2]):
      for d2 in range(self._widths[1]):
        for d1_dist in range(1, self._widths[0]):
          for d1_src in range(0, self._widths[0] - d1_dist):
            d1_dst = d1_src + d1_dist
            src_chassis, src_rack = self._location(d1_src, d2, d3)
            dst_chassis, dst_rack = self._location(d1_dst, d2, d3)
            source = layout.Coordinate(src_chassis, src_rack)
            destination = layout.Coordinate(dst_chassis, dst_rack)
            yield source, destination, self._weights[0]

    # connect dimension 2
    self._len_fsm = 2
    if self._weights[1]:
      for d3 in range(self._widths[2]):
        for d1 in range(self._widths[0]):
          for d2_dist in range(1, self._widths[1]):
            for d2_src in range(0, self._widths[1] - d2_dist):
              d2_dst = d2_src + d2_dist
              src_chassis, src_rack = self._location(d1, d2_src, d3)
              dst_chassis, dst_rack = self._location(d1, d2_dst, d3)
              source = layout.Coordinate(src_chassis, src_rack)
              destination = layout.Coordinate(dst_chassis, dst_rack)
              yield source, destination, self._weights[1]

    # connect dimension 3
    self._len_fsm = 3
    if self._weights[2]:
      for d2 in range(self._widths[1]):
        for d1 in range(self._widths[0]):
          for d3_dist in range(1, self._widths[2]):
            for d3_src in range(0, self._widths[2] - d3_dist):
              d3_dst = d3_src + d3_dist
              src_chassis, src_rack = self._location(d1, d2, d3_src)
              dst_chassis, dst_rack = self._location(d1, d2, d3_dst)
              source = layout.Coordinate(src_chassis, src_rack)
              destination = layout.Coordinate(dst_chassis, dst_rack)
              yield source, destination, self._weights[2]

  def info_file(self, filename):
    with open(filename, 'w') as fd:
      print('all: ave={:.02f} min={:.02f} max={:.02f}'.format(
        self._cable_lens[0][2] / self._cable_lens[0][3],
        self._cable_lens[0][1],
        self._cable_lens[0][0]), file=fd)
      for dim in range(1, 4):
        ave = 0
        if self._cable_lens[dim][3] > 0:
          ave = self._cable_lens[dim][2] / self._cable_lens[dim][3]
        print('dim{}: ave={:.02f} min={:.02f} max={:.02f}'.format(
          dim, ave, self._cable_lens[dim][1], self._cable_lens[dim][0]),
          file=fd)
