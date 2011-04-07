
class Frontend:
    class FrontendException:
        def __init__(self, msg):
            self.msg = msg
        def __str__(self):
            return self.msg
