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

class FatTree(topology.Topology):
  """
  A standard 3-level fat tree using leaf switches and director switches.
  """

  def __init__(self, **kwargs):
    super(FatTree, self).__init__(**kwargs)

    # mandatory
    self._leaves = None
    self._down_ports = None
    self._up_ports = None
    self._leaves_per_rack = None
    self._directors_per_rack = None
    self._director_radix = None
    self._director_rack_inset = None

    # parse kwargs
    for key in kwargs:
      if key == 'leaves':
        self._leaves = int(kwargs[key])
      elif key == 'down_ports':
        self._down_ports = int(kwargs[key])
      elif key == 'up_ports':
        self._up_ports = int(kwargs[key])
      elif key == 'leaves_per_rack':
        self._leaves_per_rack = int(kwargs[key])
      elif key == 'directors_per_rack':
        self._directors_per_rack = int(kwargs[key])
      elif key == 'director_radix':
        self._director_radix = int(kwargs[key])
      elif key == 'director_rack_inset':
        self._director_rack_inset = int(kwargs[key])
      elif key in super(FatTree, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # check mandatory were given
    assert (self._leaves != None and
            self._down_ports != None and
            self._up_ports != None and
            self._leaves_per_rack != None and
            self._directors_per_rack != None and
            self._director_radix != None and
            self._director_rack_inset != None), \
            ('leaves, down_ports, up_ports, leaves_per_rack, '
             'directors_per_rack, director_radix, and director_rack_inset '
             'must all be specified')

    # compute number of routers and nodes
    total_up_links = self._leaves * self._up_ports
    self._directors = math.ceil(total_up_links / self._director_radix)
    self._routers = self._leaves + self._directors
    self._nodes = self._leaves * self._down_ports

    # determine director rack locations
    leaf_racks = math.ceil(self._leaves / self._leaves_per_rack)
    director_racks = math.ceil(self._directors / self._directors_per_rack)
    self._total_racks = leaf_racks + director_racks
    leaf_racks_per_set = self._director_rack_inset * 2
    rack_sets = leaf_racks // leaf_racks_per_set
    director_racks_per_set = math.ceil(director_racks / rack_sets)
    self._director_locations = []
    rack_index = self._director_rack_inset
    director_rack_count = 0
    done = False
    while not done:
      # add director locations in current rack
      for d in range(self._directors_per_rack):
        if len(self._director_locations) == director_racks:
          done = True
          break
        else:
          self._director_locations.append(rack_index)
      # advance to next director rack
      director_rack_count += 1
      rack_index += 1
      if director_rack_count == director_racks_per_set:
        director_rack_count = 0
        rack_index += leaf_racks_per_set
    assert len(self._director_locations) == director_racks

    # max, min, lencnt, cblcnt
    self._cable_lens = [0, 99999999, 0, 0]

  def structure(self):
    return self._nodes, self._leaves_per_rack, self._total_racks

  def routers(self):
    radix = self._down_ports + self._up_ports
    yield radix, self._leaves
    yield self._director_radix, self._directors

  def notify_length(self, length, count):
    if length > self._cable_lens[0]:
      self._cable_lens[0] = length
    if length < self._cable_lens[1]:
      self._cable_lens[1] = length
    self._cable_lens[2] += (length * count)
    self._cable_lens[3] += count

  def cables(self):
    # connect leaves to directors
    for leaf in range(self._leaves):
      # determine the leaf's chassis within a rack
      leaf_chassis = leaf % self._leaves_per_rack
      # determine the leaf's rack
      leaf_rack = leaf // self._leaves_per_rack
      for director_location in self._director_locations:
        if leaf_rack >= director_location:
          leaf_rack += 1
      # verify leaf rack isn't a director rack
      assert leaf_rack not in self._director_locations
      # connect this leaf to all directors for all uplinks
      for uplink in range(self._up_ports):
        # get the directors rack
        director_index = uplink % self._directors
        director_rack = self._director_locations[director_index]
        # find the director chassis in switch chassis terms
        director_chassis = director_index % self._directors_per_rack
        director_chassis *= (self._leaves_per_rack // self._directors_per_rack)
        # get source and destination and yield the cable
        source = layout.Coordinate(leaf_chassis, leaf_rack)
        destination = layout.Coordinate(director_chassis, director_rack)
        yield source, destination, 1

    # connect director ASICs to each other
    """
    for director_rack in self._director_locations:
      director_chassis = director_index % self._directors_per_rack
      source_chassis = director_chassis
      director_chassis *= (self._leaves_per_rack / self._directors_per_rack)
      destination_chassis = director_chassis + 1 if director_chassis == 0 else director_chassis
    """

  def info_file(self, filename):
    with open(filename, 'w') as fd:
      print('all: ave={:.02f} min={:.02f} max={:.02f}'.format(
        self._cable_lens[2] / self._cable_lens[3],
        self._cable_lens[1],
        self._cable_lens[0]), file=fd)
