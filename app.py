#coding=utf-8
import urllib
import urllib2
import json
import sys
import time  
import uuid
import logging  
import logging.handlers 


reload(sys)
sys.setdefaultencoding('utf8')

LOG_FILE = 'task.log'
__config = {};
'''
订单配置
'''
__config['order_get'] = {}
__config['order_get']['type'] = 'get'
__config['order_get']['url'] = 'http://kd.xxx.com/print?restaurant=1'

__config['order_post'] = {}
__config['order_post']['type'] = 'post'
__config['order_post']['url'] = 'http://kd.xiaolinyx.com/print'
__config['order_post']['params'] = {
	'restaurant': 1,
	'table_id': 10
}

'''
打印配置
'''
__config['print'] = {}
__config['print']['type'] = 'post'
__config['print']['url'] = 'http://app.liugm.com/api/i_printer/msg'
__config['print']['params'] = {
	'token': 'fymXzSymNQyzkWUgV'
}

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler   
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  

formatter = logging.Formatter(fmt)    
handler.setFormatter(formatter)   

logger = logging.getLogger('TASK')  
logger.addHandler(handler)         
logger.setLevel(logging.DEBUG)  

'''
请求发送
'''
def request(config={}):
	if config['type'] != 'post':
		res = urllib2.urlopen(config['url'])
		resData = json.load(res)
		return resData
	else:
		print config
		req = urllib2.Request(url = config['url'], data=urllib.urlencode(config['params']))
		res_data = urllib2.urlopen(req)
		resData = json.load(res_data)
		return resData
'''
订单信息打印
'''
def printOrderDetail():
	__uuid = uuid.uuid1()
	# 获取订单信息
	orders_res = request(__config['order_get'])
	status = orders_res['status']

	if status['code'] != 200:
		logger.error('[ORDER_GET]', __uuid, __config['order_get'], orders_res)
		return 

	orders_data = orders_res['data']
	# 日志
	logger.info('[ORDER_GET]', __uuid, __config['order_get'], orders_data)

	# 根据桌分组
	orderMaps = {}
	for item in orders_data:
		tableId = item['table_id']
		isFirst = orderMaps.has_key(tableId);
		if isFirst:
			orderMaps[tableId].append(item)
		else:
			orderMaps[tableId] = []
			orderMaps[tableId].append(item)

	logger.info('[ORDER_MAPS]', __uuid, orderMaps)

	# 打印
	for key in orderMaps:
		header = '\r\n=======================\r\n'
		body = ''
		for order in orderMaps[key]:
			body += u'%s %s %s \r\n'%(order['food_name'], order['number'], order['remark'])

		
		__config['order_post']['params']['table_id'] = key;
		__config['print']['params']['msg'] = header + body;
		print_res = request(__config['print'])
		logger.info('[PRINT]', __uuid, __config['print'], print_res)

		orders_res = request(__config['order_post'])
		status = orders_res['status']
		if status['code'] == 200:
			logger.info('[UPDATE_STATUS]', __uuid, __config['order_post'], orders_res)./
			return
		else:
			logger.error('[UPDATE_STATUS]', __uuid, __config['order_post'], orders_res)

	logger.info('[DONE]', __uuid)

def task(n):  
    ''''' 
    每n秒执行一次 
    '''  
    while True:    
        logger.info('[START]', time.strftime('%Y-%m-%d %X',time.localtime()))
        printOrderDetail()     
        time.sleep(n)  
# 执行
task(3)



