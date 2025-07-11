import string
import random
import secrets
import uuid
from ..models import SensorItem


def generate_unique_registration_code():
    while True:
        code = "-".join(
            "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
            for _ in range(3)
        )
        if not SensorItem.objects.filter(registration_code=code).exists():
            return code


def generate_unique_password():
    while True:
        pwd = "".join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))
        if not SensorItem.objects.filter(password=pwd).exists():
            return pwd


def generate_api_key():
    # Strong and unique, does not need to be user-friendly
    return uuid.uuid4().hex
