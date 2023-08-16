import logging.config
import os
import pickle
import socketserver
import struct
import threading

from pandas import DataFrame

from tutake import Tutake
from tutake.utils.config import TUTAKE_SERVER_PORT_KEY

PARENT_DIR = os.path.dirname(__file__)

LOG = logging.getLogger(__name__)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            data_size = struct.unpack('>I', self.request.recv(4))[0]
            received_payload = b""
            remaining_payload_size = data_size
            while remaining_payload_size != 0:
                received_payload += self.request.recv(remaining_payload_size)
                remaining_payload_size = data_size - len(received_payload)
            payload = pickle.loads(received_payload)
            self.server.execute(payload, self.request)
        except ConnectionError as conError:
            pass


class RemoteServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, tutake: Tutake):
        self.allow_reuse_port = True
        self.tutake = tutake
        port = self.tutake.config.get_config(TUTAKE_SERVER_PORT_KEY, 5000)
        super().__init__(("127.0.0.1", port), ThreadedTCPRequestHandler, bind_and_activate=False)

    def execute(self, payload, request):
        namespace = payload.get('namespace')
        api_name = payload.get('api_name')
        fields = payload.get('fields')
        kwargs = payload.get('kwargs') or {}

        if namespace == "tushare":
            df = self.tutake.tushare_api().query(api_name, fields, **kwargs)
        elif namespace == "xueqiu":
            df = self.tutake.xueqiu_api().query(api_name, fields, **kwargs)
        else:
            df = DataFrame()
        serialized_payload = pickle.dumps(df)
        request.sendall(struct.pack('>I', len(serialized_payload)))
        request.sendall(serialized_payload)

    def start(self, daemon=False):
        self.allow_reuse_address = True
        self.server_bind()
        self.server_activate()
        if daemon:
            try:
                self.serve_forever()
            except KeyboardInterrupt:
                print('Server stop by Keyboard Interrupt.')
        else:
            server_thread = threading.Thread(target=self.serve_forever)
            server_thread.daemon = True
            server_thread.start()


if __name__ == '__main__':
    # main()

    server = RemoteServer(Tutake("../../config.yml"))
    server.start()

    # ip, port = server.server_address
    # try:
    #     server.serve_forever()
    #     # server_thread = threading.Thread(target=server.serve_forever)
    #     # server_thread.daemon = False
    #     # server_thread.start()
    #
    #     # server.serve_forever()
    # except KeyboardInterrupt:
    #     print('Server stop by Keyboard Interrupt.')
