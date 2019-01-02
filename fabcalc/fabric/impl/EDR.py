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

class EDR(fabric.Fabric):
  """
  This is the public information about Mellanox EDR
  """

  def __init__(self, **kwargs):
    super(EDR, self).__init__(**kwargs)

    # parse kwargs
    for key in kwargs:
      if key in super(EDR, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

    # data from:
    # https://store.mellanox.com/search.php?search_query=edr+cable&x=0&y=0
    self._options = [
      (0.5,   'pcc', 90,    0),
      (1.0,   'pcc', 99,    0),
      (1.5,   'pcc', 105,   0),
      (2.0,   'pcc', 115,   0),
      (3.0,   'pcc', 135,   0),
      (5.0,   'aoc', 590,   3.5*2),
      (10.0,  'aoc', 610,   3.5*2),
      (15.0,  'aoc', 645,   3.5*2),
      (20.0,  'aoc', 680,   3.5*2),
      (30.0,  'aoc', 770,   3.5*2),
      (50.0,  'aoc', 1100,  3.5*2),
      (100.0, 'aoc', 1865,  3.5*2),
      (200.0, 'aoc', 4000,  3.5*2)] # made up

  def _make_interface(self, minimum_radix):
    assert minimum_radix <= 1, 'EDR only supports 1 port interfaces'
    return fabric.Interface(1)

  def _make_router(self, minimum_radix):
    if minimum_radix <= 36:
      return fabric.Router(36)
    elif minimum_radix <= 648:
      return fabric.Router(36)
    else:
      assert minimum_radix <= 648, 'EDR only supports 36 and 648 port routers'

  def _make_cable(self, minimum_length):
    for clen, ctype, ccost, cpower in self._options:
      if clen >= minimum_length:
        if not self.partial_cables:
          return fabric.Cable(minimum_length, clen)
        else:
          return fabric.Cable(minimum_length, minimum_length)
    assert False, 'no cable available for length: {}'.format(minimum_length)

  def _set_interface_attributes(self, interface, count):
    interface.tech = 'IB'
    interface.cost = 100
    interface.power = 50

  def _set_router_attributes(self, router, count):
    if router.radix == 36:
      router.tech = 'IB'
      router.cost = 10000
      router.power = 250
    elif router.radix == 648:
      router.tech = 'IB'
      router.cost = 250000
      router.power = (18 + 36) * 250
    else:
      assert False, 'Programmer error!'

  def _set_cable_attributes(self, cable, count):
    for clen, ctype, ccost, cpower in self._options:
      if clen >= cable.actual_length:
        cable.tech = ctype
        cable.cost = ccost
        cable.power = cpower
        return
    assert False
