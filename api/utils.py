import re
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from lbdev_chat import settings


def email_hide(email: str):
    def hide_method(x):
        return "*" * len(x.group())
    hidden_email = re.sub(r"(?<=^.{2}).*(?=@)", hide_method, email)
    hidden_email = re.sub(r"(?<=@)(.*?)(?=\.)", hide_method, hidden_email)
    return hidden_email
