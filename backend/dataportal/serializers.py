from rest_framework.serializers import Serializer, FileField, CharField

from .models import Template

# Serializers define the API representation.

class UploadTemplateSerializer(Serializer):
    template_upload = FileField()
    pulsar_name     = CharField(max_length=32)
    project_code    = CharField(max_length=32)
    band            = CharField(max_length=32)


class UploadImageSerializer(Serializer):
    image_upload = FileField()
    class Meta:
        fields = ['image_upload']