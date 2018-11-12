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

class Topology(object):
  """
  This is an abstract class that represents a fabric technology
  The 'topology' defines structure and makes connections
  """

  @staticmethod
  def using_options():
    """
    Tells the base class which option keys it uses
    """
    return []

  def __init__(self, **kwargs):
    """
    Constructs a Topology object
    """
    pass

  def structure(self):
    """
    This returns the structure of the system in terms of:
    nodes       : total number of nodes
    chassis     : number of chassis per rack
    total_racks : total number of racks

    Returns:
      tuple (int, int, int, int) : nodes, chassis, racks, rows
    """
    raise NotImplementedError('subclasses must override this')

  def routers(self):
    """
    This is a generator that generates (radix, count) tuples
    'radix' and 'count' are of type int
    """
    raise NotImplementedError('subclasses must override this')

  def cables(self):
    """
    This is a generator that generates (source, destination, count) tuples
    'source' and 'destination' are of type layout.Coordinate
    'count' is of type int
    """
    raise NotImplementedError('subclasses must override this')

  def notify_length(self, length, count):
    """
    This notifies the topology module of the length of cables generated. This
    can be used by the topology module to generate topology specific cable
    length statistics
    length  : length of cable
    count   : count of cables
    """
    pass  # this is only used when desired by the topology module

  def info_file(self, filename):
    """
    This writes topology specific information to a file
    filename : the file to be written
    """
    raise NotImplementedError('subclasses must override this')
