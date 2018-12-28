#!/usr/bin/env python3

import argparse
import copy
import glob
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
import os
import shutil
import ssplot
import subprocess
import taskrun

class Tester(object):
  def __init__(self):
    cpus = os.cpu_count()
    mem = taskrun.MemoryResource.current_available_memory_gib();
    rm = taskrun.ResourceManager(taskrun.CounterResource('cpus', 1, cpus),
                                 taskrun.MemoryResource('mem', 3, mem))
    cob = taskrun.FileCleanupObserver()
    vob = taskrun.VerboseObserver(description=False, summary=True)
    fm = taskrun.FailureMode.ACTIVE_CONTINUE
    self._tm = taskrun.TaskManager(resource_manager=rm,
                                   observers=[cob, vob],
                                   failure_mode=fm)

  def add(self, topology, fabric, layout):
    name = '_'.join([topology[0], fabric[0], layout[0]])
    outdir = 'tests_output/' + name
    if not os.path.isdir(outdir):
      os.mkdir(outdir)
    cmd = (('./main.py -v {1} {2} {3} '
            '--topts {4} '
            '--fopts {5} '
            '--lopts {6} '
            '--summary {0}/summary.json '
            '--bargraph {0}/bargraph.png '
            #'--bargraph_xmax 60 '
            '--interface_csv {0}/interfaces.csv '
            '--router_csv {0}/routers.csv '
            '--cable_csv {0}/cables.csv '
            '--tray_csv {0}/trays.csv '
            '--topo_info {0}/topo.txt ')
           .format(outdir, topology[1], fabric[1], layout[1],
                   topology[2], fabric[2], layout[2]))
    task = taskrun.ProcessTask(self._tm, name, cmd)
    task.stdout_file = '{0}/log.txt'.format(outdir)
    task.stderr_file = 'stdout'
    task.add_condition(taskrun.FileModificationCondition(
      [], ['{0}/summary.json'.format(outdir),
           '{0}/bargraph.png'.format(outdir),
           '{0}/interfaces.csv'.format(outdir),
           '{0}/routers.csv'.format(outdir),
           '{0}/cables.csv'.format(outdir),
           '{0}/trays.csv'.format(outdir),
           '{0}/topo.txt'.format(outdir)]))

  def run(self):
    return self._tm.run_tasks()


def main(args):
  # set up full directory
  if args.clean:
    if os.path.isdir('tests_output'):
      shutil.rmtree('tests_output')
  if not os.path.isdir('tests_output'):
    os.mkdir('tests_output')

  # fabrics
  fabrics = [
    ('kim08', 'Kim08', ''),
    ('ib-edr', 'EDR', ''),
    ('ib-hdr', 'HDR', ''),
    ('ib-ndr', 'NDR', ''),
    ('eth40', 'Eth40', ''),
    ('eth100', 'Eth100', ''),
    ('poc-2f', 'PassiveOptical', ''),
    ('poc-12f', 'PassiveOptical', 'fibers=12'),
    ('poc-24f', 'PassiveOptical', 'fibers=24')
  ]

  # layouts
  layouts = [
    ('rackandstack', 'RackAndStack',
     ('rack_height=52U rack_width=24in rack_depth=48in cable_tray_gap=6in '
      'router_bays=16 router_chassis=1 router_chassis_height=4U '
      'node_bays=16 node_chassis=16 node_chassis_height=3U '
      'max_racks_per_row=16')),
    ('integrated', 'Integrated',
     ('rack_height=48U rack_width=24in rack_depth=48in cable_tray_gap=6in '
      'chassis=16 chassis_height=3U '
      'router_bays=1 node_bays=16 '
      'max_racks_per_row=16'))
  ]

  # topologies
  hx = [
    ('hx-4k', 'Hyperx',
     'widths=16,16 weights=1,1 concentration=16'),
    ('hx-8k', 'Hyperx',
     'widths=16,16,2 weights=1,1,8 concentration=16'),
    ('hx-16k', 'Hyperx',
     'widths=16,16,4 weights=1,1,4 concentration=16'),
    ('hx-32k', 'Hyperx',
     'widths=16,16,8 weights=1,1,2 concentration=16'),
    ('hx-64k', 'Hyperx',
     'widths=16,16,16 weights=1,1,1 concentration=16')
  ]
  df_sg = [
    ('df-sg-4k', 'Dragonfly',
     ('global_width=16 global_weight=16 local_width=16 local_weight=2 '
      'concentration=16')),
    ('df-sg-8k', 'Dragonfly',
     ('global_width=32 global_weight=8 local_width=16 local_weight=2 '
      'concentration=16')),
    ('df-sg-16k', 'Dragonfly',
     ('global_width=64 global_weight=4 local_width=16 local_weight=2 '
      'concentration=16')),
    ('df-sg-32k', 'Dragonfly',
     ('global_width=128 global_weight=2 local_width=16 local_weight=2 '
      'concentration=16')),
    ('df-sg-64k', 'Dragonfly',
     ('global_width=256 global_weight=1 local_width=16 local_weight=2 '
      'concentration=16'))
  ]
  df_lg = [
    ('df-lg-4k', 'Dragonfly',
     ('global_width=8 global_weight=64 local_width=32 local_weight=1 '
      'concentration=16')),
    ('df-lg-8k', 'Dragonfly',
     ('global_width=16 global_weight=32 local_width=32 local_weight=1 '
      'concentration=16')),
    ('df-lg-16k', 'Dragonfly',
     ('global_width=32 global_weight=16 local_width=32 local_weight=1 '
      'concentration=16')),
    ('df-lg-32k', 'Dragonfly',
     ('global_width=64 global_weight=8 local_width=32 local_weight=1 '
      'concentration=16')),
    ('df-lg-64k', 'Dragonfly',
     ('global_width=128 global_weight=4 local_width=32 local_weight=1 '
      'concentration=16'))
  ]
  topos = hx + df_sg# + df_lg

  # permute
  tester = Tester()
  for layout in layouts:
    for fabric in fabrics:
      for topo in topos:
        tester.add(topo, fabric, layout)
  ret = tester.run()
  return ret

if __name__ == '__main__':
  ap = argparse.ArgumentParser()
  ap.add_argument('-c', '--clean', action='store_true',
                  help='clean output directory')
  args = ap.parse_args()
  main(args)
