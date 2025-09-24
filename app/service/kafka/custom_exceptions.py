class UnknownException(Exception):
    def __init__(self, method=""):
        self.message = "An unknown error occurred at {}. Watch the log.".format(method)
        super().__init__(self.message)

class TopicAlreadyExistsException(Exception):
    def __init__(self, topic):
        self.topic = topic
        self.message = f"Topic '{topic}' already exists."
        super().__init__(self.message)

class TopicNotFoundException(Exception):
    def __init__(self, topic):
        self.topic = topic
        self.message = f"Topic '{topic}' not found."
        super().__init__(self.message)
