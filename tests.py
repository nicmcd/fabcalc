#!/usr/bin/env python3

import os
import shutil
import subprocess
import taskrun

def test(topology, fabric, layout):
  name = '_'.join([topology[0], fabric[0], layout[0]])
  outdir = 'outputs/' + name
  os.mkdir(outdir)
  cmd = (('./main.py {1} {2} {3} '
          '--topts {4} '
          '--fopts {5} '
          '--lopts {6} '
          '--summary {0}/summary.json '
          '--bargraph {0}/bargraph.png '
          #'--bargraph_xmax 60 '
          '--router_csv {0}/routers.csv '
          '--cable_csv {0}/cables.csv '
          '--tray_csv {0}/trays.csv '
          '--topo_info {0}/topo.txt ')
         .format(outdir, topology[1], fabric[1], layout[1],
                 topology[2], fabric[2], layout[2]))
  print(name)
  subprocess.run(cmd, shell=True)

def main():
  # topologies
  hx2d_1k = ('hx2d-1k', 'Hyperx',
             'widths=4,8 weights=4,1 concentration=8 chassis=4')
  hx3d_16k = ('hx3d_16k', 'Hyperx',
              'widths=4,16,16 weights=4,1,1 concentration=16 chassis=4')
  dfly_1k = ('dfly-1k', 'Dragonfly',
             ('global_width=32 global_weight=1 local_width=8 '
              'local_weight=1 concentration=4 chassis=4'))
  dfly_16k = ('dfly-16k', 'Dragonfly',
              ('global_width=128 global_weight=1 local_width=16 '
               'local_weight=1 concentration=8 chassis=4'))
  ftree_1k = ('ftree_1k', 'FatTree',
              ('leaves=128 down_ports=8 up_ports=8 leaves_per_rack=4 '
               'directors_per_rack=1 director_radix=128 director_rack_inset=6'))
  ftree_16k = ('ftree_16k', 'FatTree',
               ('leaves=1024 down_ports=16 up_ports=16 leaves_per_rack=4 '
                'directors_per_rack=1 director_radix=1024 '
                'director_rack_inset=6'))

  # fabrics
  kim_dally = ('kim-dally', 'KimDally', '')
  edr = ('edr', 'EDR', '')

  # layouts
  standard = ('standard', 'Standard', '')


  # set up full directory
  if os.path.isdir('outputs'):
    shutil.rmtree('outputs')
  os.mkdir('outputs')


  test(hx2d_1k, kim_dally, standard)
  test(hx3d_16k, kim_dally, standard)
  test(dfly_1k, kim_dally, standard)
  test(dfly_16k, kim_dally, standard)
  test(ftree_1k, kim_dally, standard)
  test(ftree_16k, kim_dally, standard)

  test(hx2d_1k, edr, standard)
  test(dfly_1k, edr, standard)
  test(ftree_1k, edr, standard)

if __name__ == '__main__':
  main()
