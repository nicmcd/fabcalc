#!/usr/bin/env python3

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

import argparse
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import fabric
import layout
import topology
import utils

def main(args):
  # convert the argparse options to kwargs style dicts
  topo_opts = dict([] if not args.topts else args.topts)
  layout_opts = dict([] if not args.lopts else args.lopts)
  fabric_opts = dict([] if not args.fopts else args.fopts)
  if args.verbose:
    print('Topology Options : {}'.format(topo_opts))
    print('Layout Options   : {}'.format(layout_opts))
    print('Fabric Options   : {}'.format(fabric_opts))

  # construct the models
  topo_model = topology.factory(args.topology, **topo_opts)
  nodes, routers = topo_model.structure()
  layout_model = layout.factory(args.layout, nodes, routers, **layout_opts)
  fabric_model = fabric.factory(args.fabric, **fabric_opts)

  # generate routers and cables
  for radix, count in topo_model.interfaces():
    fabric_model.add_interface(radix, count)
  for radix, count in topo_model.routers():
    fabric_model.add_router(radix, count)
  for node, router, count in topo_model.external_cables():
    length = layout_model.external_cable(node, router, count)
    topo_model.notify_length(length, count)
    fabric_model.add_cable(length, count)
  for router1, router2, count in topo_model.internal_cables():
    length = layout_model.internal_cable(router1, router2, count)
    topo_model.notify_length(length, count)
    fabric_model.add_cable(length, count)

  # set router and cable attributes
  fabric_model.set_attributes()

  # generate outputs
  if args.summary is None:
    args.summary = '-'
  fabric_model.summary(nodes, args.summary)
  if args.bargraph is not None:
    fabric_model.cable_bargraph(plt, args.bargraph, args.bargraph_xmax,
                                args.bargraph_cost, args.bargraph_power)
  if args.interface_csv is not None:
    fabric_model.interface_csv(args.interface_csv)
  if args.router_csv is not None:
    fabric_model.router_csv(args.router_csv)
  if args.cable_csv is not None:
    fabric_model.cable_csv(args.cable_csv)
  if args.tray_csv is not None:
    layout_model.cable_tray_csv(args.tray_csv)
  if args.topo_info is not None:
    topo_model.info_file(args.topo_info)

if __name__ == '__main__':
  # ensures key/value pair format and converts to tuple
  def check_option(pair):
    if (len(pair.split('=')) != 2 or
        len(pair.split('=')[0]) == '' or
        len(pair.split('=')[1]) == ''):
      raise argparse.ArgumentTypeError('invalid key/pair: {}'.format(pair))
    else:
      return tuple(pair.split('='))

  ap = argparse.ArgumentParser()
  ap.add_argument('topology', type=str,
                  help='the topology model to use')
  ap.add_argument('--topts', nargs='*', type=check_option,
                  help='<key>=<value> pair to configure the topology model')
  ap.add_argument('fabric', type=str,
                  help='the fabric model to use')
  ap.add_argument('--fopts', nargs='*', type=check_option,
                  help='<key>=<value> pair to configure the fabric model')
  ap.add_argument('layout', type=str,
                  help='the layout model to use')
  ap.add_argument('--lopts', nargs='*', type=check_option,
                  help='<key>=<value> pair to configure the layout model')
  ap.add_argument('--summary', type=str,
                  help='cost and power summary file')
  ap.add_argument('--bargraph', type=str,
                  help='bargraph of cable information')
  ap.add_argument('--bargraph_xmax', type=float,
                  help='maximum value of x-axis on bargraph')
  ap.add_argument('--bargraph_cost', type=utils.str_to_bool, default=True,
                  help='plot cost in bargraph')
  ap.add_argument('--bargraph_power', type=utils.str_to_bool, default=True,
                  help='plot power in bargraph')
  ap.add_argument('--interface_csv', type=str,
                  help='CSV file of interface information')
  ap.add_argument('--router_csv', type=str,
                  help='CSV file of router information')
  ap.add_argument('--cable_csv', type=str,
                  help='CSV file of cable information')
  ap.add_argument('--tray_csv', type=str,
                  help='CSV file of cable tray usage')
  ap.add_argument('--topo_info', type=str,
                  help='Topology information file')
  ap.add_argument('-v', '--verbose', action='store_true',
                  help='print extra information')

  args = ap.parse_args()
  main(args)
