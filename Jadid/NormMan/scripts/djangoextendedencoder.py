from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.core.serializers.json import DjangoJSONEncoder

class ExtendedEncoder(DjangoJSONEncoder):
    '''for dealing with file fields
    '''
    def default(self, o):
        match type(o).__qualname__:
            case ImageFieldFile.__qualname__:
                return str(o)
            case FieldFile.__qualname__:
                return str(o.name)         

        return super().default(o)





        # if isinstance(o, ImageFieldFile):
        #     return str(o)
        # elif isinstance(o, FieldFile):
        #     return str(o.name)
        # else:
        #     return super().default(o)