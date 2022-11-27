from datetime import datetime


def get_date_file_name() -> str:
    now = datetime.now()
    return (
        f"{now.year}_{0 if now.month < 10 else ''}{now.month}_"
        f"{0 if now.day < 10 else ''}{now.day}_{0 if now.hour < 10 else ''}"
        f"{now.hour}{0 if now.minute < 10 else ''}{now.minute}"
        f"{0 if now.second < 10 else ''}{now.second}"
    )
