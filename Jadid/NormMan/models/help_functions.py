from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.files import ImageFieldFile, FieldFile
import os


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


def get_upload_to(instance, filename):
    '''Dynamic Upload To
    '''
    file_name, file_extension = os.path.splitext(filename)
    match file_extension:

        case ".stl":
            file_name = "stl_thumbnail"
        case ".png":
            file_name = "thumbnail_" + instance.__class__.__name__ + "_id_" + instance.id
        case ".jpg":
            file_name = "thumbnail_" + instance.__class__.__name__ + "_id_" + instance.id
        case ".jpeg":
            file_name = "thumbnail_" + instance.__class__.__name__ + "_id_" + instance.id
        case ".pdf":
            file_name = "supplier_info"
        case ".CATPart":
            file_name = "catia_part"

    path = remove_prefix(instance.data_path + file_name + file_extension , "media/")
    return path


def NumbersOnlyValidator(value):
    if not value.isnumeric():
        raise ValidationError(
            _('%(value)s is not a number'),
            params={'value': value},
        )