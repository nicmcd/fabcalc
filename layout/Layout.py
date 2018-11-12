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
import numpy

class Layout(object):
  """
  This is an abstract class that represents a system layout.

  Layouts are specified in 3 dimensional space (rows of racks). A coordinate in
  the system specifies a row, rack of the row, and chassis of the rack. The
  chassis are numbered numerically in order. The 0th chassis is at the bottom of
  the rack for layouts that use subfloor for cabling. The top of the rack is
  used for layouts that use cable trays above the rack.
  """

  @staticmethod
  def using_options():
    """
    Tells the base class which option keys it uses
    """
    return ['racks_per_row']

  def __init__(self, chassis, total_racks, **kwargs):
    """
    Constructs a Layout object

    Args:
      chassis (int) : number of vertical chassis units per rack
      total_racks (int) : total number of racks
    """

    self.chassis = chassis
    self.total_racks = total_racks
    self.racks_per_row = int(kwargs.get('racks_per_row', 16))
    self.rows = math.ceil(total_racks / self.racks_per_row)

    # create an array to hold number of cables between racks
    #  these are counters for cable trays
    self._actual_racks_per_row = min(self.racks_per_row, self.total_racks)
    self._row_cables = numpy.zeros((self.rows, self._actual_racks_per_row - 1))
    self._col_cables = numpy.zeros((self._actual_racks_per_row, self.rows - 1))

  def length(self, source, destination, count):
    """
    This returns a length in meters from the source to the destination

    Args:
      source (Coordinate) : the source coordinate of the cable
      destination (Coordinate) : the destination coordinate of the cable
      count (int) : the count of cables following this route
    """
    raise NotImplementedError('subclasses must implement this')

  def row_cable_strand(self, row, start, end, count):
    """
    This adds a cable strand down a row for cable tray accounting

    Args:
      row (int) : row ID
      start (int) : column rack ID where strand starts
      end (int) : column rack ID where strand ends
      count (int) : number of cables being accounted
    """
    assert end >= start, 'end must be >= start'
    if end > start:
      for loc in range(start, end):
        self._row_cables[row, loc] += count

  def col_cable_strand(self, col, start, end, count):
    """
    This adds a cable strand down a column for cable tray accounting

    Args:
      row (int) : column ID
      start (int) : row rack ID where strand starts
      end (int) : row rack ID where strand ends
      count (int) : row of cables being accounted
    """
    assert end >= start, 'end must be >= start'
    if end > start:
      for loc in range(start, end):
        self._col_cables[col, loc] += count

  def cable_tray_csv(self, filename):
    """
    Writes the cable tray information to the specified CSV file
    """

    with open(filename, 'w') as fd:
      # loop over each row
      for row in range(self.rows):
        # print the row
        fd.write('R,')
        for idx, col in enumerate(self._row_cables[row]):
          last = idx == len(self._row_cables[row]) - 1
          fd.write('{},R{}'.format(col, '' if last else ','))
        fd.write('\n')

        # print the row-to-row
        if row < self.rows - 1:
          for col in range(self._actual_racks_per_row):
            value = self._col_cables[col, row]
            last = col == self._actual_racks_per_row - 1
            fd.write('{}{}'.format(value, '' if last else ',-,'))
          fd.write('\n')
