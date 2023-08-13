import json
import logging
import os
import pathlib

import jinja2
import pendulum
from yapf.yapflib.yapf_api import FormatCode

from tutake.code.tushare_api import JsonConfigApi
from tutake.utils.utils import file_dir

logger = logging.getLogger("api.generate")


def get_sql_type(type):
    if type == 'str':
        return 'String'
    elif type == 'int':
        return 'Integer'
    elif type == 'float':
        return 'Float'
    elif type == 'number':
        return 'Float'
    elif type == 'datetime':
        return 'String'
    elif type == 'bool' or type == 'boolean':
        return 'Boolean'
    raise Exception('Unsupport type {}'.format(type))


class CodeGenerator(object):

    def __init__(self, tmpl_dir, output_dir):
        self.tmpl_dir = tmpl_dir
        self.output_dir = output_dir
        loader = jinja2.FileSystemLoader(tmpl_dir)
        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters['get_sql_type'] = get_sql_type
        env.globals['now'] = pendulum.now().format("YYYY/MM/DD")
        self.env = env

    def render_code(self, code_dir: str, file_name: str, code: str, overwrite: bool = True, file_suffix: str = 'py'):
        file_path = pathlib.Path(code_dir, f'{file_name}.{file_suffix}')
        if os.path.exists(file_path) and not overwrite:
            # 如果文件存在，且设置不覆盖，就直接退出
            return

        with open(file_path, 'w', encoding='utf-8') as file:
            try:
                formatted, changed = FormatCode(code, style_config='setup.cfg')
                file.write(formatted)
            except Exception as err:
                file.write(code)
                logger.error("Exp in render code {} {}".format(file_name, err))

    def _load_api_config(self, api, api_dir):
        if api:
            config_file = pathlib.PurePath(api_dir, 'config', f"{api['name']}.json")
            if os.path.exists(config_file):
                f = open(config_file, encoding='utf-8')
                data = json.load(f)
                return {**api, **data}
            else:
                return api

    def generate_api_code(self, api, prefix, package, api_tmpl=None, api_ext_tmpl=None):
        if not api:
            print(f"Api is None.")
            return None
        code_dir = pathlib.PurePath(self.output_dir, package)
        api_config = self._load_api_config(api, code_dir)
        if api_config and api_config.get('name'):
            print("Render code {} {}.py".format(api['id'], api_config.get('name')))
            if api_config.get('path'):
                api_config['path'] = '-'.join(tups[1] for tups in api_config.get('path'))
            api_config['table_name'] = f"{prefix}_{api_config.get('name')}"
            if not api_config.get('if_exists'):
                api_config['if_exists'] = 'append'
            if not api_config.get('database'):
                api_config['database'] = f"{prefix}_{api_config.get('name')}"
            if not api_config.get('default_limit'):
                api_config['default_limit'] = ""

            api_config['title_name'] = "{}".format(api_config['name'].replace('_', ' ').title().replace(' ', ''))
            api_config['entity_name'] = f"{prefix.capitalize()}{api_config['title_name']}"

            self.set_index(api_config)
            self.generate_order_by(api_config)
            if api_tmpl:
                self.render_code(code_dir, api_config['name'], api_tmpl.render(api_config))
            if api_ext_tmpl:
                self.render_code(code_dir, "%s_ext" % api_config['name'], api_ext_tmpl.render(api_config), False)
        else:
            logger.warning("Miss name info with api. {} {}".format(api_config.get('id'), api_config.get('title')))
        return api_config

    def set_index(self, api):
        inputs = api["inputs"]
        outputs = api["outputs"]
        input_params = [_input["name"] for _input in inputs]
        for _output in outputs:
            if _output["name"] in input_params and not _output.get("primary_key"):
                _output['index'] = True
        if len([i for i in api['outputs'] if 'primary_key' in i and i['primary_key']]) > 0:
            api['exist_primary_key'] = True

    def generate_order_by(self, api):
        """

        :param api:
        :return:
        """
        if not api.get('order_by'):
            order_cols = [output["name"] for output in api['outputs'] if output["name"] in ['trade_date', 'ts_code']]
            order_by = []
            if 'trade_date' in order_cols:
                order_by.append('trade_date desc')
            if 'ts_code' in order_cols:
                order_by.append('ts_code')
            api['order_by'] = ",".join(order_by)
        if len(api.get('order_by')) == 0:
            api['order_by'] = None

    def tushare_code_generate(self):
        code_dir = str(pathlib.PurePath(self.output_dir, "ts"))
        api_loader = JsonConfigApi(code_dir)
        apis = api_loader.get_ready_api()
        api_tmpl = self.env.get_template('tushare_api.tmpl')
        api_ext_tmpl = self.env.get_template('tushare_api_ext.tmpl')
        dao_tmpl = self.env.get_template('ts_api.tmpl')
        api_params = []
        for i in apis:
            api_params.append(self.generate_api_code(i, "tushare", "ts", api_tmpl, api_ext_tmpl))

        api_names = ['daily_basic', 'ggt_daily', 'ggt_top10', 'hsgt_top10', 'ggt_monthly', 'income_vip',
                     'balancesheet_vip',
                     'cashflow_vip', 'forecast_vip', 'express_vip', 'dividend', 'fina_indicator_vip', 'ths_daily',
                     'ths_member', 'anns', 'trade_cal', 'stock_vx', 'stock_mx']
        index_api = ['index_basic', 'index_daily', 'index_dailybasic', 'index_classify', 'index_member', 'ths_index',
                     'index_global', 'index_weekly', 'index_monthly', 'index_weight', 'daily_info', 'sz_daily_info',
                     'ths_daily', 'ths_member', 'ci_daily']
        fund_api = ['fund_adj', 'fund_company', 'fund_div', 'fund_manager', 'fund_nav', 'fund_portfolio',
                    'fund_sales_ratio', 'fund_sales_vol', 'fund_share', 'fund_daily']
        api_names.extend(fund_api)
        api_names.extend(index_api)
        for n in api_names:
            api = api_loader.get_api_by_name(n)
            if api:
                api_params.append(self.generate_api_code(api, "tushare", "ts", api_tmpl, api_ext_tmpl))
                apis.append(api)

        self.render_code(code_dir, "tushare_api", dao_tmpl.render({"apis": api_params}))

    def xueqiu_code_generate(self):
        package = "xq"
        code_dir = str(pathlib.PurePath(self.output_dir, package))
        api_loader = JsonConfigApi(code_dir)
        apis = api_loader.get_all()
        api_tmpl = self.env.get_template('xueqiu_api.tmpl')
        api_ext_tmpl = self.env.get_template('xueqiu_api_ext.tmpl')
        apis_tmpl = self.env.get_template('xq_api.tmpl')
        api_params = []
        for i in apis:
            api_params.append(self.generate_api_code(i, "xueqiu", package, api_tmpl, api_ext_tmpl))
        self.render_code(code_dir, "xueqiu_api", apis_tmpl.render({"apis": api_params}))


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    current_dir = file_dir(__file__)
    generator = CodeGenerator(pathlib.PurePath(current_dir, "tmpl"),
                              pathlib.PurePath(current_dir, "..", "api"))
    generator.tushare_code_generate()
    generator.xueqiu_code_generate()
    # print()
