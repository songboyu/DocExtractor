# -*- coding: utf-8 -*-
'''
@author: HSS
@modify: 2015-4-14
@summary: 文本分析模块----Tonardo服务端
'''
import re
import json
import time
import datetime

import concurrent
import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.concurrent
import tornado.httpclient

from DocExtractor import *
from sentiment.sentiment import *

dll0 = None
dll1 = None

class DocExtractHandler(tornado.web.RequestHandler):
    executor = concurrent.futures.ThreadPoolExecutor(16)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        result = yield self._parse(self.request.arguments)
        self.write(json.dumps(result))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _parse(self,params):
        result = {}
        try:
            text = params['text'][0].decode('utf8','ignore').encode('gbk','ignore').strip()
            # text = re.sub(r'\s','', text)
            t = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            print '---------------'
            print t,text[0:50]+'...'

            startTime = datetime.datetime.now()

            r = DocExtract(dll0, text)
            r[8] = r[8].strip()
            endTime = datetime.datetime.now()
            # print r[5]
            r[5] = re.sub(r'/.*?#','#',r[5])
            t = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            print t+' score:'+str(r[9])+' time:'+str((endTime - startTime).seconds)+'s'

            result['code'] = 1
            result['msg'] = 'sucess'
            result['result'] = r

        except Exception as e:
            result = {
                'code':0,
                'msg':'error',
                'result':[]
            }
            print e
        return result

class MultiObjsSentimentHandler(tornado.web.RequestHandler):
    executor = concurrent.futures.ThreadPoolExecutor(16)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        result = yield self._parse(self.request.arguments)
        self.write(json.dumps(result))
        self.finish()

    @tornado.concurrent.run_on_executor
    def _parse(self,params):
        result = {}
        try:
            sTitle = params['title'][0].decode('utf8','ignore').encode('gbk','ignore').strip()
            sText = params['text'][0].decode('utf8','ignore').encode('gbk','ignore').strip()
            objs = params['objs'][0].decode('utf8','ignore').encode('gbk','ignore').strip()
            # text = re.sub(r'\s','', text)
            t = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            print '---------------'
            print t,'multi objs',objs

            startTime = datetime.datetime.now()

            r = person_sentiment(dll1, sTitle, sText, objs)

            endTime = datetime.datetime.now()

            t = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            print t+' time:'+str((endTime - startTime).seconds)+'s'
            result['code'] = 1
            result['msg'] = 'sucess'
            result['result'] = r

        except Exception as e:
            result = {
                'code':0,
                'msg':'error',
                'result':[]
            }
            print e
        return result

if __name__ == '__main__':
    dll0 = CDLL('dll/DocExtractor/DocExtractor.dll')
    dll1 = CDLL('dll/LJSentiment/LJSentiment.dll')
    # Data 文件夹的路径，为空字符串时默认从工程根目录下开始寻找
    sPath = c_char_p('')
    # 编码格式，具体如下：0：GBK；1：UTF8；2：BIG5；3：GBK（里面包含繁体字）
    nEncoding = c_int(0)

    nRst = dll0.DE_Init(sPath, nEncoding)
    if nRst==1:
        print  u'DocExtractor.dll 初始化成功' 
        nRst = dll1.ST_Init(sPath, nEncoding)
        if nRst==1:
            print  u'LJSentiment.dll 初始化成功' 
            application = tornado.web.Application([
                (r'/sentiment/common', DocExtractHandler),
                (r'/sentiment/multi_objs', MultiObjsSentimentHandler)
            ])
            application.listen(7777)
            tornado.ioloop.IOLoop.instance().start()
        else:
            print u'LJSentiment.dll 初始化失败' 
            print dll.ST_GetLastErrMsg()
    else:
        print  u'DocExtractor.dll 初始化失败' 
        print dll.DE_GetLastErrMsg()
    