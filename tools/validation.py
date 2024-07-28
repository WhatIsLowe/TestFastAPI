import requests


def is_valid_api_key(api_key: str) -> bool:
    """Проверяет, валидный ли API-ключ Proxy6"""
    if not api_key:
        return False

    url = f"https://proxy6.net/api/{api_key}/getproxy"
    response = requests.get(url)
    if response.status_code != 200 or response.json()['status'] != 'yes':
        return False

    return True
