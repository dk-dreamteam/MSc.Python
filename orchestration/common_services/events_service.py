from datetime import datetime

class EventsService:
    def __init__(self, logger):
        self.logger = logger

    def Send(self):
        self.logger.info("sentttt")

    def GetTimestamp(self):
        return f"{datetime.now()} senttttt"
