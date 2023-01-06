import json
import random
import threading
import time
import types
from datetime import datetime

import pandas as pd
import requests
import tushare as ts

from tutake.api.process_client import Task
from tutake.api.process_report import CriticalException
from tutake.utils.config import TUSHARE_TOKENS_KEY, TutakeConfig
from tutake.utils.utils import end_of_day


def _is_useful_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.stock_basic(limit=100)
        if df.shape[0] == 100:
            return True
    except Exception:
        return False


def _is_2000_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.stk_managers(ts_code='000001.SZ')
        if df.shape[0] >= 1:
            return True
    except Exception:
        return False


def _is_800_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.block_trade(ts_code='000001.SZ')
        if df.shape[0] >= 1:
            return True
    except Exception:
        return False


def _is_600_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.stk_account(ts_code='000001.SZ')
        if df.shape[0] >= 1:
            return True
    except Exception:
        return False


def _is_120_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.libor()
        if df.shape[0] >= 1:
            return True
    except Exception:
        return False


def _is_5000_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.ggt_monthly(trade_date='201906')
        if df.shape[0] >= 1:
            return True
    except Exception:
        return False


def _baseline_score(i):
    if _is_5000_token(i):
        return 5000, i
    elif _is_2000_token(i):
        return 2000, i
    elif _is_800_token(i):
        return 800, i
    elif _is_600_token(i):
        return 600, i
    elif _is_120_token(i):
        return 120, i
    elif _is_useful_token(i):
        return 0, i
    else:
        return -1, i


def check_token(config: TutakeConfig):
    config_tokens = config.get_config(TUSHARE_TOKENS_KEY)
    for level in config_tokens.keys():
        tokens = config_tokens.get(level)
        for token in tokens:
            val = _baseline_score(token)
            if val[0] != level:
                print(f"Check failed. {token} expect:{level} actual:{val[0]}")


def _test_token(path):
    with open(path, 'r', encoding='utf-8') as f:
        tokens = {"5000": set(), "2000": set(), "800": set(), "120": set()}
        for t in set(f.read().split("\n")):
            tt = t.split(" #")
            tokens[tt[1]].add(tt[0])
        for i in tokens:
            print(f"{i}:")
            for j in tokens[i]:
                print(f" - {j}")
        # print(tokens)
        # i = _baseline_score(t.split(" ")[0])
        # if i[0] > 0:
        #     print(f"{i[1]} #{i[0]}")


class TushareTokenPool(object):

    def __init__(self, score, tokens: []):
        self.score = score
        self.t_apis = {i: ts.pro_api(tokens[i]) for i in range(len(tokens))}
        self.token_index = 0

    def get_api(self):
        if self.t_apis:
            api = self.t_apis[self.token_index]
            self.token_index = (self.token_index + 1) % len(self.t_apis.keys())
            return api
        else:
            return None


class TuShareBase(Task):
    def __init__(self, api_name, config, token_integral=120):
        super().__init__(api_name, "tushare")
        tushare_token = config.get_tushare_token()
        if tushare_token:
            self.t_api = TushareClient(tushare_token)
        tushare_tokens = config.get_config(TUSHARE_TOKENS_KEY)
        self.client_queue = None
        if tushare_tokens and len(tushare_tokens) > 1:
            clients = []
            for t in tushare_tokens:
                if t >= token_integral:
                    clients.extend([TushareClient(token, t, time.time() - t) for token in tushare_tokens[t]])
            self.client_queue = TushareTokenQueue(clients, self.logger)
        # assert self.t_api is not None or self.client_queue is not None, 'Tushare token is required, pls config it in config.yaml'

    def tushare_query(self, api, fields, **kwargs):
        if self.client_queue:
            client = self.client_queue.get(65)
            if client:
                try:
                    return client.query(api, fields, **kwargs)
                except Exception as err:
                    if str(err).startswith("抱歉，您每分钟最多访问该接口"):
                        self.client_queue.alive(client, time.time() + 60)
                        self.logger.debug(
                            f"Flow limit {api} {client} {self.client_queue.useful_size()} {','.join(str(err).split('，')[0:2])}")
                        return self.tushare_query(api, fields, **kwargs)
                    elif str(err).startswith("抱歉，您每天最多访问该接口"):
                        self.client_queue.alive(client, end_of_day().timestamp())
                        print(
                            f"Request limit {api} {client} {self.client_queue.useful_size()} {','.join(str(err).split('，')[0:2])}")
                        return self.tushare_query(api, fields, **kwargs)
                    elif str(err).startswith("抱歉，您没有访问该接口的权限") or str(err).startswith(
                            "抱歉，您输入的TOKEN无效！"):
                        self.client_queue.alive(client, time.time() + 4294967.0)
                        print(
                            f"Request limit {api} {client} {self.client_queue.useful_size()} {','.join(str(err).split('，')[0:2])}")
                        return self.tushare_query(api, fields, **kwargs)
                    else:
                        raise err
            else:
                raise CriticalException(f"None useful ts token to query {api}")
        elif self.t_api:
            try:
                return self.t_api.query(api, fields, **kwargs)
            except Exception as err:
                if str(err).startswith("抱歉，您每分钟最多访问该接口"):
                    self.logger.debug(f"Flow limit {api}, sleep 60 seconds and retry")
                    time.sleep(60)
                    return self.tushare_query(api, fields, **kwargs)
                if str(err).startswith("抱歉，您输入的TOKEN无效！"):
                    self.logger.debug(f"Error token {api}, {err}")
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

    def query(self, api_name, fields='', **kwargs):
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
            data = result['data']
            columns = data['fields']
            items = data['items']
            return pd.DataFrame(items, columns=columns)
        else:
            return pd.DataFrame()

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

    __class_getitem__ = classmethod(types.GenericAlias)


if __name__ == '__main__':
    config = TutakeConfig("/Users/rmfish/Documents/Projects/PycharmProjects/tutake")
    check_token(config)

    # _test_token("/Users/rmfish/Documents/Projects/PycharmProjects/tutake/tmp/token2.txt")
    # tokens = [TushareClient(i, time.time() - 5000) for i in ["123", "345"]]
    # queue = TushareTokenQueue(tokens)
    # print(queue)
    # # for i in range(10):
    # #     print(queue.get())
    # queue.alive(tokens[1], time.time() + 100)
    # queue.alive(tokens[0], time.time() + 100)
    # start = time.time()
    # for i in range(50):
    #     time.sleep(0.3)
    #     j = queue.get(5)
    #     print("{} {}".format(time.time() - start, j))
