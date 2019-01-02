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

import fabric
import utils

class PassiveOptical(fabric.Fabric):
  """
  This is a passive optical cable system with generic ASIC costs
  """

  def __init__(self, **kwargs):
    super(PassiveOptical, self).__init__(**kwargs)

    self._planes = 1
    self._interface_radix = 4
    self._interface_asic_cost = 1500
    self._interface_asic_power = 375
    self._router_radix = 64
    self._router_asic_cost = 1500
    self._router_asic_power = 375
    self._fiber_type = 'om4'
    self._fibers = 2
    self._optics_cost = 0

    # parse kwargs
    for key in kwargs:
      if key == 'planes':
        self._planes = int(kwargs[key])
      elif key == 'interface_radix':
        self._interface_radix = utils.str_to_bool(kwargs[key])
      elif key == 'interface_asic_cost':
        self._interface_asic_cost = float(kwargs[key])
      elif key == 'interface_asic_power':
        self._interface_asic_power = float(kwargs[key])
      elif key == 'router_radix':
        self._router_radix = utils.str_to_bool(kwargs[key])
      elif key == 'router_asic_cost':
        self._router_asic_cost = float(kwargs[key])
      elif key == 'router_asic_power':
        self._router_asic_power = float(kwargs[key])
      elif key == 'fiber_type':
        self._fiber_type = kwargs[key]
        assert self._fiber_type in ['om3', 'om4']
      elif key == 'fibers':
        self._fibers = int(kwargs[key])
        assert self._fibers in [2, 12, 24]
      elif key == 'max_cots_len':
        self._max_cots_len = utils.meters(kwargs[key])
      elif key == 'non_cots_scalar':
        self._non_cots_scalar = float(kwargs[key])
      elif key == 'optics_cost':
        self._optics_cost = float(kwargs[key])
      elif key in super(PassiveOptical, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    self._options = {
      'om3': {
        2: [
          (0.5,   'poc', 10,   0),
          (1.0,   'poc', 11,   0),
          (3.0,   'poc', 12,   0),
          (5.0,   'poc', 13,   0),
          (10.0,  'poc', 16,   0),
          (15.0,  'poc', 20,   0),
          (20.0,  'poc', 23,   0),
          (30.0,  'poc', 29,   0),
          (50.0,  'poc', 46,   0),
          (100.0, 'poc', 75,   0)],
        12: [
          (0.5,   'poc', 57,   0),
          (1.0,   'poc', 59,   0),
          (3.0,   'poc', 68,   0),
          (5.0,   'poc', 77,   0),
          (10.0,  'poc', 100,  0),
          (15.0,  'poc', 122,  0),
          (20.0,  'poc', 144,  0),
          (30.0,  'poc', 189,  0),
          (50.0,  'poc', 278,  0),
          (100.0, 'poc', 502,  0)],
        24: [
          (0.5,   'poc', 70,   0),
          (1.0,   'poc', 73,   0),
          (3.0,   'poc', 87,   0),
          (5.0,   'poc', 101,  0),
          (10.0,  'poc', 136,  0),
          (15.0,  'poc', 171,  0),
          (20.0,  'poc', 206,  0),
          (30.0,  'poc', 276,  0),
          (50.0,  'poc', 416,  0),
          (100.0, 'poc', 766,  0)]
      },
      'om4': {
        2: [
          (0.5,   'poc', 10,   0),
          (1.0,   'poc', 11,   0),
          (3.0,   'poc', 12,   0),
          (5.0,   'poc', 14,   0),
          (10.0,  'poc', 17,   0),
          (15.0,  'poc', 21,   0),
          (20.0,  'poc', 25,   0),
          (30.0,  'poc', 32,   0),
          (50.0,  'poc', 46,   0),
          (100.0, 'poc', 83,   0),
          (200.0, 'poc', 200,  0)],  # made up
        12: [
          (0.5,   'poc', 58,   0),
          (1.0,   'poc', 60,   0),
          (3.0,   'poc', 72,   0),
          (5.0,   'poc', 83,   0),
          (10.0,  'poc', 111,  0),
          (15.0,  'poc', 139,  0),
          (20.0,  'poc', 167,  0),
          (30.0,  'poc', 223,  0),
          (50.0,  'poc', 334,  0),
          (100.0, 'poc', 614,  0),
          (200.0, 'poc', 1000, 0)],  # made up
        24: [
          (0.5,   'poc', 72,   0),
          (1.0,   'poc', 75,   0),
          (3.0,   'poc', 86,   0),
          (5.0,   'poc', 98,   0),
          (10.0,  'poc', 126,  0),
          (15.0,  'poc', 153,  0),
          (20.0,  'poc', 181,  0),
          (30.0,  'poc', 237,  0),
          (50.0,  'poc', 349,  0),
          (100.0, 'poc', 629,  0),
          (200.0, 'poc', 1015, 0)]  # made up
      }
    }

    # validate settings
    assert self._fibers >= (self._planes * 2)

    # OZS info
    self._cost_per_router = self._planes * self._router_asic_cost
    self._power_per_router = self._planes * self._router_asic_cost

    # save only the options selected
    self._options = self._options[self._fiber_type][self._fibers]

  def _make_interface(self, minimum_radix):
    if minimum_radix <= self._interface_radix:
      return fabric.Interface(self._interface_radix)
    else:
      assert False, 'invalid number of interface ports'

  def _make_router(self, minimum_radix):
    if minimum_radix <= self._router_radix:
      return fabric.Router(self._router_radix)
    else:
      assert False, 'invalid number of router ports'

  def _make_cable(self, minimum_length):
    for clen, ctype, ccost, cpower in self._options:
      if clen >= minimum_length:
        if not self.partial_cables:
          return fabric.Cable(minimum_length, clen)
        else:
          return fabric.Cable(minimum_length, minimum_length)
    assert False, 'no cable available for length: {}'.format(minimum_length)

  def _set_interface_attributes(self, interface, count):
    interface.tech = 'Generic'
    interface.cost = self._interface_asic_cost
    interface.power = self._interface_asic_power

  def _set_router_attributes(self, router, count):
    router.tech = 'Generic'
    router.cost = self._cost_per_router
    router.power = self._power_per_router

  def _set_cable_attributes(self, cable, count):
    for clen, ctype, ccost, cpower in self._options:
      if clen >= cable.actual_length:
        cable.tech = ctype
        cable.cost = ccost
        cable.cost += (2 * self._optics_cost)
        cable.power = cpower
        return
    assert False
