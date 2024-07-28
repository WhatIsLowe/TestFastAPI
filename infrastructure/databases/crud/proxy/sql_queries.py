ADD_PROXY6_API_KEY = """
INSERT INTO proxy.proxy6 (user_id, api_key)
VALUES (:user_id, :api_key)
RETURNING id
"""

GET_PROXY6_API_KEY = """
SELECT api_key
FROM proxy.proxy6
WHERE user_id = :user_id
"""