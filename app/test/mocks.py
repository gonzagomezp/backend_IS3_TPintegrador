# Mock para MySQLDatabase
class MockModel:
    def __init__(self):
        self.users = []

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
        if not username or not password:
            raise ValueError("Username and password are required")
        user_id = len(self.users) + 1
        self.users.append((user_id, username, password))
        print(self.users)
        return user_id

    def delete_user(self, idd: int):
        if idd == 1: 
            return True
        else:
            return False
