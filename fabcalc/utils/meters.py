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

def meters(length):
  if isinstance(length, float) or isinstance(length, int):
    return length
  elif length.endswith('m'):
    return float(length[:-1].strip())
  elif length.endswith('cm'):
    return float(length[:-2].strip()) * 100
  elif length.endswith('mm'):
    return float(length[:-2].strip()) * 1000
  elif (length.endswith('RU') or length.endswith('ru')):
    return rack_units_to_meters(float(length[:-2].strip()))
  elif (length.endswith('U') or length.endswith('u')):
    return rack_units_to_meters(float(length[:-1].strip()))
  elif length.endswith('in'):
    return inches_to_meters(float(length[:-2].strip()))
  elif length.endswith('ft'):
    return inches_to_meters(12 * float(length[:-2].strip()))
  else:
    assert False, 'invalid length: ' + length

def rack_units_to_meters(rack_units):
  return rack_units * 0.04445

def inches_to_meters(inches):
  return inches * 0.0254
