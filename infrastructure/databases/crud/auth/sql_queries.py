USERNAME_EXISTS = """
SELECT 1 FROM users.users WHERE username = :username
"""

REGISTER_USER = """
INSERT INTO users.users (username, password)
VALUES (:username, :password)
RETURNING id
"""

GET_USER_BY_UUID = """
SELECT * FROM users.users WHERE id = :uuid
"""

GET_USER_BY_USERNAME = """
SELECT * FROM users.users WHERE username = :username
"""