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
    return []

  def __init__(self, nodes, routers, **kwargs):
    """
    Constructs a Layout object

    Args:
      node    (int) : number of nodes
      routers (int) : number of routers
    """
    self.nodes = nodes
    self.routers = routers

  def _set_racking(self, total_racks, racks_per_row):
    """
    Subclasses must call this within their constructor

    Args:
      total_racks (int)   : total number of racks
      racks_per_row (int) : number of racks per row
    """
    assert racks_per_row <= total_racks, 'or racks per row than total racks!'
    self.total_racks = total_racks
    self.racks_per_row = racks_per_row
    self.rows = math.ceil(self.total_racks / self.racks_per_row)

    # create an array to hold number of cables between racks
    #  these are counters for cable trays
    self._row_cables = numpy.zeros((self.rows, self.racks_per_row - 1))
    self._col_cables = numpy.zeros((self.racks_per_row, self.rows - 1))

  def external_cable(self, node, router, count):
    """
    This returns registers a cable from a node to a router.
    This function returns the length of the cable in meters.

    Args:
      node   (int) : the node this cable connects to
      router (int) : the router this cable connects to
      count  (int) : the count of cables following this route

    Returns:
      (float) : length of cable in meters
    """
    raise NotImplementedError('subclasses must implement this')

  def internal_cable(self, router1, router2, count):
    """
    This returns registers a cable from a router to a router.
    This function returns the length of the cable in meters.

    Args:
      router1 (int) : the first router this cable connects to
      router2 (int) : the second router this cable connects to
      count   (int) : the count of cables following this route

    Returns:
      (float) : length of cable in meters
    """
    raise NotImplementedError('subclasses must implement this')

  def _row_cable_strand(self, row, start, end, count):
    """
    This adds a cable strand down a row for cable tray accounting

    Args:
      row   (int) : row ID
      start (int) : column rack ID where strand starts
      end   (int) : column rack ID where strand ends
      count (int) : number of cables being accounted
    """
    assert end >= start, 'end must be >= start'
    if end > start:
      for loc in range(start, end):
        self._row_cables[row, loc] += count

  def _col_cable_strand(self, col, start, end, count):
    """
    This adds a cable strand down a column for cable tray accounting

    Args:
      row   (int) : column ID
      start (int) : row rack ID where strand starts
      end   (int) : row rack ID where strand ends
      count (int) : row of cables being accounted
    """
    assert end >= start, 'end must be >= start'
    if end > start:
      for loc in range(start, end):
        self._col_cables[col, loc] += count

  def cable_tray_csv(self, filename):
    """
    Writes the cable tray information to the specified CSV file

    Args:
      filename (str) : name of file to be written
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
          for col in range(self.racks_per_row):
            value = self._col_cables[col, row]
            last = col == self.racks_per_row - 1
            fd.write('{}{}'.format(value, '' if last else ',-,'))
          fd.write('\n')
