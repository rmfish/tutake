import logging

import jinja2
from yapf.yapflib.yapf_api import FormatCode

from tutake.code.TushareApi import get_api, get_api_path, get_api_children
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
    raise Exception('Unsupport type'.format(type))


class CodeGenerator(object):

    def __init__(self, tmpl_dir, output_dir):
        loader = jinja2.FileSystemLoader(tmpl_dir)
        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters['get_sql_type'] = get_sql_type
        self.env = env
        self.output_dir = output_dir

    def render_code(self, file_name, code):
        with open("{}/{}.py".format(self.output_dir, file_name), 'w') as file:
            try:
                formatted, changed = FormatCode(code,style_config='setup.cfg')
                file.write(formatted)
            except Exception as err:
                file.write(code)
                logger.error("Exp in render code {} {}".format(file_name, err))

    def generate_api_code(self, api_id):
        temp = self.env.get_template('api_replace.tmpl')
        api = get_api(api_id)
        if api.get('name'):
            print("Render code {} {}.py".format(api_id, api.get('name')))
            api['path'] = '-'.join(tups[1] for tups in get_api_path(api_id))
            api['table_name'] = "tushare_{}".format(api.get("name"))
            if not api.get('if_exists'):
                api['if_exists'] = 'append'
            if not api.get('database'):
                api['database'] = 'tushare_%s' % api['name']
            if not api.get('default_limit'):
                api['default_limit'] = ""
            if len([i for i in api['outputs'] if 'primary_key' in i and i['primary_key']]) > 0:
                api['exist_primary_key'] = True

            api['title_name'] = "{}".format(api['name'].replace('_', ' ').title().replace(' ', ''))
            api['entity_name'] = "Tushare{}".format(api['title_name'])

            self.generate_order_by(api)
            self.generate_prepare(api)
            self.generate_tushare_parameters(api)
            self.generate_param_loop_process(api)
            self.render_code(api['name'], temp.render(api))
        else:
            logger.warning("Miss name info with api. {} {}".format(api.get('id'), api.get('title')))
        return api

    def generate_dao_code(self, apis):
        tmpl = self.env.get_template('dao.tmpl')
        self.render_code("dao", tmpl.render({"apis": apis}))

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

    def generate_prepare(self, api):
        """
        生成prepare代码块
        :param api:
        :return:
        """
        code_prepare = api.get('code_prepare')
        if code_prepare:
            if code_prepare == 'deleteAll()':
                api['prepare_code'] = '''logger.warning("Delete all data of {}")
        self.delete_all()'''

    def generate_tushare_parameters(self, api):
        """
        生成parameters代码
        :param api:
        :return:
        """
        code_tushare_parameters = api.get('code_tushare_parameters')
        if code_tushare_parameters:
            api['tushare_parameters_code'] = code_tushare_parameters
        else:
            api['tushare_parameters_code'] = "return [{}]"

    def generate_param_loop_process(self, api):
        code_param_loop_process = api.get('code_param_loop_process')
        if code_param_loop_process:
            api['param_loop_process_code'] = code_param_loop_process
        else:
            api['param_loop_process_code'] = "return params"


if __name__ == '__main__':
    current_dir = file_dir(__file__)
    tmpl_dir = "{}/tmpl".format(current_dir)
    api_dir = realpath("{}/../api".format(current_dir))

    generator = CodeGenerator(tmpl_dir, api_dir)
    api_ids = [94]
    parent_id = [15, 24]
    api_params = []
    for api_id in parent_id:
        apis = get_api_children(api_id)
        for i in apis:
            api_params.append(generator.generate_api_code(i['id']))
    for i in api_ids:
        api_params.append(generator.generate_api_code(i))
    generator.generate_dao_code(api_params)

    # for i in api_id:
    #     render_api(i, dir, output)
