import re


def validate_phone_number(phone_number):
    phone_number_regex = re.compile(r'^\d{10}$')
    if not phone_number_regex.match(phone_number):
        return "Invalid phone number"


def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.search(pattern, email):
        return "Invalid email"
