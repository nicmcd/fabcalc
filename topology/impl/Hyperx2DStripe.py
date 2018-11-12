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

class Hyperx2DStripe(topology.Topology):
  """
  This topology is a 2-dimensional HyperX The concentration just assumes all
  nodes sit next to the switch chassis.
  """

  def __init__(self, **kwargs):
    super(Hyperx2DStripe, self).__init__(**kwargs)

    # mandatory
    self._concentration = None
    self._widths = None
    self._weights = None
    self._chassis = None  # chassis per rack

    # optional
    self._rack_stripe = False

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
      elif key == 'rack_stripe':
        self._rack_stripe = utils.str_to_bool(kwargs[key])
      elif key in super(Hyperx2DStripe, self).using_options():
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
    assert len(self._widths) <= 2, 'This topology supports up to 2 dimensions'
    for width in self._widths:
      assert width >= 2, 'HyperX widths must be > 1'

    # compute number of routers and nodes
    self._routers = functools.reduce(operator.mul, self._widths)
    self._nodes = self._routers * self._concentration

    # adjust the topology into a 2D topology even if it isn't
    dims = len(self._widths)
    for more_dims in range(dims, 2):
      self._widths.append(1)
      self._weights.append(0)
    assert len(self._widths) == 2

    # determine total number of racks
    self._racks = math.ceil((self._widths[0] * self._widths[1]) / self._chassis)

    # lengths
    self._lenmax = 0
    self._lenmin = 9999999
    self._lensum = 0
    self._cblcnt = 0

  def structure(self):
    return self._nodes, self._chassis, self._racks

  def routers(self):
    radix = self._concentration
    for width, weight in zip(self._widths, self._weights):
      radix += ((width - 1) * weight)
    yield radix, self._routers

  def _location(self, d1, d2):
    if not self._rack_stripe:
      chassis_id = (self._widths[0] * d2 + d1)
      rack = chassis_id // self._chassis
      chassis = chassis_id % self._chassis
    else:
      rack = (self._widths[0] * (d2 // self._chassis) + d1)
      chassis = d2 % self._chassis
    assert rack < self._racks
    assert chassis < self._chassis
    return chassis, rack

  def length(self, length, count):
    if length > self._lenmax:
      self._lenmax = length
    if length < self._lenmin:
      self._lenmin = length
    self._lensum += (length * count)
    self._cblcnt += count

  def cables(self):
    # connect dimension 1
    if self._weights[0]:
      for d2 in range(self._widths[1]):
        for d1_dist in range(1, self._widths[0]):
          for d1_src in range(0, self._widths[0] - d1_dist):
            d1_dst = d1_src + d1_dist
            src_chassis, src_rack = self._location(d1_src, d2)
            dst_chassis, dst_rack = self._location(d1_dst, d2)
            source = layout.Coordinate(src_chassis, src_rack)
            destination = layout.Coordinate(dst_chassis, dst_rack)
            yield source, destination, self._weights[0]
    print('dim1: ave={:.02f} min={:.02f} max={:.02f}'.format(
      self._lensum / self._cblcnt, self._lenmin, self._lenmax))
    self._lenmax = 0
    self._lenmin = 9999999
    self._lensum = 0
    self._cblcnt = 0

    # connect dimension 2
    if self._weights[1]:
      for d1 in range(self._widths[0]):
        for d2_dist in range(1, self._widths[1]):
          for d2_src in range(0, self._widths[1] - d2_dist):
            d2_dst = d2_src + d2_dist
            src_chassis, src_rack = self._location(d1, d2_src)
            dst_chassis, dst_rack = self._location(d1, d2_dst)
            source = layout.Coordinate(src_chassis, src_rack)
            destination = layout.Coordinate(dst_chassis, dst_rack)
            yield source, destination, self._weights[1]
    print('dim2: ave={:.02f} min={:.02f} max={:.02f}'.format(
      self._lensum / self._cblcnt, self._lenmin, self._lenmax))
    self._lenmax = 0
    self._lenmin = 9999999
    self._lensum = 0
    self._cblcnt = 0
