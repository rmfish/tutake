import logging.config
import os
import socket
import threading
import zlib

import zmq

import msgpack
from tutake.remote.auth import KeyMonkey
from tutake.remote.exception import (
    SQLiteRxCompressionError,
    SQLiteRxConnectionError,
    SQLiteRxTransportError,
    SQLiteRxSerializationError,
)

DEFAULT_REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 5
DEFAULT_DATABASE_NAME = "DEFAULT"

PARENT_DIR = os.path.dirname(__file__)

LOG = logging.getLogger(__name__)

__all__ = ['SQLiteClient']


class SQLiteClient(threading.local):

    def __init__(self,
                 connect_address: str,
                 use_encryption: bool = False,
                 curve_dir: str = None,
                 client_curve_id: str = None,
                 server_curve_id: str = None,
                 context=None):
        """
        A thin and reliable client to send query execution requests to a remote :class: `sqlite_rx.server.SQLiteServer`

        The SQLiteClient has a single method called execute().

        Args:
            connect_address: The address and port on which the server will listen for client requests.
            use_encryption: True means use `CurveZMQ` encryption. False means don't
            curve_dir: Curve key files directory. Defaults to `~/.curve`
            client_curve_id: Server curve id. Defaults to "id_server_{}_curve".format(socket.gethostname())
            server_curve_id: Client curve id. Defaults to "id_client_{}_curve".format(socket.gethostname())
            context: `zmq.Context`

        """
        self.client_id = "python@{}_{}".format(socket.gethostname(), threading.get_ident())
        self._context = context or zmq.Context.instance()
        self._connect_address = connect_address
        self._encrypt = use_encryption
        self.server_curve_id = server_curve_id if server_curve_id else "id_server_{}_curve".format(socket.gethostname())
        client_curve_id = client_curve_id if client_curve_id else "id_client_{}_curve".format(socket.gethostname())
        self._keymonkey = KeyMonkey(client_curve_id, destination_dir=curve_dir)
        self._client = self._init_client()

    def _init_client(self):
        LOG.info("Initializing Client")
        client = self._context.socket(zmq.REQ)
        if self._encrypt:
            LOG.debug("requests will be encrypted; will load CurveZMQ keys")
            client = self._keymonkey.setup_secure_client(client, self._connect_address, self.server_curve_id)
        client.connect(self._connect_address)
        self._poller = zmq.Poller()
        self._poller.register(client, zmq.POLLIN)
        LOG.info("registered zmq poller")
        LOG.info("client %s initialisation completed", self.client_id)
        return client

    def database_client(self, database: str):
        return SQLiteDatabaseClient(database, self)

    def _send_request(self, request):
        try:
            self._client.send(zlib.compress(msgpack.dumps(request)))
        except zmq.ZMQError:
            LOG.exception("Exception while sending message")
            raise SQLiteRxTransportError("ZMQ send error")
        except zlib.error:
            LOG.exception("Exception while request body compression")
            raise SQLiteRxCompressionError("zlib compression error")
        except Exception:
            LOG.exception("Exception while serializing the request")
            raise SQLiteRxSerializationError("msgpack serialization")

    def _recv_response(self):
        try:
            response = msgpack.loads(zlib.decompress(self._client.recv()), raw=False)
        except zmq.ZMQError:
            LOG.exception("Exception while receiving message")
            raise SQLiteRxTransportError("ZMQ receive error")
        except zlib.error:
            LOG.exception("Exception while request body decompression")
            raise SQLiteRxCompressionError("zlib compression error")
        except Exception:
            LOG.exception("Exception while deserializing the request")
            raise SQLiteRxSerializationError("msgpack deserialization error")
        return response

    def execute(self,
                query: str,
                *args,
                **kwargs) -> dict:
        """Synchronous which will send the `query` and the parameters to a remote SQLiteServer instance,
        wait for the response and return the response to the caller.

        Important keyword arguments are as follows:

            1. `execute_many`: True if you want to insert multiple rows with one execute call.

            2. `execute_script`: True if you want to execute a script with multiple SQL commands.

            3. `request_timeout`: Time in ms to wait for a response before retrying. Default is 2500 ms

            4. `retries`: Number of times to retry before abandoning the request. Default is 5

        Args:
            query: A valid SQL query or SQL script

        Returns:
            response: A dictionary of the form
            {
                "items": []
                "error": None
            }

        Raises:
            sqlite_rx.exception.SQLiteRxTransportError: An error at the Transport layer i.e. zmq socket
            sqlite_rx.exception.SQLiteRxCompressionError: An error while compressing the request body using `zlib`
            sqlite_rx.exception.SQLiteRxSerializationError: An error while serializing the request body using `msgpack`

        """
        LOG.info("Executing query %s for client %s", query, self.client_id)

        request_retries = kwargs.pop('retries', REQUEST_RETRIES)
        execute_many = kwargs.pop('execute_many', False)
        execute_script = kwargs.pop('execute_script', False)
        request_timeout = kwargs.pop('request_timeout', DEFAULT_REQUEST_TIMEOUT)
        database = kwargs.pop('database', DEFAULT_DATABASE_NAME)

        # Do some client side validations.
        if execute_script and execute_many:
            raise ValueError("Both `execute_script` and `execute_many` cannot be True")

        request = {
            "client_id": self.client_id,
            "query": query,
            "params": args,
            "execute_many": execute_many,
            "execute_script": execute_script,
            "database": database,
        }

        expect_reply = True

        while request_retries:
            LOG.info("Preparing to send request")
            self._send_request(request)
            while expect_reply:
                socks = dict(self._poller.poll(request_timeout))
                if socks.get(self._client) == zmq.POLLIN:
                    response = self._recv_response()
                    return response
                else:
                    LOG.warning("No response from server, retrying...")
                    self.cleanup()
                    request_retries -= 1
                    if request_retries == 0:
                        LOG.error("Server seems to be offline, abandoning")
                        break
                    LOG.info("Reconnecting and resending request %r", request)
                    self._client = self._init_client()
                    self._send_request(request)

        raise SQLiteRxConnectionError("No response after retrying. Abandoning Request")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        try:
            self._client.setsockopt(zmq.LINGER, 0)
            self._client.close()
            self._poller.unregister(self._client)
        except zmq.ZMQError as e:
            if e.errno in (zmq.EINVAL,
                           zmq.EPROTONOSUPPORT,
                           zmq.ENOCOMPATPROTO,
                           zmq.EADDRINUSE,
                           zmq.EADDRNOTAVAIL,):
                LOG.error("ZeroMQ Transportation endpoint was not setup")

            elif e.errno in (zmq.ENOTSOCK,):
                LOG.error("ZeroMQ request was made against a non-existent device or invalid socket")

            elif e.errno in (zmq.ETERM, zmq.EMTHREAD,):
                LOG.error("ZeroMQ context is not a state to handle this request for socket")
        except Exception:
            LOG.exception("Exception while shutting down SQLiteClient")


class SQLiteDatabaseClient:

    def __init__(self, database: str, client: SQLiteClient):
        self._database = database
        self._client = client

    def execute(self,
                query: str,
                *args,
                **kwargs) -> dict:
        kwargs['database'] = self._database
        return self._client.execute(query, *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        self._client.cleanup()


if __name__ == '__main__':
    # client = SQLiteClient("tcp://127.0.0.1:5000")
    client = SQLiteClient("tcp://sqlite.rmfish.top:49191")
    meta = SQLiteDatabaseClient("tushare_daily.db", client)

    with meta:
        result = meta.execute(
            '''SELECT tushare_daily.id, tushare_daily.ts_code, tushare_daily.trade_date, tushare_daily.open, tushare_daily.high, tushare_daily.low, tushare_daily.close, tushare_daily.pre_close, tushare_daily.change, tushare_daily.pct_chg, tushare_daily.vol, tushare_daily.amount 
FROM tushare_daily 
WHERE tushare_daily.ts_code = '000002.SZ' ORDER BY trade_date,ts_code
 LIMIT 6000''')
        print(result)
