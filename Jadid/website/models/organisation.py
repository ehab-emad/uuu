from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import uuid, os
from django.core.files.storage import default_storage
from django.contrib.staticfiles.storage import staticfiles_storage
from decouple import config
class Organisation(models.Model):
    UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100,  default= 'No Name Organisation', editable=True)
    full_name = models.CharField(max_length=100,  default= 'No Name Organisation GmbH', editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logo = models.ImageField(upload_to='banners/',  default=None)

    is_current_organisation =models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_current_organisation:
            # Deselect all other organisations
            Organisation.objects.filter(is_current_organisation=True).update(is_current_organisation=False)
        super().save(*args, **kwargs)
        
    def get_banner_url(self):
        """
        Since the default banner will be stored in static and uploaded in media it is necessary to get banner with helper function
        """
        if self.logo:
            return self.logo.url  # Return the URL for the uploaded file
        else:
            # Return the URL for the default static file
            return os.path.join(settings.STATIC_URL,  os.environ.get('DJANGO_CUSTOMER_BANNER', config('DJANGO_CUSTOMER_BANNER', default='website/customer_banner/EDAG_BANNER.png')))
    class Meta:
        app_label = 'website'

    def __str__(self):
        return str(self.full_name )

    def get_banner_path(self):
        url = self.get_banner_url()
        if url.startswith(settings.STATIC_URL):
            # Remove the STATIC_URL part to get the relative path and convert to an absolute path
            relative_path = url[len(settings.STATIC_URL):]
            file_path = staticfiles_storage.path(relative_path)
        elif url.startswith(settings.MEDIA_URL):
            # Remove the MEDIA_URL part to get the relative path and convert to an absolute path
            relative_path = url[len(settings.MEDIA_URL):]
            file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        else:
            raise ValueError("The URL does not belong to STATIC or MEDIA directories.")
        
        return file_path



    @classmethod
    def get_current_organisation(cls, name=None):
        """
        Returns an organisation based on the provided name. If no name is provided, returns the current organisation.
        Raises an exception if no organisation is found.
        """
        try:
            if name:
                return cls.objects.get(name=name)
            return cls.objects.get(is_current_organisation=True)
        except ObjectDoesNotExist:
            return None  # Or handle this case as needed