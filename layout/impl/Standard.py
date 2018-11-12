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

class Standard(layout.Layout):
  """
  This is a standard system layout design optionally with CDUs
  """

  def __init__(self, chassis, total_racks, **kwargs):
    super(Standard, self).__init__(chassis, total_racks, **kwargs)

    # optional
    self._rack_height = utils.meters('48U')
    self._rack_width = utils.meters('24in')
    self._rack_depth = utils.meters('48in')
    self._cold_aisle_width = utils.meters('48in')
    self._hot_aisle_width = utils.meters('36in')
    self._cable_tray_gap = utils.meters('5in')
    self._cdu_width = utils.meters('24in')
    self._racks_per_cdu = 4

    # parse kwargs
    for key in kwargs:
      if key == 'rack_height':
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
      elif key == 'cdu_width':
        self._cdu_width = utils.meters(kwargs[key])
      elif key == 'racks_per_cdu':
        self._racks_per_cdu = int(kwargs[key])
      elif key in super(Standard, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # precompute intra-rack distance
    self._rack_unit_distance = self._rack_height / self.chassis

    # precompute CDU locations
    cdus_per_row = math.ceil(self.racks_per_row / self._racks_per_cdu)
    racks_left = self.racks_per_row
    cdu_block_racks = []
    while len(cdu_block_racks) < cdus_per_row:
      racks_in_block = min(racks_left, self._racks_per_cdu)
      cdu_block_racks.append(racks_in_block)
      racks_left -= racks_in_block
    self._cdu_locs = []
    next_rack = 0
    for cdu in range(cdus_per_row):
      block_dist = cdu_block_racks[cdu]
      self._cdu_locs.append(next_rack + math.ceil(block_dist / 2) - 1)
      next_rack += block_dist

    # a random number generator
    self._random = random.Random()
    self._random.seed(12345678)

    # state for cable placement
    self._row_first = True

  def length(self, source, destination, count):
    same_rack = source.rack == destination.rack
    if same_rack:
      delta = abs(source.chassis - destination.chassis)
      return delta * self._rack_unit_distance

    else:
      # compute distance in and out of the racks
      out_distance = (source.chassis * self._rack_unit_distance +
                      self._cable_tray_gap)
      in_distance = (source.chassis * self._rack_unit_distance +
                     self._cable_tray_gap)

      # determine row and col of rack
      src_col, src_row = self._rack_loc(source.rack)
      dst_col, dst_row = self._rack_loc(destination.rack)
      src_row, dst_row = sorted((src_row, dst_row))
      src_col, dst_col = sorted((src_col, dst_col))

      # compute rack to rack distance within a row
      cdus = 0
      for cdu_loc in self._cdu_locs:
        if cdu_loc >= src_col and dst_col > cdu_loc:
          cdus += 1
      row_delta = (dst_col - src_col) + (cdus * self._cdu_width)
      row_distance = row_delta * self._rack_width

      # compute row to row distance
      col_delta = abs(src_row - dst_row)
      hot_unit_distance = self._hot_aisle_width
      cold_unit_distance = 2 * self._rack_depth + self._cold_aisle_width
      col_distance = (((col_delta + 1) // 2) * hot_unit_distance +
                      (col_delta // 2) * cold_unit_distance)

      # do accounting for the cable trays
      #  this algorithm uses row-then-col placement
      src_col, src_row = self._rack_loc(source.rack)
      dst_col, dst_row = self._rack_loc(destination.rack)
      if self._row_first:  #self._random.random() < 0.5:
        row, col = src_row, dst_col
      else:
        row, col = dst_row, src_col
      self._row_first = not self._row_first
      src_row, dst_row = sorted((src_row, dst_row))
      src_col, dst_col = sorted((src_col, dst_col))
      self.row_cable_strand(row, src_col, dst_col, count)
      self.col_cable_strand(col, src_row, dst_row, count)

      # return the total distance
      return out_distance + row_distance + col_distance + in_distance


  def _rack_loc(self, rack):
    """
    This maps a group index to a rack col,row coordinate
    """
    assert rack < self.total_racks
    row = rack // self.racks_per_row
    col = rack % self.racks_per_row
    assert row < self.rows and col < self.racks_per_row
    return col, row
