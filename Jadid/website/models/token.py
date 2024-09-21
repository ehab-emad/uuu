from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
class Token(models.Model):
    TOKEN_TYPE_CHOICES = [
        ('limited', 'Limited Usage'),
        ('unlimited', 'Unlimited Usage'),
        ('expiry', 'Expiry Date'),
        ('expiry_limited', 'Expiry and Limited Usage'),
    ]

    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES, default='limited')
    max_usage = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum usage count. Leave blank for unlimited.")
    usage_count = models.PositiveIntegerField(default=0, help_text="Number of times this token has been used.")
    expiry_date = models.DateTimeField(null=True, blank=True, help_text="Expiry date for the token. Leave blank for no expiry.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    protected_component_UUID = models.UUIDField(verbose_name="Shared Component",   default=None, editable=True, blank=True, null=True,)
    related_tokens = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='bundled_tokens', help_text="Tokens that are part of this bundle.")
    
    def is_expired(self):
        if self.token_type in ['expiry', 'expiry_limited']:
            return timezone.now() >= self.expiry_date
        return False

    def can_be_used(self):
        if self.token_type in ['limited', 'expiry_limited']:
            if self.usage_count >= self.max_usage:
                return False
        return not self.is_expired()

    def use(self):
        if not self.can_be_used():
            raise ValueError("Token cannot be used. It is either expired or has reached its usage limit.")
        self.usage_count += 1
        self.save()

    def use_bundle(self):
        if self.related_tokens.exists():
            for token in self.related_tokens.all():
                token.use()

    def __str__(self):
        return self.key