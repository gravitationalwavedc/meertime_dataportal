from rest_framework.serializers import Serializer, FileField, CharField, BooleanField, IntegerField

from .models import Template

# Serializers define the API representation.

class UploadTemplateSerializer(Serializer):
    template_upload = FileField()
    pulsar_name     = CharField(max_length=32)
    project_code    = CharField(max_length=32)
    band            = CharField(max_length=32)


class UploadPipelineImageSerializer(Serializer):
    pipeline_run_id = IntegerField()
    image_upload    = FileField()
    image_type      = CharField(max_length=16)
    resolution      = CharField(max_length=4)
    cleaned         = BooleanField()