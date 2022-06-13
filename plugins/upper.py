class PayloadProcessor:
    name = __name__
    description = '大写'
    def __init__(self, payload, args=[]):
        self.payload = payload
        self.args = args

    def __str__(self):
        return self.name

    def genterPatload(self):
        try:
            return self.payload.upper()
        except Exception as e:
            print(e)