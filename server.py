import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
from pymongo import MongoClient

class IndexPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

    def post(self):
        host_addr = self.get_body_argument('host') or 'localhost'
        host_port = self.get_body_argument('port') or 27017
        db_name = self.get_body_argument('dbname')
        client = MongoClient(host_addr, host_port)
        database = client[db_name]
        collections = database.collection_names()
        sql_string = 'CREATE DATABASE {}; USE {};'.format(db_name, db_name)
        tables = []

        for collection in collections:
            documents = database[collection].find()

            for document in documents:
                keys = document.keys()

                if collection not in tables:
                    tables.append(collection)
                    sql_string = '{} CREATE TABLE {} ('.format(sql_string, collection)

                    for key in keys:
                        if key == '_id':
                            sql_string = '{} {} varchar (100),'.format(sql_string, key)
                        else:
                            sql_string = '{} {} varchar (255),'.format(sql_string, key)

                    sql_string = '{} PRIMARY KEY (_id) );'.format(sql_string)

                sql_string = '{} INSERT INTO {} VALUES ('.format(sql_string, collection)

                for count, key in enumerate(keys):
                    if type(document[key]) is list:
                        value = ', '.join(document[key])
                    else:
                        value = document[key]

                    if count == len(keys) - 1:
                        sql_string = '{} \'{}\''.format(sql_string, value)
                    else:
                        sql_string = '{} \'{}\','.format(sql_string, value)

                sql_string = '{} );'.format(sql_string)

        self.render('result.html', sql=sql_string)

class ResultPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('result.html')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexPageHandler),
            (r'/result', ResultPageHandler)
        ]

        settings = {
            'debug': True,
            'template_path': 'templates',
            'static_path': 'static'
        }

        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == '__main__':
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
