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

class Kim08(fabric.Fabric):
  """
  This is from the Kim et al. 2008 Dragonfly paper:
  "Technology-driven, highly-scalable dragonfly topology."
  """

  def __init__(self, **kwargs):
    super(Kim08, self).__init__(**kwargs)

    # parse kwargs
    for key in kwargs:
      if key in super(Kim08, self).using_options():
        pass
      else:
        assert False, 'unknown option key: {}'.format(key)

  def _make_interface(self, minimum_radix):
    return fabric.Interface(minimum_radix)

  def _make_router(self, minimum_radix):
    return fabric.Router(minimum_radix)

  def _make_cable(self, minimum_length):
    actual_length = minimum_length
    if not self.partial_cables:
      real_lengths = [0.5, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25, 30, 50, 75, 100,
                      150, 200]
      found = False
      for real_length in real_lengths:
        if real_length >= minimum_length:
          actual_length = real_length
          found = True
          break
      assert found, 'no cable available for length: {}'.format(actual_length)
    return fabric.Cable(minimum_length, actual_length)

  def _set_interface_attributes(self, router, count):
    # Note: the paper didn't have any interface cost/power information
    router.tech = 'mythical'
    router.cost = 400
    router.power = 50

  def _set_router_attributes(self, router, count):
    # Note: the paper didn't have any router cost/power information
    router.tech = 'mythical'
    router.cost = 1000
    router.power = 250

  def _set_cable_attributes(self, cable, count):
    ec = (1.4 * cable.actual_length) + 2.16
    oc = (0.364 * cable.actual_length) + 9.7103
    if ec <= oc:
      cable.tech = 'acc'
      cable.cost = ec
      cable.power = 0.5*2
    else:
      cable.tech = 'aoc'
      cable.cost = oc
      cable.power = 1.5*2
