from fastapi import Request
from fastapi.templating import Jinja2Templates
from urllib.parse import unquote

from ._flash import FLASH_SUCCESS, FLASH_ERROR, FLASH_INFO

templates = Jinja2Templates(directory="app/app/templates")

def render(request: Request, name: str, context: dict, status_code: int = 200):
    flash_success = request.cookies.get(FLASH_SUCCESS)
    flash_error = request.cookies.get(FLASH_ERROR)
    flash_info = request.cookies.get(FLASH_INFO)
    
    flash_success = unquote(flash_success) if flash_success else None
    flash_error = unquote(flash_error) if flash_error else None
    flash_info = unquote(flash_info) if flash_info else None
    
    ctx = {
        "request": request,
        **context,
        "flash_success": flash_success,
        "flash_error": flash_error,
        "flash_info": flash_info
    }
    
    response = templates.TemplateResponse(name, ctx, status_code)
    
    if flash_success:
        response.delete_cookie(FLASH_SUCCESS)
    if flash_error:
        response.delete_cookie(FLASH_ERROR)
    if flash_info:
        response.delete_cookie(FLASH_INFO)
    
    return response