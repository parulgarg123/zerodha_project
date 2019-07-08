# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 01:11:00 2019

@author: beast
"""

import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
import redis
import pandas as pd

conf_path = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(conf_path), trim_blocks=True)
conf_path = os.path.join(conf_path, "myconf.conf")
cherrypy.config.update(conf_path)

r = redis.Redis(host='localhost',  port=6379,  db=0)


def get_Keys():
    ll = r.keys('*')
    for i in range(0, len(ll)):
        xx = ll[i].decode()
        ll[i] = str(xx)
    ll.sort()
    ls = list()
    for i in ll:
        ls.append(r.hgetall(i))
    df = pd.DataFrame(ls)
    df = df.stack().str.decode('utf-8').unstack()
    df.columns = ['close', 'code', 'high', 'low', 'name', 'open']
    df = df[['code', 'name', 'open', 'high', 'low', 'close']]
    df.index = df['name']
    return df


class main(object):
    @cherrypy.expose
    def index(self, **kwargs):
        print(cherrypy.request.method)
        if cherrypy.request.method == 'GET':
            template = env.get_template('media/dashboard.html')
            return template.render(title=get_Keys().head(10).values.tolist())
        else:
            template = env.get_template('media/dashboard.html')
            # print(kwargs['searchbar'].upper())
            key = kwargs['searchbar'].upper()
            # print(type(key))
            try:
                df = get_Keys()
                df = df.filter(like=key, axis=0)
                if len(df) > 0:
                    return template.render(title=df.values.tolist())
                else:
                    return template.render(title="None")
                # return ()
            except Exception as e:
                template = env.get_template('media/dashboard.html')
                return template.render(title=get_Keys().head(10).values.tolist(
                ))
                
# cherrypy.quickstart(main(), '/', {
#     '/media': {
#         'tools.staticdir.on': True,
#         'tools.staticdir.dir': 'static'
#     }
# })
cherrypy.quickstart(main(), '/')
