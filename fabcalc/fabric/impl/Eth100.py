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

class Eth100(fabric.Fabric):
  """
  This is the public information about 100 GbE using Tomahawk II
  """

  def __init__(self, **kwargs):
    super(Eth100, self).__init__(**kwargs)

    # parse kwargs
    for key in kwargs:
      if key in super(Eth100, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # electrical
    # http://www.fs.com/products/47096.html (Dell)
    # optical
    # http://www.fs.com/products/65892.html
    self._options = [
      (1.0,   'pcc', 67,   0),
      (2.0,   'pcc', 90,   0),
      (3.0,   'pcc', 110,  0),
      (5.0,   'pcc', 200,  0),
      (7.0,   'aoc', 500,  3.5*2),
      (10.0,  'aoc', 510,  3.5*2),
      (15.0,  'aoc', 520,  3.5*2),
      (20.0,  'aoc', 540,  3.5*2),
      (25.0,  'aoc', 550,  3.5*2),
      (30.0,  'aoc', 570,  3.5*2),
      (50.0,  'aoc', 590,  3.5*2),  # a guess
      (75.0,  'aoc', 640,  3.5*2),  # a guess
      (100.0, 'aoc', 750,  3.5*2),  # a guess
      (200.0, 'aoc', 2000,  3.5*2)]  # a guess

  def _make_interface(self, minimum_radix):
    assert minimum_radix <= 1, 'Eth100 only supports 1 port interfaces'
    return fabric.Interface(1)

  def _make_router(self, minimum_radix):
    assert minimum_radix <= 64, 'Eth100 only supports 64 port routers'
    return fabric.Router(64)

  def _make_cable(self, minimum_length):
    for clen, ctype, ccost, cpower in self._options:
      if clen >= minimum_length:
        if not self.partial_cables:
          return fabric.Cable(minimum_length, clen)
        else:
          return fabric.Cable(minimum_length, minimum_length)
    assert False, 'no cable available for length: {}'.format(minimum_length)

  def _set_interface_attributes(self, interface, count):
    interface.tech = '100GbE'
    interface.cost = 500
    interface.power = 50

  def _set_router_attributes(self, router, count):
    router.tech = '100GbE'
    router.cost = 5000
    router.power = 300

  def _set_cable_attributes(self, cable, count):
    for clen, ctype, ccost, cpower in self._options:
      if clen >= cable.actual_length:
        cable.tech = ctype
        cable.cost = ccost
        cable.power = cpower
        return
    assert False
