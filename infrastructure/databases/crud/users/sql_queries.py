GET_USER_INFO_BY_SESSION = """
SELECT u.id, u.username
FROM users.sessions s
JOIN users.users as u ON u.id = s.user_id
WHERE s.id = :session_uuid
"""

GET_SESSION_BY_UUID = """
SELECT * FROM users.sessions WHERE id = :session_uuid
"""