from rest_framework_simplejwt.tokens import Token, RefreshToken
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

logger.info("Entered..............................................")


def get_custom_primary_key_settings():
    custom_id_fields = {
        'User': 'user_id',
        'Profile': 'profile_id',
        # Add more models and their respective custom primary key fields here
    }
    # You might dynamically fetch models and their custom primary keys here

    jwt_settings = {}
    for model, custom_id_field in custom_id_fields.items():
        jwt_settings[f'{model.upper()}_ID_FIELD'] = custom_id_field

    return jwt_settings


def custom_token_payload(user):
    logger.info("Generating custom token payload...")
    token = Token()
    token['user_id'] = user.id
    token['username'] = user.username
    token['email'] = user.email
    # Add other user details as needed

    # Set token expiration (optional)
    token['exp'] = token.current_time + timedelta(days=1)  # Expiry time (e.g., 1 day)

    return token


class CustomPayloadRefreshToken(RefreshToken):
    def __init__(self, user_data):
        super().__init__()
        self['user_id'] = user_data['user_id']
        self['username'] = user_data['username']
        self['email'] = user_data['email']
        self['is_admin'] = user_data['is_admin']
