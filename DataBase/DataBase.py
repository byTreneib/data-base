# Main class -> Manages file and backend?


class DataBase:
    def __init__(self):
        self.tables = []

    def register(self, cls):
        self.tables.append(cls)

        return cls
