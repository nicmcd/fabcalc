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

import math
import random

import layout
import utils

class RackAndStack(layout.Layout):
  """
  This is a standard system layout design using switch chassis and node chassis
  """

  def __init__(self, nodes, routers, **kwargs):
    super(RackAndStack, self).__init__(nodes, routers, **kwargs)

    # mandatory
    self._router_bays = None
    self._router_chassis = None
    self._router_chassis_height = None
    self._node_bays = None
    self._node_chassis = None
    self._node_chassis_height = None
    self._max_racks_per_row = None

    # optional
    self._rack_height = utils.meters('42U')
    self._rack_width = utils.meters('24in')
    self._rack_depth = utils.meters('48in')
    self._cold_aisle_width = utils.meters('48in')
    self._hot_aisle_width = utils.meters('36in')
    self._cable_tray_gap = utils.meters('5in')

    # parse kwargs
    for key in kwargs:
      if key == 'router_bays':
        assert self._router_bays == None, 'duplicate router_bays'
        self._router_bays = int(kwargs[key])
      elif key == 'router_chassis':
        assert self._router_chassis == None, 'duplicate router_chassis'
        self._router_chassis = int(kwargs[key])
      elif key == 'router_chassis_height':
        assert self._router_chassis_height == None, \
          'duplicate router_chassis_height'
        self._router_chassis_height = utils.meters(kwargs[key])
      elif key == 'node_bays':
        assert self._node_bays == None, 'duplicate node_bays'
        self._node_bays = int(kwargs[key])
      elif key == 'node_chassis':
        assert self._node_chassis == None, 'duplicate node_chassis'
        self._node_chassis = int(kwargs[key])
      elif key == 'node_chassis_height':
        assert self._node_chassis_height == None, \
          'duplicate node_chassis_height'
        self._node_chassis_height = utils.meters(kwargs[key])
      elif key == 'max_racks_per_row':
        assert self._max_racks_per_row == None, 'duplicate max_racks_per_row'
        self._max_racks_per_row = int(kwargs[key])
      elif key == 'rack_height':
        self._rack_height = utils.meters(kwargs[key])
      elif key == 'rack_width':
        self._rack_width = utils.meters(kwargs[key])
      elif key == 'rack_depth':
        self._rack_depth = utils.meters(kwargs[key])
      elif key == 'cold_aisle_width':
        self._cold_aisle_width = utils.meters(kwargs[key])
      elif key == 'hot_aisle_width':
        self._hot_aisle_width = utils.meters(kwargs[key])
      elif key == 'cable_tray_gap':
        self._cable_tray_gap = utils.meters(kwargs[key])
      elif key in super(RackAndStack, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # compute spacing at the top of the rack
    self._top_of_rack_gap = (
      self._rack_height -
      (self._router_chassis * self._router_chassis_height) -
      (self._node_chassis * self._node_chassis_height))
    assert self._top_of_rack_gap >= 0.0, 'not enough space in rack'

    # center size
    self._routers_per_rack = self._router_bays * self._router_chassis
    self._nodes_per_rack = self._node_bays * self._node_chassis
    total_racks = max(
      math.ceil(self.nodes / self._nodes_per_rack),
      math.ceil(self.routers / self._routers_per_rack))
    racks_per_row = min(self._max_racks_per_row, total_racks)
    self._set_racking(total_racks, racks_per_row)

    # precomputed distances
    self._router_bay_width = self._rack_width / self._router_bays
    self._node_bay_width = self._rack_width / self._node_bays
    self._routers_startx = self._router_bay_width / 2
    self._routers_starty = (self._top_of_rack_gap +
                           (self._router_chassis_height / 2))
    self._nodes_startx = self._node_bay_width / 2
    self._nodes_starty = (self._top_of_rack_gap +
                         (self._router_chassis_height * self._router_chassis) +
                         (self._node_chassis_height / 2))

    # a random number generator
    self._random = random.Random()
    self._random.seed(12345678)

    # state for cable placement
    self._row_first = True

  def _node_coordinate(self, node):
    node_bay = node % self._node_bays
    node_chassis = ((node // self._node_bays) % self._node_chassis)
    node_rack = ((node // self._node_bays) // self._node_chassis)
    return node_bay, node_chassis, node_rack

  def _router_coordinate(self, router):
    router_bay = router % self._router_bays
    router_chassis = (router // self._router_bays) % self._router_chassis
    router_rack = (router // self._router_bays) // self._router_chassis
    return router_bay, router_chassis, router_rack

  def external_cable(self, node, router, count):
    node_bay, node_chassis, node_rack = self._node_coordinate(node)
    router_bay, router_chassis, router_rack = self._router_coordinate(router)

    nx = self._nodes_startx + (node_bay * self._node_bay_width)
    ny = self._nodes_starty + (node_chassis * self._node_chassis_height)
    rx = self._routers_startx + (router_bay * self._router_bay_width)
    ry = self._routers_starty + (router_chassis * self._router_chassis_height)

    if node_rack == router_rack:
      return self._intra_rack_distance(nx, ny, rx, ry)
    else:
      return (self._intra_rack_distance(nx, ny, self._rack_width / 2, 0) +
              self._inter_rack_distance(node_rack, router_rack) +
              self._intra_rack_distance(self._rack_width / 2, 0, rx, ry))

  def internal_cable(self, router1, router2, count):
    router1_bay, router1_chassis, router1_rack = (
      self._router_coordinate(router1))
    router2_bay, router2_chassis, router2_rack = (
      self._router_coordinate(router2))

    ax = self._routers_startx + (router1_bay * self._router_bay_width)
    ay = self._routers_starty + (router1_chassis * self._router_chassis_height)
    bx = self._routers_startx + (router2_bay * self._router_bay_width)
    by = self._routers_starty + (router2_chassis * self._router_chassis_height)

    if router1_rack == router2_rack:
      return self._intra_rack_distance(ax, ay, bx, by)
    else:
      return (self._intra_rack_distance(ax, ay, self._rack_width / 2, 0) +
              self._inter_rack_distance(router1_rack, router2_rack) +
              self._intra_rack_distance(self._rack_width / 2, 0, bx, by))

  def _intra_rack_distance(self, x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

  def _inter_rack_distance(self, rack1, rack2):
    src_col, src_row = self._rack_coords(rack1)
    dst_col, dst_row = self._rack_coords(rack2)
    src_row, dst_row = sorted((src_row, dst_row))
    src_col, dst_col = sorted((src_col, dst_col))

    row_delta = dst_col - src_col
    row_distance = row_delta * self._rack_width

    col_delta = abs(src_row - dst_row)
    hot_unit_distance = self._hot_aisle_width
    cold_unit_distance = 2 * self._rack_depth + self._cold_aisle_width
    if src_row % 2 == 0:
      col_distance = (((col_delta + 1) // 2) * hot_unit_distance +
                      (col_delta // 2) * cold_unit_distance)
    else:
      col_distance = (((col_delta + 1) // 2) * cold_unit_distance +
                      (col_delta // 2) * hot_unit_distance)
    return (2 * self._cable_tray_gap) + row_distance + col_distance

  def _rack_coords(self, rack):
    assert rack < self.total_racks
    row = rack // self.racks_per_row
    col = rack % self.racks_per_row
    assert row < self.rows and col < self.racks_per_row
    return col, row
