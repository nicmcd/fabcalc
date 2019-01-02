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

class Topology(object):
  """
  This is an abstract class that represents a fabric technology
  The 'topology' defines structure and makes connections
  """

  @staticmethod
  def using_options():
    """
    Tells the base class which option keys it uses
    """
    return []

  def __init__(self, **kwargs):
    """
    Constructs a Topology object
    """
    self._cable_groups = [[0, 99999999, 0, 0, 'All']]
    self._cable_group = -1

  def _create_cable_groups(self, names):
    """
    This create cable groups so that each topology can have specific groups

    Args:
      names (str array) : the names of the groups
    """
    for name in names:
      self._cable_groups.append([0, 99999999, 0, 0, name])

  def _set_cable_group(self, group):
    """
    Sets the group that the next generated cables will assigned to

    Args:
      group (int) : group identifier
    """
    assert group < len(self._cable_groups) - 1, 'invalid group id'
    self._cable_group = group

  def structure(self):
    """
    This returns the structure of the system in terms of:
    nodes       : total number of nodes
    chassis     : number of chassis per rack
    total_racks : total number of racks

    Returns:
      tuple (int, int, int, int) : nodes, chassis, racks, rows
    """
    raise NotImplementedError('subclasses must override this')

  def interfaces(self):
    """
    This is a generator that generates (radix, count) tuples
    'radix' and 'count' are of type int
    """
    raise NotImplementedError('subclasses must override this')

  def routers(self):
    """
    This is a generator that generates (radix, count) tuples
    'radix' and 'count' are of type int
    """
    raise NotImplementedError('subclasses must override this')

  def external_cables(self):
    """
    This is a generator that generates (node, router, count) tuples.
    'node' is a node ID. 'router' is a router ID. Both are of type int.
    'count' is of type int
    """
    raise NotImplementedError('subclasses must override this')

  def internal_cables(self):
    """
    This is a generator that generates (router, router, count) tuples.
    'router' is a router ID. Both are of type int. 'count' is of type int
    """
    raise NotImplementedError('subclasses must override this')

  def notify_length(self, length, count):
    """
    This notifies the topology of the length of cables generated. This
    is used by the topology to generate topology specific cable length
    statistics.

    Args:
      length  : length of cable
      count   : count of cables
    """
    # all cables
    if length > self._cable_groups[0][0]:
      self._cable_groups[0][0] = length
    if length < self._cable_groups[0][1]:
      self._cable_groups[0][1] = length
    self._cable_groups[0][2] += (length * count)
    self._cable_groups[0][3] += count

    # specific groups
    if len(self._cable_groups) > 1:
      if length > self._cable_groups[self._cable_group + 1][0]:
        self._cable_groups[self._cable_group + 1][0] = length
      if length < self._cable_groups[self._cable_group + 1][1]:
        self._cable_groups[self._cable_group + 1][1] = length
      self._cable_groups[self._cable_group + 1][2] += (length * count)
      self._cable_groups[self._cable_group + 1][3] += count


  def info_file(self, filename):
    """
    This writes topology specific information to a file

    Args:
      filename (str) : the file to be written
    """
    with open(filename, 'w') as fd:
      for group in self._cable_groups:
        ave = 0
        if group[3] > 0:
          ave = group[2] / group[3]
        print('{}: ave={:.02f} min={:.02f} max={:.02f}'.format(
          group[4], ave, group[1], group[0]), file=fd)
