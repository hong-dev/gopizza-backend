from django.utils               import six
from django.contrib.auth.tokens import PasswordRestTokenGenerator

class AccountActivationTokenGenerator(PasswordRestTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp_)) + six.text_type(user.is_active)

account_activation_token = AccountActivationTokenGenerator()
