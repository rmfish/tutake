import logging
import logging.config

from apscheduler.schedulers.background import BackgroundScheduler
import tutake as ts
from tutake.api.tushare.process import ProcessType

# scheduler = BackgroundScheduler()
# scheduler.add_job(lambda:pro.process('daily'))


if __name__ == '__main__':
    pro = ts.process_api()
    print(pro.daily(process_type=ProcessType.INCREASE))
    print(pro.stock_basic(process_type=ProcessType.INCREASE))
