import logging.config
import os
import platform
import socket
import sqlite3
import sys
import traceback
import zlib
from signal import SIGTERM, SIGINT, signal
from typing import List, Union, Callable

import billiard as multiprocessing
import msgpack
import zmq
from tornado import ioloop, version
from zmq.auth.ioloop import IOLoopAuthenticator
from zmq.eventloop import zmqstream

from tutake.remote.auth import Authorizer, KeyMonkey
from tutake.remote.exception import SQLiteRxZAPSetupError

PARENT_DIR = os.path.dirname(__file__)

LOG = logging.getLogger(__name__)

__all__ = ['SQLiteServer']


class SQLiteZMQProcess(multiprocessing.Process):

    def __init__(self, *args, **kwargs):
        """The :class: ``sqlite_rx.server.SQLiteServer`` is intended to run as an isolated process.
        This class represents some of the abstractions for isolated server process

        """
        super(SQLiteZMQProcess, self).__init__(*args, **kwargs)
        self.context = None
        self.loop = None
        self.socket = None
        self.auth = None

    def setup(self):
        LOG.info("Python Platform %s", platform.python_implementation())
        LOG.info("libzmq version %s", zmq.zmq_version())
        LOG.info("pyzmq version %s", zmq.__version__)
        LOG.info("tornado version %s", version)
        self.context = zmq.Context()
        self.loop = ioloop.IOLoop()

    def stream(self,
               sock_type,
               address: str,
               callback: Callable = None,
               use_encryption: bool = False,
               server_curve_id: str = None,
               curve_dir: str = None,
               use_zap: bool = False):
        """

        Method used to setup a ZMQ stream which will be bound to a ZMQ.REP socket.
        On this REP stream we register a callback to execute client queries as they arrive.
        The stream is used in conjunction with `tornado` eventloop

        Args:
            sock_type: ZMQ Socket type. For e.g. zmq.REP
            address: Address to bind to
            callback: A callback to invoke as messages arrive on the ZMQ stream
            use_encryption: True if you want CurveZMQ encryption to be enabled
            server_curve_id: Server curve id. Defaults to "id_server_{}_curve".format(socket.gethostname())
            curve_dir: Curve key files directory. Defaults to `~/.curve`
            use_zap: True if you want ZAP authentication to be enabled.

        Raises:
            sqlite_rx.exception.SQLiteRxZAPSetupError: If ZAP is enabled without CurveZMQ
        """

        self.socket = self.context.socket(sock_type)

        if use_encryption or use_zap:

            server_curve_id = server_curve_id if server_curve_id else "id_server_{}_curve".format(socket.gethostname())
            keymonkey = KeyMonkey(key_id=server_curve_id, destination_dir=curve_dir)

            if use_encryption:
                LOG.info("Setting up encryption using CurveCP")
                self.socket = keymonkey.setup_secure_server(self.socket, address)

            if use_zap:
                if not use_encryption:
                    raise SQLiteRxZAPSetupError("ZAP requires CurveZMQ(use_encryption = True) to be enabled. Exiting")

                self.auth = IOLoopAuthenticator(self.context)
                LOG.info("ZAP enabled. \n Authorizing clients in %s.", keymonkey.authorized_clients_dir)
                self.auth.configure_curve(domain="*", location=keymonkey.authorized_clients_dir)
                self.auth.start()

        self.socket.bind(address)

        stream = zmqstream.ZMQStream(self.socket, self.loop)
        if callback:
            stream.on_recv(callback)
        return stream


class SQLiteServer(SQLiteZMQProcess):

    def __init__(self,
                 bind_address: str,
                 database: Union[bytes, str],
                 auth_config: dict = None,
                 curve_dir: str = None,
                 server_curve_id: str = None,
                 use_encryption: bool = False,
                 use_zap_auth: bool = False,
                 *args, **kwargs):
        """
        SQLiteServer runs as an isolated python process.

        Args:
            bind_address : The address and port on which the server will listen for client requests.
            database: A path like object or the string ":memory:" for in-memory database.
            context: The ZMQ context
            auth_config : A dictionary describing what actions are authorized, denied or ignored.
            use_encryption : True means use `CurveZMQ` encryption. False means don't
            use_zap_auth : True means use `ZAP` authentication. False means don't

        """
        super(SQLiteServer, self).__init__(*args, *kwargs)
        self._bind_address = bind_address
        self._database = database
        self._auth_config = auth_config
        self._encrypt = use_encryption
        self._zap_auth = use_zap_auth
        self.server_curve_id = server_curve_id
        self.curve_dir = curve_dir
        self.rep_stream = None

    def setup(self):
        """
        Start a zmq.REP socket stream and register a callback :class: `sqlite_rx.server.QueryStreamHandler`

        """
        super().setup()
        # Depending on the initialization parameters either get a plain stream or secure stream.
        self.rep_stream = self.stream(zmq.REP,
                                      self._bind_address,
                                      use_encryption=self._encrypt,
                                      use_zap=self._zap_auth,
                                      server_curve_id=self.server_curve_id,
                                      curve_dir=self.curve_dir)
        # Register the callback.
        self.rep_stream.on_recv(QueryStreamHandler(self.rep_stream,
                                                   self._database,
                                                   self._auth_config))

    def handle_signal(self, signum, frame):
        LOG.info("SQLiteServer %s PID %s received %r", self, self.pid, signum)
        LOG.info("SQLiteServer Shutting down")

        self.rep_stream.close()
        self.socket.close()
        self.loop.stop()

        if self.back_up_recurring_thread:
            self.back_up_recurring_thread.cancel()
        os._exit(os.EX_OK)

    def run(self):
        LOG.info("Setting up signal handlers")

        signal(SIGTERM, self.handle_signal)
        signal(SIGINT, self.handle_signal)

        self.setup()

        LOG.info("SQLiteServer (Tornado) i/o loop started..")

        if self.back_up_recurring_thread:
            self.back_up_recurring_thread.start()

        LOG.info("Ready to accept client connections on %s", self._bind_address)
        self.loop.start()


class QueryStreamHandler:

    def __init__(self,
                 rep_stream,
                 database: Union[bytes, str],
                 auth_config: dict = None):
        """
        Executes SQL queries and send results back on the `zmq.REP` stream

        Args:
             rep_stream: The zmq.REP socket stream on which to send replies.
             database: A path like object or the string ":memory:" for in-memory database.
             auth_config: A dictionary describing what actions are authorized, denied or ignored.

        """
        self._connection_pool = ConnectionCursorPool(database, auth_config)
        # self._connection = sqlite3.connect(database=database,
        #                                    isolation_level=None,
        #                                    check_same_thread=False)
        # self._connection.execute('pragma journal_mode=wal')
        # self._connection.set_authorizer(Authorizer(config=auth_config))
        # self._cursor = self._connection.cursor()
        self._rep_stream = rep_stream

    @staticmethod
    def capture_exception():
        exc_type, exc_value, exc_tb = sys.exc_info()
        exc_type_string = "%s.%s" % (exc_type.__module__, exc_type.__name__)
        error = {"type": exc_type_string, "message": traceback.format_exception_only(exc_type, exc_value)[-1].strip()}
        return error

    def __call__(self, message: List):
        try:
            message = message[-1]
            message = msgpack.loads(zlib.decompress(message), raw=False)
            self._rep_stream.send(self.execute(message))
        except Exception:
            LOG.exception("exception while preparing response")
            error = self.capture_exception()
            result = {"items": [],
                      "error": error}
            self._rep_stream.send(zlib.compress(msgpack.dumps(result)))

    def execute(self, message: dict, *args, **kwargs):
        execute_many = message['execute_many']
        execute_script = message['execute_script']
        database_name = message['database']
        error = None
        _cursor = self._connection_pool.cursor(database_name)
        try:
            if execute_script:
                LOG.debug("Query Mode: Execute Script")
                _cursor.executescript(message['query'])
            elif execute_many and message['params']:
                LOG.debug("Query Mode: Execute Many")
                _cursor.executemany(message['query'], message['params'])
            elif message['params']:
                LOG.debug("Query Mode: Conditional Params")
                _cursor.execute(message['query'], message['params'])
            else:
                LOG.debug("Query Mode: Default No params")
                _cursor.execute(message['query'])
        except Exception:
            LOG.exception("Exception while executing query %s", message['query'])
            error = self.capture_exception()

        result = {
            "items": [],
            "error": error
        }
        if error:
            return zlib.compress(msgpack.dumps(result))

        try:
            result['keys'] = list(map(lambda x: x[0], _cursor.description))
            result['items'] = list(_cursor.fetchall())
            # If rowcount attribute is set on the cursor object include it in the response
            if _cursor.rowcount > -1:
                result['rowcount'] = _cursor.rowcount
            # If lastrowid attribute is set on the cursor include it in the response
            if _cursor.lastrowid:
                result['lastrowid'] = _cursor.lastrowid

            return zlib.compress(msgpack.dumps(result))

        except Exception:
            LOG.exception("Exception while collecting rows")
            result['error'] = self.capture_exception()
            return zlib.compress(msgpack.dumps(result))


class ConnectionCursorPool:

    def __init__(self, database: Union[bytes, str],
                 auth_config: dict = None):
        self._cursor_pool = {}
        self._database = database
        self._auth_config = auth_config
        self._init_conn()

    def _init_conn(self):
        database = self._database
        if ':memory:' == database:
            self._create_connection("DEFAULT", database, self._auth_config)
        elif os.path.exists(database):
            if os.path.isfile(database):
                self._create_connection("DEFAULT", database, self._auth_config)
            elif os.path.isdir(database):
                files = os.listdir(database)
                for file in files:
                    if file.endswith('.db'):
                        path = os.path.join(database, file)
                        if os.path.isfile(path):
                            try:
                                self._create_connection(file, path, self._auth_config)
                            except:
                                pass

    def _create_connection(self, name, database, auth_config):
        connection = sqlite3.connect(database=database,
                                     isolation_level=None,
                                     check_same_thread=False)
        # connection.execute('pragma journal_mode=wal')
        connection.execute('pragma query_only=ON')
        connection.set_authorizer(Authorizer(config=auth_config))
        cursor = connection.cursor()
        LOG.debug("Create connection %s", name)
        self._cursor_pool.update({name: cursor})

    def cursor(self, database_name):
        return self._cursor_pool[database_name]


def main():
    # database is a path-like object giving the pathname
    # of the database file to be opened.

    # You can use ":memory:" to open a database connection to a database
    # that resides in RAM instead of on disk

    server = SQLiteServer(database="/Users/rmfish/Documents/Projects/PycharmProjects/sqlite_rx/data",
                          bind_address="tcp://127.0.0.1:5000")
    server.start()
    server.join()


if __name__ == '__main__':
    main()
