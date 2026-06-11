from django.db import models
from django.db import models
from django.utils import timezone

class OTPRecord(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # OTP expires after 5 minutes
        expiration_time = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() > expiration_time