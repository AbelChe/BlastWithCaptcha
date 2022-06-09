import json
import sys

from requests_toolbelt.multipart.encoder import MultipartEncoder

from log import Logging

print('Please use python version >=3.7') if sys.version_info.major < 3 or sys.version_info.minor < 7 else "PASS"


log = Logging.getLogger(__name__)


class ParseBurpRequest:
    def __init__(self, filename):
        self.filename = filename
        if sys.platform == 'win32':
            self.OS_Line_Separator = '\r\n'
        else:
            self.OS_Line_Separator = '\n'
        self.headers = {}
        self.request_method = ''
        self.data = None
        self.jsondata = {}
        self.params = {}
        self.host = ''
        self.path = ''
        self.content_type = ''

        self._parse()

    def getCookies(self):
        try:
            c = self.headers.get('Cookie').replace(' ', '')
            return dict([i.split('=') for i in c.split(';')])
        except Exception as e:
            log.error(e)

    def setCookie(self, key, value):
        try:
            c = self.getCookies()
            c[key] = value
            self.headers['Cookie'] = '; '.join(
                ['{}:{}'.format(k, c[k]) for k in c])
        except Exception as e:
            log.error(e)

    def rmCookie(self):
        try:
            if self.headers.get('Cookie'):
                self.headers.pop('Cookie')
        except Exception as e:
            log.error(e)

    def getURL(self, ssl=False):
        try:
            scheme = 'https' if ssl else 'http'
            return f'{scheme}://{self.host}{self.path}'
        except Exception as e:
            log.error(e)

    def _parseBody(self, body):
        def parseMultipartFormData(data):
            """parse multi params

            Parse multi params from body then return a dictionary for `MultipartEncode`.

            Args:
                data: plain text from request body.
            Returns:
                A dictionary for `MultipartEncode`.
                example:

                {"id": "example"}
                {"file": ("example.txt", b"file content......", "application/octet-stream")}
                {"file": ("example.txt", b"file content......", "image/jpeg")}
                ......
            Raises:

            """
            data_field = data.strip().split(self.OS_Line_Separator*2, 1)
            if len(data_field[0].split(';')) == 2:
                param_name = data_field[0].split(
                    ';')[1].strip().replace('name=', '')[1:-1]
                param_data = data_field[1]
                return param_name, param_data
            elif len(data_field[0].split(';')) == 3:
                param_name = data_field[0].split(self.OS_Line_Separator)[0].replace(
                    ' ', '').split(';')[1].replace('name=', '')[1:-1]
                filename = data_field[0].split(self.OS_Line_Separator)[0].replace(
                    ' ', '').split(';')[2].replace('filename=', '')[1:-1]
                contenttype = data_field[0].split(self.OS_Line_Separator)[
                    1].replace(' ', '').split(':')[1]
                filecontent = data_field[1]
                return param_name, (filename, filecontent.encode(), contenttype)
            else:
                log.error(
                    f'Can not parse data field: {self.OS_Line_Separator}-----------------{self.OS_Line_Separator}{data.strip()}{self.OS_Line_Separator}-----------------')

        try:
            if self.content_type.split(';')[0] == 'text/html':
                self.data = body
            elif self.content_type.split(';')[0] == 'text/plain':
                self.data = body
            elif self.content_type.split(';')[0] == 'application/json':
                self.jsondata = json.loads(body)
            elif self.content_type.split(';')[0] == 'application/xml':
                self.data = body
            elif self.content_type.split(';')[0] == 'text/xml':
                self.data = body
            elif self.content_type.split(';')[0] == 'application/x-www-form-urlencoded':
                data = {}
                for i in body.split('&'):
                    k, v = i.split('=', 1)
                    data[k] = v
                self.data = data
            elif self.content_type.split(';')[0] == 'multipart/form-data':
                boundary = self.content_type.replace(
                    ' ', '').split(';')[1].split('=')[1]
                a = body.split('--'+boundary)
                fields = {}
                for i in a[1:-1]:
                    k, v = parseMultipartFormData(i)
                    if v.__class__ is tuple:
                        fields[k] = v if k not in fields.keys(
                        ) else fields[k] + v
                    else:
                        fields[k] = v
                self.data = MultipartEncoder(fields=fields, boundary=boundary)
            else:
                log.info('Sorry, not supported now...')
        except Exception as e:
            log.error(e)

    def _parse(self):
        try:
            f = open(self.filename, 'r')
            file_content = f.read()
            f.close()

            head, body = file_content.split(self.OS_Line_Separator*2, 1)

            for index, value in enumerate(head.split(self.OS_Line_Separator)):
                if index == 0:
                    self.request_method = value.strip().split(' ')[0]
                    self.path = value.strip().split(' ')[1].split('?')[0]
                    self.params = dict([i.split('=') for i in value.strip().split(' ')[1].split(
                        '?')[1].split('#')[0].split('&')]) if '?' in value.strip().split(' ')[1] else {}
                    continue
                k, v = value.strip().split(': ')
                if k.lower() == 'host':
                    self.host = v
                    self.headers['Host'] = v
                elif k.lower() == 'cookie':
                    self.headers['Cookie'] = v
                elif k.lower() == 'content-length':
                    continue
                elif k.lower() == 'content-type':
                    self.headers['Content-Type'] = v
                    self.content_type = v
                else:
                    self.headers[k] = v
            if self.request_method.lower() in ['post', 'put']:
                self._parseBody(body)
        except Exception as e:
            log.error(e)
