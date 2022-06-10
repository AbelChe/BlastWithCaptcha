class PayloadProcessor:
    name = __name__
    description = '添加前缀'
    def __init__(self, payload, args=[]):
        self.payload = payload
        self.args = args

    def __str__(self):
        return self.name

    def genterPatload(self):
        try:
            return self.args[0] + self.payload
        except Exception as e:
            print(e)