import json
import logging
import os

import jinja2
import pendulum
from yapf.yapflib.yapf_api import FormatCode

from tutake.code.tushare_api import TushareJsonApi
# from tutake.code.tushare_api import get_api, get_api_path, get_ready_api, get_all_leaf_api
from tutake.utils.file_utils import file_dir, realpath

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
    raise Exception('Unsupport type {}'.format(type))


class CodeGenerator(object):

    def __init__(self, tmpl_dir, output_dir):
        loader = jinja2.FileSystemLoader(tmpl_dir)
        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters['get_sql_type'] = get_sql_type
        env.globals['now'] = pendulum.now().format("YYYY/MM/DD")
        self.env = env
        self.output_dir = output_dir
        self.api_loader = TushareJsonApi()

    def render_code(self, file_name: str, code: str, overwrite: bool = True, file_suffix: str = 'py'):
        file_path = "{}/{}.{}".format(self.output_dir, file_name, file_suffix)
        if os.path.exists(file_path) and not overwrite:
            # 如果文件存在，且设置不覆盖，就直接退出
            return

        with open(file_path, 'w') as file:
            try:
                formatted, changed = FormatCode(code, style_config='setup.cfg')
                file.write(formatted)
            except Exception as err:
                file.write(code)
                logger.error("Exp in render code {} {}".format(file_name, err))

    def _load_api_config(self, api):
        config_file = "%s/config/%s.json" % (self.output_dir, api['name'])
        if os.path.exists(config_file):
            f = open(config_file)
            data = json.load(f)
            return {**api, **data}
        else:
            return api

    def generate_api_code(self, api_id):
        api_tmpl = self.env.get_template('tushare_api.tmpl')
        api_ext_tmpl = self.env.get_template('tushare_api_ext.tmpl')
        api_config = self._load_api_config(self.api_loader.get_api(api_id))
        if api_config.get('name'):
            print("Render code {} {}.py".format(api_id, api_config.get('name')))
            api_config['path'] = '-'.join(tups[1] for tups in api_config['path'])
            api_config['table_name'] = "tushare_{}".format(api_config.get("name"))
            if not api_config.get('if_exists'):
                api_config['if_exists'] = 'append'
            if not api_config.get('database'):
                api_config['database'] = 'tushare_%s' % api_config['name']
            if not api_config.get('default_limit'):
                api_config['default_limit'] = ""

            api_config['title_name'] = "{}".format(api_config['name'].replace('_', ' ').title().replace(' ', ''))
            api_config['entity_name'] = "Tushare{}".format(api_config['title_name'])

            self.set_index(api_config)
            self.generate_order_by(api_config)
            self.render_code(api_config['name'], api_tmpl.render(api_config))
            self.render_code("extends/%s_ext" % api_config['name'], api_ext_tmpl.render(api_config), False)
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

    def generate_dao_code(self, apis):
        tmpl = self.env.get_template('dao.tmpl')
        self.render_code("dao", tmpl.render({"apis": apis}))

    def _generate_config_code(self, apis):
        for api in apis:
            api['database'] = None
            api['default_limit'] = None
            api['order_by'] = None
            print("Generate config %s.json" % api['name'])
            self.render_code("config/%s" % api['name'], json.dumps(api, indent=4, ensure_ascii=False),
                             False, file_suffix='json')

    def generate_config(self):
        leaf_apis = self.api_loader.get_all_leaf_api()
        self._generate_config_code(leaf_apis)

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


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    current_dir = file_dir(__file__)
    tmpl_dir = "{}/tmpl".format(current_dir)
    api_dir = realpath("{}/../api/tushare".format(current_dir))

    generator = CodeGenerator(tmpl_dir, api_dir)
    api_params = []

    apis = generator.api_loader.get_ready_api()
    for i in apis:
        api_params.append(generator.generate_api_code(i['id']))

    # parent_id = [15, 24]
    # for api_id in parent_id:
    #     apis = get_api_children(api_id)
    #     for i in apis:
    #         api_params.append(generator.generate_api_code(i['id']))

    api_names = ['ggt_daily', 'ggt_top10', 'hsgt_top10', 'ggt_monthly', 'income_vip', 'balancesheet_vip',
                 'cashflow_vip', 'forecast_vip', 'express_vip', 'dividend',
                 'fina_indicator_vip', 'index_daily', 'index_dailybasic', 'index_classify', 'index_member', 'ths_index',
                 'ths_daily', 'ths_member', 'index_global', 'anns']
    for n in api_names:
        api = generator.api_loader.get_api_by_name(n)
        if api:
            api_params.append(generator.generate_api_code(api['id']))

    api_ids = [94]
    for i in api_ids:
        api_params.append(generator.generate_api_code(i))

    generator.generate_dao_code(api_params)
