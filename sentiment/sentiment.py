#encoding: utf8
import os
import re
from ctypes import *
import binascii
from bs4 import BeautifulSoup

def person_sentiment(dll, sTitle, sText, objs):
	model = open('sentiment/model.xml').read()
	objs = objs.replace('#','|')
	model = re.sub('<brandword>(.*?)</brandword>','<brandword>'+objs+'</brandword>', model)
	# print model
	f = open('sentiment/stConduct.xml','w+')
	f.write(model)
	f.close()
	# 特定人物情感分析
	# s = dll.ST_GetOneObjectResult(sTitle, sParagraph, sPerson)
	s = dll.ST_GetMultiObjectResult(sTitle, sText, "sentiment/stConduct.xml")
	s = cast(s, c_char_p)
	# print s.value
	soup = BeautifulSoup(s.value)
	r = soup.select('result')
	result = []
	for ro in r:
		dic = {
			'object':ro.select('object')[0].text,
			'polarity':float(ro.select('polarity')[0].text),
			'sentenceclue':ro.select('sentenceclue')[0].text.strip().split()
		}
		result.append(dic)

	# dll.ST_Exit()
	return result

if __name__ == '__main__':
	dll = CDLL('../dll/LJSentiment/LJSentiment.dll')
	# Data 文件夹的路径，为空字符串时默认从工程根目录下开始寻找
	sPath = c_char_p('../')
	# 编码格式，具体如下：0：GBK；1：UTF8；2：BIG5；3：GBK（里面包含繁体字）
	nEncoding = c_int(0)

	nRst = dll.ST_Init(sPath, nEncoding)
	if nRst==1:
		print  u'初始化成功' 
	else:
		print  u'初始化失败' 
		print dll.ST_GetLastErrMsg()
	sTitle = u'郭德纲需反思：观众如水，能载舟亦能覆舟'.encode('gbk')
	sText = u'''据《法制晚报》报道，警方已经证实1 月9 号在首都国际机场打人
的均是德云社员工，且德云社三名员工因打人被警方处以行政拘留并罚款。目前德云社已
申请行政复议，而郭德纲与“打人”字眼再次引起人们的热议。
德云社为什么会频频出现打人事件，这是一个让我们很难理解的事情。
在舞台上，郭德纲把自己的身段放的那么低，与观众是那样的亲，为什么一到舞台下面就
似乎完全是换了一个人呢?
郭德纲不在体制内，按他的话说自己就是一个“非著名相声演员”，而那些
在体质内的则统一被他戏称为“主流的”，而且在一切场合尽自己的最大的可能来讽刺和挖
苦这些所谓的“主流”相声演员。郭德纲成名，靠的不是哪个政府部门，靠的是自己坚持不
懈的努力，靠的是观众们的力捧，靠的是电视台网络的大力宣传。所以，他在唱经典段子
《大实话》的时候会一直唱“要说亲，观众们亲，观众演员心连着心!”'''.encode('gbk')
	objs = u'郭德纲#德云社'.encode('gbk')

	print person_sentiment(dll, sTitle, sText, objs)