import pickle
import socket
import struct
import threading
from queue import Queue

# TCP 客户端配置
THREAD_COUNT = 5  # 线程数
CONNECTION_POOL_SIZE = 10  # 连接池大小


class RemoteClient:
    def __init__(self, address, port):
        self.connection_pool = Queue(CONNECTION_POOL_SIZE)
        self.lock = threading.Lock()
        self.address = address
        self.port = port
        # 初始化连接池
        self.initialize_connection_pool()

    # 创建 TCP 连接
    def create_connection(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        conn.connect((self.address, self.port))
        return conn

    # 初始化连接池
    def initialize_connection_pool(self):
        for _ in range(CONNECTION_POOL_SIZE):
            connection = self.create_connection()
            self.connection_pool.put(connection)

    # 从连接池获取连接
    def get_connection_from_pool(self):
        return self.connection_pool.get()

    # 将连接放回连接池
    def put_connection_to_pool(self, connection):
        self.connection_pool.put(connection)

    # 发送查询请求
    def query(self, data):
        # 从连接池获取连接
        connection = self.get_connection_from_pool()

        try:
            with connection:
                # 发送序列化后的数据
                serialized_payload = pickle.dumps(data)
                connection.sendall(struct.pack('>I', len(serialized_payload)))
                connection.sendall(serialized_payload)

                # 接收响应
                data_size = struct.unpack('>I', connection.recv(4))[0]
                received_payload = b""
                remaining_payload_size = data_size
                while remaining_payload_size != 0:
                    received_payload += connection.recv(remaining_payload_size)
                    remaining_payload_size = data_size - len(received_payload)
                    # 反序列化响应数据
                return pickle.loads(received_payload)
        except Exception as e:
            print(f"Error - {str(e)}")
        finally:
            # 将连接放回连接池
            self.put_connection_to_pool(connection)


if __name__ == '__main__':
    client = RemoteClient("127.0.0.1", 5000)
    result = client.query({"namespace": "tushare", "api_name": "index_weekly", 'kwargs': {"ts_code": '000002.SH'}})
    print(result)
