import logging.config
import os
import pickle
import socket
import threading
import zlib

import zmq

DEFAULT_REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 5
DEFAULT_DATABASE_NAME = "DEFAULT"

PARENT_DIR = os.path.dirname(__file__)

LOG = logging.getLogger(__name__)

__all__ = ['TutakeClient']


class TutakeClient(threading.local):

    def __init__(self,
                 connect_address: str,
                 context=None):
        self.client_id = "python@{}_{}".format(socket.gethostname(), threading.get_ident())
        self._context = context or zmq.Context.instance()
        self._connect_address = connect_address
        self._client = self._init_client()

    def _init_client(self):
        LOG.info("Initializing Client")
        client = self._context.socket(zmq.REQ)
        client.connect(self._connect_address)
        self._poller = zmq.Poller()
        self._poller.register(client, zmq.POLLIN)
        LOG.info("registered zmq poller")
        LOG.info("client %s initialisation completed", self.client_id)
        return client

    def _send_request(self, request):
        try:
            self._client.send(zlib.compress(pickle.dumps(request)))
        except zmq.ZMQError:
            LOG.exception("Exception while sending message")
            raise Exception("ZMQ send error")
        except zlib.error:
            LOG.exception("Exception while request body compression")
            raise Exception("zlib compression error")
        except Exception:
            LOG.exception("Exception while serializing the request")
            raise Exception("msgpack serialization")

    def _recv_response(self):
        try:
            response = pickle.loads(zlib.decompress(self._client.recv()))
        except zmq.ZMQError:
            LOG.exception("Exception while receiving message")
            raise Exception("ZMQ receive error")
        except zlib.error:
            LOG.exception("Exception while request body decompression")
            raise Exception("zlib compression error")
        except Exception:
            LOG.exception("Exception while deserializing the request")
            raise Exception("msgpack deserialization error")
        return response

    def query(self, namespace: str, api_name: str, fields: str = '', **kwargs) -> dict:
        LOG.info("Executing query %s %s %s for client %s", namespace, api_name, fields, self.client_id)

        request_retries = REQUEST_RETRIES
        request_timeout = DEFAULT_REQUEST_TIMEOUT

        request = {
            "namespace": namespace,
            "api_name": api_name,
            "fields": fields,
            "kwargs": kwargs,
        }

        expect_reply = True

        while request_retries:
            # LOG.info("Preparing to send request")
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

        raise Exception("No response after retrying. Abandoning Request")

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


if __name__ == '__main__':
    client = TutakeClient("tcp://0.0.0.0:9527")
    # for i in range(1000):
    #     client.execute(namespace="tushare", api_name="index_weekly", fields="", ts_code='000002.SH')
    print(client.query(namespace="tushare", api_name="index_weekly", fields="", ts_code='000002.SH'))
