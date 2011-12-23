class FakeRequest(dict):
    def __init__(self, get=None, post=None, user=None):
        self.GET = get
        self.POST = post
        self.user = user

