import hashlib

class PayloadProcessor:
    name = __name__
    description = 'md5'
    def __init__(self, payload, args=[]):
        self.payload = payload
        self.args = args

    def __str__(self):
        return self.name

    def genterPatload(self):
        try:
            return hashlib.md5(self.payload.encode()).hexdigest()
        except Exception as e:
            print(e)