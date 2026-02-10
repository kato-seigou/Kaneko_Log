from fastapi.responses import RedirectResponse
from urllib.parse import quote

FLASH_SUCCESS = "flash_success"
FLASH_ERROR = "flash_error"
FLASH_INFO = "flash_info"

def redirect_with_flash(
    url: str,
    message: str,
    level: str = FLASH_SUCCESS,
    status_code: int = 303,
    max_age: int = 10
) -> RedirectResponse:
    """
    redirect しつつ、flash cookieを1つセットする
    """
    response = RedirectResponse(url=url, status_code=status_code)
    response.set_cookie(key=level, value=quote(message), max_age=max_age)
    return response

