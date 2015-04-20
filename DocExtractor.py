#encoding: utf8
from ctypes import *
import binascii

class _tDocExtractResult(Structure):
	_fields_ = [
		('entity_list', (c_char * 251) * 9),
		('sentiment_score', c_int),
	]

def DocExtract(dll, sParagraph):
	# sParagraph = u'中共中央政治局委员、中宣部部长刘奇葆陪同看望。中宣部、教育部、文化部、新闻出版广电总局、中国文联、中国作协有关负责同志参加看望活动。'.encode('gbk')
	# 文档内容
	sText = c_char_p(sParagraph)
	result = _tDocExtractResult()

	# 文档抽取 
	dll.DE_ParseDoc(sText, byref(result))
	r = []
	for i in range(9):
		r.append(binascii.unhexlify(binascii.hexlify(result.entity_list[i]).replace('00', '')).decode('gbk'))
	r.append(result.sentiment_score)
	return r
	# for i in range(9):
	# 	print binascii.hexlify(result.entity_list[i])
	# dll.DE_Exit()

if __name__ == '__main__':
	dll = CDLL('dll/DocExtractor/DocExtractor.dll')
	# Data 文件夹的路径，为空字符串时默认从工程根目录下开始寻找
	sPath = c_char_p('')
	# 编码格式，具体如下：0：GBK；1：UTF8；2：BIG5；3：GBK（里面包含繁体字）
	nEncoding = c_int(0)

	nRst = dll.DE_Init(sPath, nEncoding,'')
	if nRst==1:
		print  u'初始化成功' 
		dll = CDLL('dll/DocExtractor/DocExtractor.dll')
		sParagraph = u'中共中央政治局委员、中宣部部长刘奇葆陪同看望。中宣部、教育部、文化部、新闻出版广电总局、中国文联、中国作协有关负责同志参加看望活动。'.encode('gbk')
		result = DocExtract(dll, sParagraph)
		for i in range(len(result)):
			print i, result[i]