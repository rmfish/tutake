"""
Tushare的Api列表，可用于生成自动化的接口
"""
import json

import requests
from sqlalchemy import create_engine, MetaData, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.utils.config import config

engine = create_engine("%s/%s" % (config['api']['driver_url'], 'tushare_meta.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)

Base = declarative_base()
metadata = MetaData(engine)


class TushareApi(Base):
    __tablename__ = "tushare_api"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    desc = Column(String)
    parent_id = Column(Integer)
    name = Column(String)
    inputs = Column(String)
    outputs = Column(String)
    validations = Column(String)
    database = Column(String)
    default_limit = Column(String)
    is_ready = Column(Integer)
    if_exists = Column(String)
    order_by = Column(String)
    code_prepare = Column(String)
    code_tushare_parameters = Column(String)
    code_param_loop_process = Column(String)

    def __init__(self, api_id, title, desc, parent_id):
        self.id = api_id
        self.title = title
        self.desc = desc
        self.parent_id = parent_id


TushareApi.__table__.create(bind=engine, checkfirst=True)


def add_new_api(session, api_id, title, desc, parent_id):
    """Adds a new api to the system"""
    # Get the author's first and last names
    # Check if book exists
    api = session.query(TushareApi).get(api_id)
    if api is not None:
        return
    api = TushareApi(api_id, title, desc, parent_id)
    session.add(api)

    # Commit to the database
    session.commit()


def update_api_detail(session, api_id, api_json):
    api = session.query(TushareApi).get(api_id)
    if api is None:
        return
    api.name = api_json['name']
    api.inputs = json.dumps(api_json['inputs'])
    api.outputs = json.dumps(api_json['outputs'])
    api.validations = json.dumps(api_json['validations'])
    session.add(api)
    session.commit()


def get_api_children(parent_id):
    apis = session_factory().query(TushareApi).filter_by(parent_id=parent_id).all()
    if apis:
        return [assemble_api(i) for i in apis]


def get_ready_api():
    apis = session_factory().query(TushareApi).filter_by(is_ready=1).all()
    if apis:
        return [assemble_api(i) for i in apis]


def get_api(api_id):
    api = session_factory().query(TushareApi).get(api_id)
    return assemble_api(api)


def assemble_api(api):
    if api is None:
        return None
    obj = api.__dict__
    if obj.get('inputs'):
        obj["inputs"] = json.loads(obj["inputs"])
    if obj.get('outputs'):
        obj["outputs"] = json.loads(obj["outputs"])
    if obj.get('validations'):
        obj["validations"] = json.loads(obj["validations"])
    if obj.get('_sa_instance_state'):
        del obj['_sa_instance_state']
    return obj


def get_api_path(api_id):
    api = session_factory().query(TushareApi).get(api_id)
    path = [(api.id, api.title)]
    while api.parent_id is not None:
        api = session_factory().query(TushareApi).get(api.parent_id)
        path.insert(0, (api.id, api.title))
    return path


def dump():
    cookie = config["api"]["cookie"]

    def save_api(apis, parent_id=None):
        for i in range(len(apis)):
            api = apis[i]
            api_id = api['id']
            add_new_api(session_factory(), api_id, api['title'], api["desc"], parent_id)
            api_detail = api_http(api_id, cookie)
            if len(api["children"]) == 0:
                print("Update api detail. id:{0} name:{1}".format(api_id, api['title']))
                if api_detail is not None:
                    update_api_detail(session_factory(), api_id, api_detail)
            save_api(api["children"], api_id)

    metabase = api_tree_http(cookie)
    save_api(metabase)


def api_http(api_id, cookie):
    return http_get("https://tushare.pro/wctapi/documents/{0}/api_info".format(api_id), cookie)


def api_tree_http(cookie):
    """
    从http接口中获取api的元数据
    """
    return http_get("https://tushare.pro/wctapi/documents/tree", cookie)


def http_get(url, cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Cookie': cookie
    }
    r = requests.get(url, timeout=10, headers=headers)
    return r.json()['data']
