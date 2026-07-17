import re
from pathlib import Path


EMAIL_REGEX = re.compile(r"^[\w\.\-]+@[\w\.\-]+\.\w{2,}$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{6,14}$")


def detect_input_type(value: str) -> str:
    value = value.strip()
    if EMAIL_REGEX.match(value):
        return "email"
    if PHONE_REGEX.match(value):
        return "phone"
    return "username"


def detect_and_parse(
    email: str | None = None,
    phone: str | None = None,
    username: str | None = None,
    photo_path: str | None = None,
) -> dict:
    inputs = []
    if email:
        inputs.append(("email", email.strip()))
    if phone:
        inputs.append(("phone", phone.strip()))
    if username:
        inputs.append(("username", username.strip()))
    if photo_path:
        p = Path(photo_path)
        if p.exists() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            inputs.append(("photo", str(p.resolve())))
        else:
            raise ValueError(f"Invalid photo path or unsupported format: {photo_path}")
    if not inputs:
        guessed = None
        if email:
            guessed = ("email", email.strip())
        elif phone:
            guessed = ("phone", phone.strip())
        elif username:
            guessed = ("username", username.strip())
        if guessed:
            inputs.append(guessed)
        else:
            raise ValueError("No input provided. Provide at least one of: email, phone, username, photo")
    return {"inputs": inputs}
