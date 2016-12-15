import sys,json,ijson,requests,os
import datetime,pprint
import pandas as pd
import logging,logging.config
import numpy as np

max_api_pages=100000

LOGGING_CONFIG = {
	'version': 1, # required
	'disable_existing_loggers': True, # this config overrides all other loggers
	'formatters': {
		'simple': {
			'format': '%(asctime)s %(levelname)s -- %(message)s'
		},
		'whenAndWhere': {
			'format': '%(asctime)s\t%(levelname)s -- %(processName)s %(filename)s:%(lineno)s -- %(message)s'
		}
	},
	'handlers': {
		'console': {
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			'formatter': 'whenAndWhere'
		}
	},
	'loggers': {
		'': { # 'root' logger
#			 'level': 'CRITICAL',
#			 'level': 'WARN',
			'level': 'INFO',
			'handlers': ['console']
		}
	}
}

logging.config.dictConfig(LOGGING_CONFIG)
log = logging.getLogger('') # factory method
cache_path='./'
static_path='./'

def get_log():
	return log

def set_cache_path(path):
	global cache_path
	cache_path=path

def set_static_path(path):
	global static_path
	static_path=path

def rmfile_r(path):
	try:
		os.remove(path)
	except OSError as exc: # Python >2.5
		nodel=True

def get_dfincidents(filename):
	#read tariff rates from cache into df
	try:
		allcols=['Number','LineID','Open_Date','Downtime','Work_Notes','Closed_Date','Day','Hour','Shift','Minutes','Cause','Year','LessID']
		df=pd.read_csv(filename, sep='\t', encoding = "ISO-8859-1", names=allcols, usecols=allcols, skiprows=0, header=0, index_col=False)
		df['Open_Date']=pd.to_datetime(df['Open_Date'])
		#df['Closed_Date']=pd.to_datetime(df['Closed_Date'])
		return df
	except Exception as e:
		log.warning('Cannot open file %s' % filename)
		print(e)
		exit()
		return None

def run_prediction(upload_path='./',static_path='./'):
	dfincidents=get_dfincidents('%s/incidents.txt' % upload_path)
	dfout=pd.DataFrame(dfincidents['Cause'].unique(), columns=['Cause'])

	def prandom(p):
		return min(1.0,np.random.gamma(2,.1))
	def pstepup(p):
		return min(1.0,p*1.2)

	dfout['PFail_1day']=dfout['Cause'].apply(prandom)
	dfout['PFail_1week']=dfout['PFail_1day'].apply(pstepup)
	dfout['PFail_1month']=dfout['PFail_1week'].apply(pstepup)
	dfout.index.name='id'
	dfout.to_csv('%s/output.txt' % static_path, sep='|', index=True, header=True)

	#create json for REST API
	dfout['id']=dfout.index
	json_out=dfout.to_json(path_or_buf=None, orient='records', \
			 date_format='epoch', double_precision=6, force_ascii=True, date_unit='ms', default_handler=None)
	with open('%s/output.json' % static_path, 'w') as f:
		json.dump(json_out, f, sort_keys=False,separators=(',', ': '))

	return json_out

def get_output_json(filename):
	json_data=[]
	try:
		with open(filename) as f:
			json_data = json.load(f)
	except Exception as e:
		log.exception('Cannot open output json file %s' % filename)

	return json.loads(json_data)



