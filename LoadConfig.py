import yaml

configfile = open('config.yml', 'r')
CONFIG = yaml.load(configfile)
configfile.close()

PROXY = CONFIG.get('system').get('PROXY')
REQUEST_RETRIES = CONFIG.get('system').get('REQUEST_RETRIES')
ONCETIME_THREAD_POOL_SIZE = CONFIG.get('system').get('ONCETIME_THREAD_POOL_SIZE')
THREAD_POOL_SIZE = CONFIG.get('system').get('THREAD_POOL_SIZE')
TRYAGAIN_TIMES = CONFIG.get('system').get('TRYAGAIN_TIMES')
USERAGENT = CONFIG.get('system').get('USERAGENT')
LFLAG = CONFIG.get('system').get('LFLAG')
RFLAG = CONFIG.get('system').get('RFLAG')
SSL_VERIFY = CONFIG.get('system').get('SSL_VERIFY')
DEBUG = CONFIG.get('system').get('DEBUG')

CAPTCHA_REGEX = CONFIG.get('ocr').get('CAPTCHA_REGEX')
CAPTCHA_REGEX_GETVALUE_INDEX = CONFIG.get('ocr').get('CAPTCHA_REGEX_GETVALUE_INDEX')

CAPTCHA_REQUEST_FILENAME = CONFIG.get('target').get('CAPTCHA')
CAPTCHA_DATATYPE = CONFIG.get('target').get('CAPTCHA_DATATYPE')
CAPTCHA_LENGTH = CONFIG.get('target').get('CAPTCHA_LENGTH')
CAPTCHA_CUSTOM_GETFLAG = CONFIG.get('target').get('CAPTCHA_CUSTOM_GETFLAG')
BLAST_REQUEST_FILENAME = CONFIG.get('target').get('BLAST')
CAPTCHA_INDEX = CONFIG.get('target').get('CAPTCHA_INDEX')
CAPTCHA_ID_GETFLAG = CONFIG.get('target').get('CAPTCHA_ID_GETFLAG')
CAPTCHA_ID_INDEX = CONFIG.get('target').get('CAPTCHA_ID_INDEX')
WORDDICT_LIST = CONFIG.get('target').get('WORDDICT_LIST')
SSL = CONFIG.get('target').get('SSL')
CAPTCHA_ERROR_FLAG = CONFIG.get('target').get('CAPTCHA_ERROR_FLAG')
CAPTCHA_ERROR_CODE = CONFIG.get('target').get('CAPTCHA_ERROR_CODE')
LOGIN_ERROR_FLAG = CONFIG.get('target').get('LOGIN_ERROR_FLAG')
LOGIN_ERROR_CODE = CONFIG.get('target').get('LOGIN_ERROR_CODE')
LOGIN_SUCCESS_FLAG = CONFIG.get('target').get('LOGIN_SUCCESS_FLAG')
LOGIN_SUCCESS_CODE = CONFIG.get('target').get('LOGIN_SUCCESS_CODE')