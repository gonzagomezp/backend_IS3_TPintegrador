# Mock para MySQLDatabase
class MockModel:
    def __init__(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_users(self):
        return [
            [1, "testuser1", "testpassword1"],
            [2, "testuser2", "testpassword2"]
        ]

    def get_user(self, username: str):
        if (username == "testuser"):
            return [1, username, "testpassword"]
        else:
            return None

    def insert_user(self, username: str, password: str):
        return 1

    def delete_user(self, idd: int):
        if idd == 1: 
            return True
        else:
            return False
