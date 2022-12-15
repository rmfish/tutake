import time
from urllib.parse import urlparse

import pandas as pd
import pendulum
import requests

from tutake.api.process_client import Task
from tutake.api.symbol import XueQiuSymbol
from tutake.utils.singleton import Singleton


class DomainSession(object):
    def __init__(self, domain):
        self.domain = domain
        self.session = None
        self.create_time = None
        self.header = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Referer": domain
        }

    def get_session(self, refresh=False):
        if refresh or self.session is None or self.create_time is None or (
                pendulum.now().diff(self.create_time).hours > 1):
            self.session = requests.Session()
            self.session.get(self.domain, headers=self.header)
            self.create_time = pendulum.now()
        return self.session

    def get(self, url: str, **kwargs) -> requests.Response:
        if not self.session:
            self.get_session(True)
        resp = self.session.get(url, headers=self.header, **kwargs)
        return resp


@Singleton
class XueQiuSession(object):
    def __init__(self):
        self.sessions = self._pre_load()
        self._pre_load()

    def _pre_load(self):
        domains = ["https://xueqiu.com/", "https://danjuanfunds.com/"]
        sessions = {}
        for d in domains:
            session = DomainSession(d)
            session.get_session()
            sessions[d] = session
        return sessions

    def _get_url_host(self, url):
        parsed_uri = urlparse(url)
        return f'{parsed_uri.scheme}://{".".join(parsed_uri.netloc.split(".")[-2:])}/'

    def _get_session(self, url, refresh=False):
        domain = self._get_url_host(url)
        session = self.sessions.get(domain)
        if not session:
            session = DomainSession(domain)
            self.sessions[domain] = session
        return session

    def get(self, url, refresh=False):
        return self._get_session(url, refresh).get(url)


class XueQiuBase(Task):
    def __init__(self, api_name, config):
        super().__init__(api_name, 'xueqiu')
        self.name = api_name
        self.session = XueQiuSession()

    def index_valuation_request(self, **kwargs):
        url = "https://danjuanfunds.com/djapi/index_eva/dj"
        response = self.session.get(url)
        if response.status_code == 200:
            result = response.json()
            df = pd.json_normalize(result.get("data"), record_path=['items'])
            if df.shape[0] > 0:
                df['ts_code'] = df['index_code'].apply(lambda x: XueQiuSymbol(x).trade_code())
                df['trade_date'] = df['ts'].apply(
                    lambda x: pendulum.from_timestamp(x / 1000, tz="Asia/Shanghai").format("YYYYMMDD"))
            result = df[
                ['ts_code', 'name', 'trade_date', 'ttype', 'pe', 'pe_percentile', 'peg', 'pb', 'pb_percentile', 'roe',
                 'yeild', 'eva_type']]
            if kwargs.get("date"):
                return result[result['trade_date'] == kwargs.get("date")]
            else:
                return result
        else:
            raise XueQiuException(f"Error request index_valuation ", response)

    def hot_stock_request(self, **kwargs):
        hot_type = kwargs.get('hot_type')
        map = {'etf_query': 'hot_query', 'etf_1h': 'hot_1h', 'etf_follow': 'hot_follow_7', "stock_query": 10,
               "stock_increase": 10, "stock_comment": 30, "stock_follow": 40, "cube": "cube"}

        if hot_type.startswith('etf') and hot_type in map.keys():
            url = f"https://xueqiu.com/snowpard/hot_etf/list.json?type={map.get(hot_type)}"
            response = self.session.get(url)
            if response.status_code == 200:
                result = response.json()
                df = pd.json_normalize(result.get("data"), record_path=['list'])
                if df.shape[0] > 0:
                    df['ts_code'] = df['symbol'].apply(lambda x: XueQiuSymbol(x).trade_code())
                    df['hot_type'] = hot_type
                    df['trade_date'] = pendulum.now().format("YYYYMMDD")
                return df[['ts_code', 'name', 'trade_date', 'hot_type', 'value', 'rank']]
            else:
                raise XueQiuException(f"Error request {hot_type} hot_etf ", response)
        elif hot_type.startswith('stock') and hot_type in map.keys():
            order_by = 'value'
            path = 'list'
            if hot_type == 'stock_increase':
                order_by = 'rank_change'
                path = 'new_list'
            url = f"https://stock.xueqiu.com/v5/stock/hot_stock/{path}.json?page=1&size=100&order=desc&order_by={order_by}&_={int(time.time())}&type={map.get(hot_type)}&x=0.5&include=true"
            response = self.session.get(url)
            if response.status_code == 200:
                result = response.json()
                df = pd.json_normalize(result.get("data"), record_path=['items'])
                if df.shape[0] > 0:
                    df['ts_code'] = df['symbol'].apply(lambda x: XueQiuSymbol(x).trade_code())
                    df['hot_type'] = hot_type
                    df['trade_date'] = pendulum.now().format("YYYYMMDD")
                    df['rank'] = df.index
                return df[['ts_code', 'name', 'trade_date', 'hot_type', 'value', 'rank', 'increment']]
            else:
                raise XueQiuException(f"Error request {hot_type} hot_stock ", response)
        elif hot_type.startswith('cube') and hot_type in map.keys():
            url = f"https://xueqiu.com/cube/center/cube_found/hot_symbol_list.json?page=1&size=100"
            response = self.session.get(url)
            if response.status_code == 200:
                result = response.json()
                df = pd.json_normalize(result.get("data"), record_path=['list'])
                if df.shape[0] > 0:
                    df['ts_code'] = df['symbol'].apply(lambda x: XueQiuSymbol(x).trade_code())
                    df['hot_type'] = hot_type
                    df['value'] = df['trade_score']
                    df['trade_date'] = pendulum.now().format("YYYYMMDD")
                return df[['ts_code', 'name', 'trade_date', 'hot_type', 'value', 'rank']]
            else:
                raise XueQiuException(f"Error request {hot_type} hot_cube ", response)


class XueQiuException(Exception):
    def __init__(self, message, response):
        self.message = message
        self.url = response.url
        self.method = response.request.method
        self.headers = response.headers
        self.reason = response.reason
        self.text = response.text
        self.status_code = response.status_code

    def __str__(self):
        return f"{self.status_code} {self.text}"


if __name__ == '__main__':
    xq = XueQiuBase("test", None)
    # print(xq.hot_stock_request(hot_type='etf_query'))
    # print(xq.hot_stock_request(hot_type='stock_query'))
    print(xq.index_valuation_request())
