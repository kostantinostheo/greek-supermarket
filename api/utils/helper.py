import re
import unicodedata


def normalize_text(text=""):
    return re.sub(r"[̀-ͯ]", "", unicodedata.normalize("NFD", text.lower()))
