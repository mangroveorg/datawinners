class FakeRequest(dict):
    def __init__(self, get=None, post=None, user=None):
        self.get = get
        self.post = post
        self.user = user

    def GET(self):
        return self.get

    def POST(self):
        return self.post