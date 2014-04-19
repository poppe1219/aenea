import jsonrpclib
import xmlrpclib
import httplib

import config


# Override of the xmlrpclib.Transport class to change the connection timeout.
class Transport(jsonrpclib.jsonrpc.TransportMixIn, xmlrpclib.Transport):
    def make_connection(self, host):
        #return an existing connection if possible.  This allows
        #HTTP/1.1 keep-alive.
        if self._connection and host == self._connection[0]:
            return self._connection[1]

        # create a HTTP connection object from a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        #store the host argument along with the connection object
        self._connection = host, httplib.HTTPConnection(chost, timeout=1)
        return self._connection[1]


class Proxy(object):
  def __init__(self, host, port):
    self.server = jsonrpclib.Server("http://%s:%i" % (host, port),
        transport=Transport())  # Use the custom Transport class.
    self._server = jsonrpclib.Server("http://%s:%i" % (host, 8888),
        transport=Transport())  # Use the custom Transport class.

  def toggle_server(self):
      temp = self.server
      self.server = self._server
      self._server = temp

  def execute_batch(self, batch):
    if config.USE_MULTIPLE_ACTIONS:
      self.server.multiple_actions(batch)
    else:
      for (command, args, kwargs) in batch:
        getattr(self.server, command)(*args, **kwargs)

class BatchProxy(object):
  def __init__(self):
    self._commands = []

  def __getattr__(self, key):
    def call(*a, **kw):
      if not key.startswith("_"):
        self._commands.append((key, a, kw))
    return call
