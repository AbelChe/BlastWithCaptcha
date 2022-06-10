import base64

class PayloadProcessor:
    name = __name__
    description = 'base64编码'
    def __init__(self, payload, args=[]):
        self.payload = payload
        self.args = args

    def __str__(self):
        return self.name

    def genterPatload(self):
        try:
            return base64.b64encode(self.payload.encode()).decode()
        except Exception as e:
            print(e)