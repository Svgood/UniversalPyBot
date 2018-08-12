class User:

    def __init__(self, teleid, state):
        self.teleid = teleid
        self.state = state

        self.adminDelete = []
        self.adminAdding = []

    def admin_refresh(self):
        self.adminAdding = []
        self.adminDelete = []
