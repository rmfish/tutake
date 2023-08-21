import logging
import os
import pickle
import platform
import sys
import threading
import traceback
import zlib
from typing import Callable, List

import pandas as pd
import zmq
from tornado import ioloop
from zmq.eventloop import zmqstream

from tutake import Tutake
from tutake.utils.config import TUTAKE_SERVER_PORT_KEY

LOG = logging.getLogger("tutake.remote")


class TutakeZMQProcess(threading.Thread):

    def __init__(self, *args, **kwargs):
        """The :class: ``sqlite_rx.server.SQLiteServer`` is intended to run as an isolated process.
        This class represents some of the abstractions for isolated server process

        """
        super(TutakeZMQProcess, self).__init__(*args, **kwargs)
        self.context = None
        self.loop = None
        self.socket = None
        self.auth = None

    def setup(self):
        LOG.info("Python Platform %s", platform.python_implementation())
        LOG.info("libzmq version %s", zmq.zmq_version())
        LOG.info("pyzmq version %s", zmq.__version__)
        self.context = zmq.Context()
        self.loop = ioloop.IOLoop()

    def stream(self,
               sock_type,
               address: str,
               callback: Callable = None):
        self.socket = self.context.socket(sock_type)
        self.socket.bind(address)

        stream = zmqstream.ZMQStream(self.socket, self.loop)
        if callback:
            stream.on_recv(callback)
        return stream


class TutakeServer(TutakeZMQProcess):

    def __init__(self,
                 tutake: Tutake,
                 *args, **kwargs):
        super(TutakeServer, self).__init__(*args, *kwargs)
        self._bind_address = "tcp://0.0.0.0:{}".format(tutake.config.get_config(TUTAKE_SERVER_PORT_KEY, 5000))
        self.rep_stream = None
        self.tutake = tutake

    def setup(self):
        super().setup()
        # Depending on the initialization parameters either get a plain stream or secure stream.
        self.rep_stream = self.stream(zmq.REP, self._bind_address)
        # Register the callback.
        self.rep_stream.on_recv(QueryStreamHandler(self.rep_stream, self.tutake))

    def handle_signal(self, signum, frame):
        LOG.info("TutakeServer %s PID %s received %r", self, self.pid, signum)
        LOG.info("TutakeServer Shutting down")

        self.rep_stream.close()
        self.socket.close()
        self.loop.stop()
        os._exit(os.EX_OK)

    def run(self):
        # signal(SIGTERM, self.handle_signal)
        # signal(SIGINT, self.handle_signal)

        self.setup()
        LOG.info("TutakeServer (Tornado) i/o loop started..")
        LOG.info("Ready to accept client connections on %s", self._bind_address)
        self.loop.start()


class QueryStreamHandler:

    def __init__(self, rep_stream, tutake: Tutake):
        self._rep_stream = rep_stream
        self.tutake = tutake

    @staticmethod
    def capture_exception():
        exc_type, exc_value, exc_tb = sys.exc_info()
        exc_type_string = "%s.%s" % (exc_type.__module__, exc_type.__name__)
        error = {"type": exc_type_string, "message": traceback.format_exception_only(exc_type, exc_value)[-1].strip()}
        return error

    def __call__(self, message: List):
        try:
            message = message[-1]
            message = pickle.loads(zlib.decompress(message))
            self._rep_stream.send(self.execute(message))
        except Exception:
            LOG.exception("exception while preparing response. %s", self.capture_exception())

    def execute(self, request: dict, *args, **kwargs):
        namespace = request['namespace']
        api_name = request['api_name']
        fields = request['fields']
        kwargs = request['kwargs']
        result = pd.DataFrame()
        try:
            if namespace == "tushare":
                result = self.tutake.tushare_api().query(api_name, fields, **kwargs)
            elif namespace == "xueqiu":
                result = self.tutake.xueqiu_api().query(api_name, fields, **kwargs)
        except Exception as e:
            LOG.exception("Exception while executing query %s %s", request['query'], e)
        return zlib.compress(pickle.dumps(result))


if __name__ == '__main__':
    server = TutakeServer(Tutake("../../config.yml"))
    server.start()
    server.join()
