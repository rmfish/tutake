import json
import logging
import random
import threading
import time
import types
from datetime import datetime

import pandas as pd
import requests
from pandas import DataFrame

from tutake.api.base_dao import Records
from tutake.api.process import CriticalException
from tutake.api.process_client import Task
from tutake.utils.config import TUSHARE_TOKENS_KEY, TUSHARE_TOKEN_CHECK_KEY
from tutake.utils.utils import end_of_day

tushare_logger = logging.getLogger("tutake.tushare")

tushare_clients = None
tushare_clients_init_lock = threading.Lock()


def _get_tushare_clients(_config):
    global tushare_clients
    if tushare_clients is not None:
        return tushare_clients
    else:
        tushare_clients_init_lock.acquire()
        try:
            if tushare_clients is not None:
                return tushare_clients
            tushare_tokens = _config.get_config(TUSHARE_TOKENS_KEY)
            if tushare_tokens and len(tushare_tokens) > 1:
                clients = []
                for t in tushare_tokens:
                    if tushare_tokens[t]:
                        clients.extend([TushareClient(token, t, time.time() - t) for token in tushare_tokens[t]])
                if _config.get_config(TUSHARE_TOKEN_CHECK_KEY, False):
                    tushare_clients = [client for client in clients if client.validate_token()]
                else:
                    tushare_clients = clients
                return tushare_clients
        finally:
            tushare_clients_init_lock.release()


class TuShareBase(Task):
    def __init__(self, api_name, config, token_integral=120):
        super().__init__(api_name, "tushare")
        tushare_token = config.get_tushare_token()
        if tushare_token:
            self.t_api = TushareClient(tushare_token)
        tushare_tokens = config.get_config(TUSHARE_TOKENS_KEY)
        self.client_queue = None
        if tushare_tokens and len(tushare_tokens) > 1:
            clients = _get_tushare_clients(config)
            self.client_queue = TushareTokenQueue([client for client in clients if client.score >= token_integral],
                                                  self.logger)

    def tushare_query(self, api, fields, **kwargs) -> Records:
        if self.client_queue:
            client = self.client_queue.get(65)
            if client:
                try:
                    return client.query_records(api, fields, **kwargs)
                except Exception as err:
                    if str(err).startswith("抱歉，您每分钟最多访问该接口"):
                        self.client_queue.alive(client, time.time() + 60)
                        tushare_logger.debug(
                            f"Flow limit {api} {client} {self.client_queue.useful_size()} {','.join(str(err).split('，')[0:2])}")
                        return self.tushare_query(api, fields, **kwargs)
                    elif str(err).startswith("抱歉，您每天最多访问该接口"):
                        self.client_queue.alive(client, end_of_day().timestamp())
                        tushare_logger.debug(
                            f"Request limit {api} {client} {self.client_queue.useful_size()} {','.join(str(err).split('，')[0:2])}")
                        return self.tushare_query(api, fields, **kwargs)
                    elif str(err).startswith("抱歉，您没有访问该接口的权限") or str(err).startswith(
                            "抱歉，您输入的TOKEN无效！") or str(err).startswith("抱歉，检测到您存在恶意行为"):
                        self.client_queue.alive(client, time.time() + 4294967.0)
                        tushare_logger.debug(
                            f"Request limit {api} {client} {self.client_queue.useful_size()} {','.join(str(err).split('，')[0:2])}")
                        return self.tushare_query(api, fields, **kwargs)
                    else:
                        raise err
            else:
                raise CriticalException(f"None useful ts token to query {api}")
        elif self.t_api:
            try:
                return self.t_api.query_records(api, fields, **kwargs)
            except Exception as err:
                if str(err).startswith("抱歉，您每分钟最多访问该接口"):
                    tushare_logger.debug(f"Flow limit {api}, sleep 60 seconds and retry")
                    time.sleep(60)
                    return self.tushare_query(api, fields, **kwargs)
                if str(err).startswith("抱歉，您输入的TOKEN无效！"):
                    tushare_logger.debug(f"Error token {api}, {err}")
                    raise CriticalException(f"Error token {api}", err)
                else:
                    raise err


class TushareClient:
    __token = ''
    __http_url = 'http://api.waditu.com'

    def __init__(self, token, score=0, _time=0.0):
        self._time = _time
        self.score = score
        self.__token = token
        self.__timeout = 30

    def query(self, api_name, fields='', **kwargs) -> DataFrame:
        result = self.query_records(api_name, fields, **kwargs)
        return pd.DataFrame(result.items, columns=result.fields)

    def query_json(self, api_name, fields='', **kwargs):
        req_params = {
            'api_name': api_name,
            'token': self.__token,
            'params': kwargs,
            'fields': fields
        }

        res = requests.post(self.__http_url, json=req_params, timeout=self.__timeout)
        if res:
            result = json.loads(res.text)
            if result['code'] != 0:
                raise Exception(result['msg'])
            return result['data']
        else:
            return {'items': [], 'fields': []}

    def query_records(self, api_name, fields='', **kwargs) -> Records:
        res = self.query_json(api_name, fields, **kwargs)
        if res:
            items = [tuple(i) for i in res['items']]
            return Records(res['fields'], items)
        else:
            return Records()

    def validate_token(self):
        try:
            df = self.query('user', token=self.__token)
            score = self.score
            self.score = df['到期积分'].sum()
            if score != self.score:
                logging.error(f"Check tushare token diff token:{self.__token}, acture score is {self.score}")
            return True
        except Exception as err:
            logging.error(f"Check tushare token error {err}. token:{self.__token}")
            return False

    def set_alive_time(self, _time):
        self._time = _time

    def alive(self) -> float:
        return self._time

    def is_alive(self, _time) -> bool:
        return _time > self._time

    def __str__(self):
        return f"Tushare token {self.__token} [score:{self.score}] [alive_time:{datetime.fromtimestamp(self._time)}]"

    def __repr__(self):
        return self.__str__()


class TushareTokenQueue:
    def __init__(self, items: [TushareClient], logger):
        self.items = items
        self.mutex = threading.Lock()
        self.logger = logger

        self.not_empty = threading.Condition(self.mutex)
        sorted(self.items, key=lambda x: x.alive())

    def alive(self, item, alive_time):
        item.set_alive_time(alive_time)
        sorted(self.items, key=lambda x: x.alive())
        delay = alive_time - time.time()
        if delay >= 0:
            def release():
                with self.not_empty:
                    sorted(self.items, key=lambda x: x.alive())
                    self.logger.debug(f"Release ts client {item}")
                    self.not_empty.notifyAll()

            timer = threading.Timer(alive_time - time.time(), release)
            timer.setDaemon(True)
            timer.start()

    def get(self, timeout=None):
        with self.not_empty:
            if timeout is None:
                while not self._contains():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time.time() + timeout
                while not self._contains():
                    remaining = endtime - time.time()
                    if remaining <= 0.0:
                        return None
                    self.not_empty.wait(remaining)
            item = self._get()
            return item

    def _contains(self):
        c = self.items[0].alive() <= time.time()
        return c

    def _get(self):
        now = time.time()
        item = [i for i in self.items if i.is_alive(now)]
        return random.choice(item)

    def useful_size(self):
        now = time.time()
        return len([i for i in self.items if i.is_alive(now)])

    def __str__(self):
        return str(self.items)

    # __class_getitem__ = classmethod(types.GenericAlias)
