from pathlib import Path
from fastapi.templating import Jinja2Templates
from datetime import timezone, timedelta

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

JST = timezone(timedelta(hours=9))

def to_jst_str(dt, fmt="%Y-%m-%d %H:%M"):
    if dt is None:
        return ""
    # SQLiteはtzinfoを落としがちなので、無いならUTCとして扱う
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(JST).strftime(fmt)

templates.env.filters["to_jst"] = to_jst_str