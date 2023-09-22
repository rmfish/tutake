import pandas as pd
import pendulum
from mock.mock import patch
from qlib.data import FeatureProvider, CalendarProvider, InstrumentProvider
from qlib.data.cache import H
from qlib.data.data import Cal

from tutake.utils.config import TutakeConfig

PRICE_COLS = ['open', 'close', 'high', 'low', 'pre_close']
FIELDS = {"vwap": "avg_price", "volume": "vol", }
INDEXES = ['000300.SH', '000905.SH', '000852.SH', '000903.SH', '000016.SH']


class TutakeProvider:
    def __init__(self, config: TutakeConfig):
        self.config = config

    def tushare(self):
        return self.config.load_tutake().tushare_api()


@patch("qlib.data", 'TutakeFeatureProvider')
class TutakeFeatureProvider(FeatureProvider, TutakeProvider):

    def __init__(self, config: TutakeConfig):
        TutakeProvider.__init__(self, config)

    def feature(self, instrument, field, start_index, end_index, freq):
        # validate
        if start_index is not None:
            start_index = start_index.strftime('%Y%m%d')
        if end_index is not None:
            end_index = end_index.strftime('%Y%m%d')
        field = str(field)[1:]
        mapping = FIELDS.get(field)
        if mapping is None:
            mapping = field

        if freq == 'day':
            if instrument in INDEXES:
                df = self.tushare().index_daily(ts_code=instrument, fields=f'trade_date,{mapping}',
                                                start_date=start_index, end_date=end_index, limit=100000)
            else:
                df = self.tushare().bak_daily(ts_code=instrument, fields=f'trade_date,{mapping}',
                                              start_date=start_index,
                                              end_date=end_index, limit=100000)
                if mapping in PRICE_COLS:
                    df_adj = self.tushare().adj_factor(ts_code=instrument, fields=f'trade_date,adj_factor',
                                                       start_date=start_index, limit=100000)
                    df = pd.merge(df, df_adj, how='left', left_on='trade_date', right_on='trade_date')
                    df[mapping] = df[mapping] * df['adj_factor'] / float(df_adj['adj_factor'][0])
                    df[mapping] = df[mapping].astype(float)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            df.sort_index(inplace=True)
            return df[mapping]


@patch("qlib.data", 'TutakeCalendarProvider')
class TutakeCalendarProvider(CalendarProvider, TutakeProvider):
    def __init__(self, config: TutakeConfig):
        TutakeProvider.__init__(self, config)

    def load_calendar(self, freq, future):
        if freq == 'day':
            dates = self.tushare().trade_cal(is_open=1)['cal_date'].unique().tolist()
            return [pd.Timestamp(x) for x in dates]


@patch("qlib.data", 'TutakeInstrumentProvider')
class TutakeInstrumentProvider(InstrumentProvider, TutakeProvider):
    def __init__(self, config: TutakeConfig):
        TutakeProvider.__init__(self, config)

    def _load_instruments(self, market, start_time=None, end_time=None, freq="day"):
        # csi100 中证100  -> 000903.SH
        # csi300 沪深300 -> 000300.SH
        # csi500 中证500 -> 000905.SH
        # csi1000 中证1000 -> 000852.SH
        # 000016.SH 上证50
        # 000985.CSI 中证全指

        ts_codes = []
        pretrade_date = self.tushare().trade_cal(cal_date=pendulum.now().format('YYYYMMDD'), exchange='SSE').at[
            0, 'pretrade_date']
        if end_time is None:
            end_time = pretrade_date
        index_code = None
        if market == 'csi300':
            index_code = '000300.SH'
        elif market == 'csi500':
            index_code = '000905.SH'
        elif market == 'csi1000':
            index_code = '000852.SH'
        elif market == 'csi100':
            index_code = '000903.SH'
        elif market == 'csi50':
            index_code = '000016.SH'

        _instruments = dict()
        if index_code is not None:
            df = self.tushare().index_stock(index_code=index_code, fields='con_code,list_date,delist_date')
            df['delist_date'] = df['delist_date'].fillna(pretrade_date)
        elif market == 'all':
            df = self.tushare().stock_basic(fields='ts_code,list_date,delist_date')
            df['delist_date'] = df['delist_date'].fillna(pretrade_date)
        else:
            df = self.tushare().stock_basic(ts_code=market, fields='ts_code,list_date,delist_date')
            df['delist_date'] = df['delist_date'].fillna(pretrade_date)
        for row in df.itertuples(index=False):
            _instruments.setdefault(row[0], []).append((pd.Timestamp(row[1]), pd.Timestamp(row[2])))
        return _instruments

    def list_instruments(self, instruments, start_time=None, end_time=None, freq="day", as_list=False):
        market = instruments["market"]
        if market in H["i"]:
            _instruments = H["i"][market]
        else:
            _instruments = self._load_instruments(market, start_time, end_time, freq=freq)
            H["i"][market] = _instruments
        # strip
        # use calendar boundary
        cal = Cal.calendar(freq=freq)
        start_time = pd.Timestamp(start_time or cal[0])
        end_time = pd.Timestamp(end_time or cal[-1])
        _instruments_filtered = {
            inst: list(
                filter(
                    lambda x: x[0] <= x[1],
                    [(max(start_time, pd.Timestamp(x[0])), min(end_time, pd.Timestamp(x[1]))) for x in spans],
                )
            )
            for inst, spans in _instruments.items()
        }
        _instruments_filtered = {key: value for key, value in _instruments_filtered.items() if value}
        # filter
        filter_pipe = instruments["filter_pipe"]
        for filter_config in filter_pipe:
            from qlib.data import filter as F  # pylint: disable=C0415

            filter_t = getattr(F, filter_config["filter_type"]).from_config(filter_config)
            _instruments_filtered = filter_t(_instruments_filtered, start_time, end_time, freq)
        # as list
        if as_list:
            return list(_instruments_filtered)
        return _instruments_filtered
