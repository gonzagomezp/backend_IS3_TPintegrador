# Mock para MySQLDatabase
class MockMySQLDatabase:
    def __init__(self, *args, **kwargs):
        self.users = []

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_users(self):
        return self.users

    def get_user(self, username: str):
        for user in self.users:
            if user[1] == username:
                return user
        return None

    def insert_user(self, username: str, password: str):
        if not username or not password:
            raise ValueError("Username and password are required")
        user_id = len(self.users) + 1
        self.users.append((user_id, username, password))
        return user_id

    def delete_user(self, idd: int):
        for user in self.users:
            if user[0] == idd:
                self.users.remove(user)
                return True
        return False
