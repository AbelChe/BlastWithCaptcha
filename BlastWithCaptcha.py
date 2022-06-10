import base64
import copy
import datetime
import io
import itertools
import pkgutil
import re
import sys
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait

import ddddocr
import requests
from PIL import Image
from requests_toolbelt.multipart.encoder import MultipartEncoder

from LoadConfig import (BLAST_REQUEST_FILENAME, CAPTCHA_CUSTOM_GETFLAG,
                        CAPTCHA_DATATYPE, CAPTCHA_ERROR_CODE,
                        CAPTCHA_ERROR_FLAG, CAPTCHA_INDEX, CAPTCHA_REGEX,
                        CAPTCHA_REGEX_GETVALUE_INDEX, CAPTCHA_REQUEST_FILENAME,
                        LFLAG, LOGIN_ERROR_CODE, LOGIN_ERROR_FLAG,
                        LOGIN_SUCCESS_CODE, LOGIN_SUCCESS_FLAG,
                        ONCETIME_THREAD_POOL_SIZE, PROXY, REQUEST_RETRIES,
                        RFLAG, SSL, SSL_VERIFY, THREAD_POOL_SIZE,
                        TRYAGAIN_TIMES, USERAGENT, WORDDICT_LIST)
from log import Logging
from ParseBurpRequest import ParseBurpRequest

print('Please use python version >=3.6') if sys.version_info.major < 3 or sys.version_info.minor < 6 else "PASS"


# import imgcat


log = Logging.getLogger(__name__)

requests.DEFAULT_RETRIES = REQUEST_RETRIES

REQUEST_HEADER = {
    'User-Agent': USERAGENT
}

REQUEST_PROXY = {'http': f'http://{PROXY}',
                 'https': f'https://{PROXY}'} if PROXY else None


def regexGenter(data):
    return data.replace('*', '\*').replace('.', '\.').replace('?', '\?').replace('+', '\+').replace('$', '\$').replace('^', '\^').replace('[', '\[').replace(']', '\]').replace('(', '\(').replace(')', '\)').replace('{', '\{').replace('}', '\}').replace('|', '\|').replace('\\', '\\\\').replace('/', '\/')


class CaptchaKiller:
    def __init__(self, captcha_ParseBurpRequest, blast_ParseBurpRequest) -> None:
        self.CAPTCHA_REGEX = CAPTCHA_REGEX
        self.CAPTCHA_REGEX_GETVALUE_INDEX = CAPTCHA_REGEX_GETVALUE_INDEX
        self.CAPTCHA_ParseBurpRequest = captcha_ParseBurpRequest
        self.BLAST_ParseBurpRequest = blast_ParseBurpRequest
        self.SSL = SSL
        self.BLAST_ParseBurpRequest.rmCookie()
        self.REQUEST_HEADER = self.BLAST_ParseBurpRequest.headers
        self.Session = requests.session()
        self.Session.keep_alive = False
        self.Session.proxies = REQUEST_PROXY
        self.Session.verify = SSL_VERIFY

    def _stateController(self, r):
        try:
            for _ in CAPTCHA_ERROR_FLAG:
                if re.findall(_, r.text):
                    return -1
            if r.status_code in CAPTCHA_ERROR_CODE:
                return -1
            for _ in LOGIN_ERROR_FLAG:
                if re.findall(_, r.text):
                    return 0
            if r.status_code in LOGIN_ERROR_CODE:
                return 0
            for _ in LOGIN_SUCCESS_FLAG:
                if re.findall(_, r.text):
                    return 1
            if r.status_code in LOGIN_SUCCESS_CODE:
                return 1
        except Exception as e:
            log.error(e)

    def _identifyCaptcha(self, imagebytes):
        try:
            ocr = ddddocr.DdddOcr(show_ad=False)
            res = ocr.classification(imagebytes)
            return re.findall(self.CAPTCHA_REGEX, res)[self.CAPTCHA_REGEX_GETVALUE_INDEX-1]
        except Exception as e:
            log.error(e, 'ocr result:', res)
            return res

    def _getCaptcha(self):
        try:
            img = self.Session.request(
                method=self.CAPTCHA_ParseBurpRequest.request_method,
                url=self.CAPTCHA_ParseBurpRequest.getURL(ssl=self.SSL),
                headers=self.REQUEST_HEADER,
                proxies=REQUEST_PROXY
            )
            img_btyes = b''
            if CAPTCHA_DATATYPE.lower() == 'raw':
                img_btyes = img.content
            elif CAPTCHA_DATATYPE.lower() == 'base64':
                img_btyes = base64.b64decode(img.text)
            elif CAPTCHA_DATATYPE.lower() == 'custom':
                img_b64 = re.findall(CAPTCHA_CUSTOM_GETFLAG, img.text)[0]
                img_btyes = base64.b64decode(img_b64)
            try:
                image = Image.open(io.BytesIO(img_btyes))
                image.verify()
                image.close()
            except Exception as e:
                log.error(e)
                return None
            # imgcat.imgcat(img.content)
            return self._identifyCaptcha(img.content)
        except Exception as e:
            log.error(e)

    def payloadGenerator(self, params: list):
        try:
            payload = {
                'params': None,
                'json': None,
                'data': None,
            }
            # {'params': {}},
            # {'json':   {}},
            # {'form':   {}},
            # {'multipart': <MultipartEncoder>},
            # {'plaintext': ''},
            # ......
            if self.BLAST_ParseBurpRequest.params:
                # params
                tmp_params = copy.deepcopy(self.BLAST_ParseBurpRequest.params)
                for k in self.BLAST_ParseBurpRequest.params.keys():
                    if self.BLAST_ParseBurpRequest.params[k].startswith(LFLAG) and self.BLAST_ParseBurpRequest.params[k].endswith(RFLAG):
                        this_payload_index = int(tmp_params[k].replace(
                            LFLAG, '').replace(RFLAG, '')) - 1
                        tmp_params[k] = params[this_payload_index]
                payload['params'] = tmp_params
            if self.BLAST_ParseBurpRequest.jsondata:
                # json
                tmp_jsondata = copy.deepcopy(
                    self.BLAST_ParseBurpRequest.jsondata)
                for k in self.BLAST_ParseBurpRequest.jsondata.keys():
                    if self.BLAST_ParseBurpRequest.jsondata[k].startswith(LFLAG) and self.BLAST_ParseBurpRequest.jsondata[k].endswith(RFLAG):
                        this_payload_index = int(tmp_jsondata[k].replace(
                            LFLAG, '').replace(RFLAG, '')) - 1
                        tmp_jsondata[k] = params[this_payload_index]
                payload['json'] = tmp_jsondata
            elif self.BLAST_ParseBurpRequest.data:
                # form, multipart, plaintext
                if self.BLAST_ParseBurpRequest.data.__class__ == dict:
                    # form
                    tmp_data = copy.deepcopy(self.BLAST_ParseBurpRequest.data)
                    for k in self.BLAST_ParseBurpRequest.data.keys():
                        if self.BLAST_ParseBurpRequest.data[k].startswith(LFLAG) and self.BLAST_ParseBurpRequest.data[k].endswith(RFLAG):
                            this_payload_index = int(tmp_data[k].replace(
                                LFLAG, '').replace(RFLAG, '')) - 1
                            tmp_data[k] = params[this_payload_index]
                    payload['data'] = tmp_data
                elif self.BLAST_ParseBurpRequest.data.__class__ == MultipartEncoder:
                    # multipart
                    tmp_data = copy.deepcopy(self.BLAST_ParseBurpRequest.data)
                    for k in self.BLAST_ParseBurpRequest.data.fields.keys():
                        if self.BLAST_ParseBurpRequest.data.fields[k].__class__ == tuple:
                            # exclude file field
                            continue
                        if self.BLAST_ParseBurpRequest.data.fields[k].startswith(LFLAG) and self.BLAST_ParseBurpRequest.data.fields[k].endswith(RFLAG):
                            this_payload_index = int(tmp_data.fields[k].replace(
                                LFLAG, '').replace(RFLAG, '')) - 1
                            tmp_data.fields[k] = params[this_payload_index]
                    payload['data'] = tmp_data
                elif self.BLAST_ParseBurpRequest.data.__class__ == str:
                    # plaintext
                    tmp_data = copy.deepcopy(self.BLAST_ParseBurpRequest.data)
                    rerule = regexGenter(LFLAG) + '(\d+)' + regexGenter(RFLAG)
                    payload_index_list = re.findall(rerule, tmp_data)
                    for this_payload_index in payload_index_list:
                        tmp_data = tmp_data.replace(
                            LFLAG+this_payload_index+RFLAG, params[int(this_payload_index) - 1])
                    payload['data'] = tmp_data
            return payload
        except Exception as e:
            log.error(e, 'Payload error, pass...')
            return None

    def doRequest(self, params, againflag=0):
        """start request

        Args:
            u: username
            p: password
            againflag: tryagain times
        Returns:
            None
        Raises:

        """
        try:
            c = self._getCaptcha()
            if not c:
                print(f'Captcha error... Try again...')
                self.doRequest(params, againflag)
            _params = params
            params = list(params)
            params.insert(CAPTCHA_INDEX, c)
            params = [i.rstrip() for i in params]
            payload = self.payloadGenerator(params)
            r = self.Session.request(
                method=self.BLAST_ParseBurpRequest.request_method,
                url=self.BLAST_ParseBurpRequest.getURL(ssl=self.SSL),
                params=payload.get('params'),
                data=payload.get('data'),
                json=payload.get('json'),
                headers=self.REQUEST_HEADER,
                proxies=REQUEST_PROXY
            )
            state = self._stateController(r)
            if state == 1:
                print(f'[*] FIND {params} captcha: {c}')
                f = open('BlastWithCaptchaResult.txt', 'a+')
                f.write(
                    f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]\t{params} captcha: {c}\n')
            elif state == 0:
                print(f'Login Failed... {params} captcha: {c}')
            elif state == -1:
                print(f'Try Again {params} captcha: {c}')
                if againflag < TRYAGAIN_TIMES:
                    self.doRequest(_params, againflag+1)
        except Exception as e:
            log.error(e)


def loadDict():
    def payloadPlugin(plugin_name, data: list, args):
        payload_list = []
        for i in data:
            payload_list.append(getattr(__import__(f'plugins.{plugin_name}'), plugin_name).PayloadProcessor(payload=i, args=args).genterPatload())
        return payload_list

    try:
        worddict_list = []
        for i in WORDDICT_LIST:
            lines = []
            # i: ['/Users/AbelChe/SecTools/worddicts/Blasting_dictionary/top100password.txt', 'base64']
            f = open(i.get('file'), 'r')
            payload_list = [_.rstrip() for _ in f.readlines()]
            if i.get('plugin'):
                for p in i.get('plugin'):
                    payload_list = payloadPlugin(p[0], payload_list, p[1:])
                worddict_list.append(payload_list)
            else:
                worddict_list.append(payload_list)
        return worddict_list
    except Exception as e:
        log.error(e)


def run():
    def cal_cartesian_coord(values):
        cart = [d for d in itertools.product(*values)]
        return cart
    # parse captcha requests

    cp = ParseBurpRequest(CAPTCHA_REQUEST_FILENAME)
    bp = ParseBurpRequest(BLAST_REQUEST_FILENAME)
    worddict_list = loadDict()
    word_list = cal_cartesian_coord(worddict_list)
    total = len(word_list)
    tasklist = []
    t = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)
    this_task_num = 0
    for k, v in enumerate(word_list):
        this_task_num += 1
        if this_task_num % ONCETIME_THREAD_POOL_SIZE != 0:
            C = CaptchaKiller(captcha_ParseBurpRequest=cp,
                              blast_ParseBurpRequest=bp)
            tasklist.append(t.submit(C.doRequest, v))
        else:
            if wait(tasklist, return_when=ALL_COMPLETED):
                percent = "%.4f" % ((this_task_num/total)*100)
                print(f'[{this_task_num}/{total} {percent}%] DONE')
            tasklist = []


if __name__ == '__main__':
    run()
