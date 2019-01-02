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

from collections import OrderedDict
import gridstats
import json
import math
import numpy
import sys

import fabcalc.utils

class Fabric(object):
  """
  This is an abstract class that represents a fabric technology
  The 'fabric' includes routers and cables
  """

  @staticmethod
  def using_options():
    """
    Tells the base class which option keys it uses
    """
    return ['partial_cables', 'cable_granularity']

  def __init__(self, **kwargs):
    """
    Constructs a Fabric object
    """
    # implementations must respect this
    self.partial_cables = fabcalc.utils.str_to_bool(
      kwargs.get('partial_cables', '0'))

    self._interfaces = {}  # radix->[router, count]
    self._routers = {}  # radix->[router, count]
    self._cables = {}  # actual_length->[cable,count]

    self._cable_granularity = fabcalc.utils.meters(
      kwargs.get('cable_granularity', '0.5m'))

  def add_interface(self, minimum_radix, count=1):
    """
    Adds interfaces to the fabric
    """
    assert count > 0, 'a zero number of interfaces?'

    # make the router
    interface = self._make_interface(minimum_radix)

    # add the router
    if interface.radix not in self._interfaces:
      self._interfaces[interface.radix] = [interface, 0]
    self._interfaces[interface.radix][1] += count

  def add_router(self, minimum_radix, count=1):
    """
    Adds routers to the fabric
    """
    assert count > 0, 'a zero number of routers?'

    # make the router
    router = self._make_router(minimum_radix)

    # add the router
    if router.radix not in self._routers:
      self._routers[router.radix] = [router, 0]
    self._routers[router.radix][1] += count

  def add_cable(self, minimum_length, count=1):
    """
    Adds cables to the fabric
    """
    assert count > 0, 'a zero number of cables?'

    # apply cable granularity
    minimum_length = (math.ceil(minimum_length / self._cable_granularity) *
                      self._cable_granularity)

    # make the cable
    cable = self._make_cable(minimum_length)

    # add the cable
    if cable.actual_length not in self._cables:
      self._cables[cable.actual_length] = [cable, 0]
    self._cables[cable.actual_length][1] += count

  def set_attributes(self):
    """
    This is called after all interface, routers, and cables have added to the
    model.
    """
    for _, ii in self._interfaces.items():
      self._set_interface_attributes(ii[0], ii[1])
    for _, ri in self._routers.items():
      self._set_router_attributes(ri[0], ri[1])
    for _, ci in self._cables.items():
      self._set_cable_attributes(ci[0], ci[1])

  def summary(self, nodes, filename):
    """
    Writes a summary JSON file
    """
    # determine total interface values
    interface_count = 0
    interface_cost = 0
    interface_power = 0
    for radix in sorted(self._interfaces):
      interface_count += self._interfaces[radix][1]
      interface_cost += (self._interfaces[radix][0].cost *
                         self._interfaces[radix][1])
      interface_power += (self._interfaces[radix][0].power *
                          self._interfaces[radix][1])

    # determine total router values
    router_count = 0
    router_cost = 0
    router_power = 0
    for radix in sorted(self._routers):
      router_count += self._routers[radix][1]
      router_cost += (self._routers[radix][0].cost * self._routers[radix][1])
      router_power += (self._routers[radix][0].power * self._routers[radix][1])

    # determine total cable values
    cable_count = 0
    cable_cost = 0
    cable_power = 0
    for length in sorted(self._cables):
      cable_count += self._cables[length][1]
      cable_cost += (self._cables[length][0].cost * self._cables[length][1])
      cable_power += (self._cables[length][0].power * self._cables[length][1])

    # totals and relatives
    total_cost = interface_cost + router_cost + cable_cost
    relative_cost = total_cost / nodes
    total_power = interface_power + router_power + cable_power
    relative_power = total_power / nodes

    # create dict of information
    data = OrderedDict()
    data['nodes'] = '{0:,}'.format(nodes)
    data['interface count'] = '{0:,}'.format(interface_count)
    data['interface cost'] = '${0:,.00f}'.format(interface_cost)
    data['interface power'] = '{0:,.00f} Watts'.format(interface_power)
    data['router count'] = '{0:,}'.format(router_count)
    data['router cost'] = '${0:,.00f}'.format(router_cost)
    data['router power'] = '{0:,.00f} Watts'.format(router_power)
    data['cable count'] = '{0:,}'.format(cable_count)
    data['cable cost'] = '${0:,.00f}'.format(cable_cost)
    data['cable power'] = '{0:,.00f} Watts'.format(cable_power)
    data['total cost'] = '${0:,.00f}'.format(total_cost)
    data['relative cost'] = '${0:,.02f}/node'.format(relative_cost)
    data['total power'] = '{0:,.00f} Watts'.format(total_power)
    data['relative power'] = '{0:,.02f} Watts/node'.format(relative_power)

    # write information
    if filename == '-':
      json.dump(data, sys.stdout, indent=4)
      print('')
    else:
      with open(filename, 'w') as fd:
        json.dump(data, fd, indent=4)

  def cable_bargraph(self, plt, filename, xmax, plot_cost, plot_power):
    """
    Writes a bargraph of cable information
    """

    # extract cable elements
    num_cable_lengths = len(self._cables)
    cable_lengths = sorted(self._cables)
    cable_counts = [self._cables[len][1]
                    for len in sorted(self._cables)]
    cable_costs = [self._cables[len][1] * self._cables[len][0].cost
                   for len in sorted(self._cables)]
    cable_powers = [self._cables[len][1] * self._cables[len][0].power
                    for len in sorted(self._cables)]

    # create empty cable locations
    if xmax is not None:
      if xmax < max(cable_lengths):
        raise ValueError(('bargraph xmax is less than the maximum cable length '
                          'of {}m').format(max(cable_lengths)))
      clen = self._cable_granularity
      idx = 0
      # xmax = max(cable_lengths)
      while clen <= xmax:
        if idx == len(cable_lengths) or clen != cable_lengths[idx]:
          cable_lengths.insert(idx, clen)
          cable_counts.insert(idx, 0)
          cable_costs.insert(idx, 0)
          cable_powers.insert(idx, 0)
        clen += self._cable_granularity
        idx += 1
      num_cable_lengths = len(cable_lengths)

    ind = numpy.arange(num_cable_lengths)
    width = 0.75

    fig_width = max(5, num_cable_lengths * 0.25)
    fig = plt.figure(figsize=(fig_width, 10))

    cable_plot = 1
    if not plot_cost and not plot_power:
      plots = 1
    elif plot_cost and not plot_power:
      plots = 2
      cost_plot = 2
    elif not plot_cost and plot_power:
      plots = 2
      power_plot = 2
    elif plot_cost and plot_power:
      plots = 3
      cost_plot = 2
      power_plot = 3
    ax1 = fig.add_subplot(plots, 1, cable_plot)
    if plot_cost:
      ax2 = fig.add_subplot(plots, 1, cost_plot)
    if plot_power:
      ax3 = fig.add_subplot(plots, 1, power_plot)

    # counts
    ax1.bar(ind, cable_counts, width, color='b')
    ax1.set_ylabel('Count', color='b')
    ax1.tick_params(axis='y', colors='b')

    # costs
    if plot_cost:
      ax2.bar(ind, cable_costs, width, color='g')
      ax2.set_ylabel('Cost ($)', color='g')
      ax2.tick_params(axis='y', colors='g')

    # power
    if plot_power:
      ax3.bar(ind, cable_powers, width, color='r')
      ax3.set_ylabel('Power (W)', color='r')
      ax3.tick_params(axis='y', colors='r')

    # general
    axes = [ax1]
    if plot_cost:
      axes.append(ax2)
    if plot_power:
      axes.append(ax3)

    for ax in axes:
      ax.set_xlabel('Length (m)')
      ax.set_xticks(ind)
      ax.set_xticklabels(['{0:.02f}m'.format(l) for l in cable_lengths],
                         rotation='vertical')
      ax.set_xlim(0 - width, max(ind) + width)
      ax.yaxis.grid(True)
      ax.set_axisbelow(True)

    fig.tight_layout()
    fig.suptitle('Cables', fontsize=20)
    fig.subplots_adjust(top=0.94)
    fig.savefig(filename)

  def interface_csv(self, filename):
    """
    This generates a CSV file containing interface information
    """
    # gather raw data
    interface_radices = sorted(self._interfaces)
    interface_counts = [self._interfaces[rdx][1]
                        for rdx in sorted(self._interfaces)]
    interface_costs = [self._interfaces[rdx][1] * self._interfaces[rdx][0].cost
                       for rdx in sorted(self._interfaces)]
    interface_powers = [self._interfaces[rdx][1] *
                        self._interfaces[rdx][0].power
                        for rdx in sorted(self._interfaces)]

    # create a gridstats object to hold the data
    grid = gridstats.GridStats()
    fields = ['Count', 'Cost ($)', 'Power (W)']
    grid.create('Radix', interface_radices, fields)

    # load all data
    for radix, count, cost, power in zip(
        interface_radices, interface_counts, interface_costs, interface_powers):
      grid.set(radix, 'Count', count)
      grid.set(radix, 'Cost ($)', '{0:.00f}'.format(cost))
      grid.set(radix, 'Power (W)', '{0:.00f}'.format(power))

    # write the file
    grid.write(filename)

  def router_csv(self, filename):
    """
    This generates a CSV file containing router information
    """
    # gather raw data
    router_radices = sorted(self._routers)
    router_counts = [self._routers[rdx][1]
                     for rdx in sorted(self._routers)]
    router_costs = [self._routers[rdx][1] * self._routers[rdx][0].cost
                   for rdx in sorted(self._routers)]
    router_powers = [self._routers[rdx][1] * self._routers[rdx][0].power
                    for rdx in sorted(self._routers)]

    # create a gridstats object to hold the data
    grid = gridstats.GridStats()
    fields = ['Count', 'Cost ($)', 'Power (W)']
    grid.create('Radix', router_radices, fields)

    # load all data
    for radix, count, cost, power in zip(
        router_radices, router_counts, router_costs, router_powers):
      grid.set(radix, 'Count', count)
      grid.set(radix, 'Cost ($)', '{0:.00f}'.format(cost))
      grid.set(radix, 'Power (W)', '{0:.00f}'.format(power))

    # write the file
    grid.write(filename)

  def cable_csv(self, filename):
    """
    This generates a CSV file containing cable information
    """
    # gather raw data
    cable_lengths = sorted(self._cables)
    cable_counts = [self._cables[lng][1]
                    for lng in sorted(self._cables)]
    cable_costs = [self._cables[lng][1] * self._cables[lng][0].cost
                   for lng in sorted(self._cables)]
    cable_powers = [self._cables[lng][1] * self._cables[lng][0].power
                    for lng in sorted(self._cables)]

    # create a gridstats object to hold the data
    grid = gridstats.GridStats()
    fields = ['Count', 'Cost ($)', 'Power (W)']
    grid.create('Length(m)', cable_lengths, fields)

    # load all data
    for length, count, cost, power in zip(
        cable_lengths, cable_counts, cable_costs, cable_powers):
      grid.set(length, 'Count', count)
      grid.set(length, 'Cost ($)', '{0:.00f}'.format(cost))
      grid.set(length, 'Power (W)', '{0:.00f}'.format(power))

    # write the file
    grid.write(filename)

  def _make_interface(self, minimum_radix):
    """
    Makes an interface
    """
    raise NotImplementedError('subclasses MUST implement this')

  def _make_router(self, minimum_radix):
    """
    Makes a router
    """
    raise NotImplementedError('subclasses MUST implement this')

  def _make_cable(self, minimum_length):
    """
    Makes a cable
    """
    raise NotImplementedError('subclasses MUST implement this')

  def _set_router_attributes(self, router, count):
    """
    Sets the attributes of the router
    """
    raise NotImplementedError('subclasses MUST implement this')

  def _set_cable_attributes(self, cable, count):
    """
    Sets the attributes of the cable
    """
    raise NotImplementedError('subclasses MUST implement this')
