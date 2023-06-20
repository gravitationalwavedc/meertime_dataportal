from django.conf import settings
from sentry_sdk import last_event_id
from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from .serializers import UploadTemplateSerializer, UploadImageSerializer
from .models import Template, Pulsar, Project
from .storage import create_file_hash


def handler500(request):
    if settings.ENABLE_SENTRY_DSN:
        return render(
            request,
            "500.html",
            {
                "sentry_event_id": last_event_id(),
                "sentry_dsn": settings.SENTRY_DSN,
            },
        )
    else:
        return render(request, "500.html", {})



class UploadTemplate(ViewSet):
    serializer_class = UploadTemplateSerializer

    def create(self, request):
        template_upload = request.FILES.get('template_upload')
        pulsar_name     = request.data.get('pulsar_name')
        project_code    = request.data.get('project_code')
        band            = request.data.get('band')

        # Get foreign key models
        try:
            pulsar  = Pulsar.objects.get(name=pulsar_name)
        except Pulsar.DoesNotExist:
            return JsonResponse({'error': f'Pulsar {pulsar_name} not found.'}, status=400)
        try:
            project = Project.objects.get(code=project_code)
        except Project.DoesNotExist:
            return JsonResponse({'error': f'Project code {project_code} not found.'}, status=400)

        # Create Template object
        template, created = Template.objects.get_or_create(
            pulsar=pulsar,
            project=project,
            band=band,
            template_hash=create_file_hash(template_upload),
        )
        template.save()
        if created:
            # We use the save() method of the FileField to save the file.
            # This ensures that the file object remains open until the file is properly saved to the disk.
            template.template_file.save(template_upload.name, template_upload, save=True)
            response = f"POST API and you have uploaded a template file to Template id: {template}"
        else:
            response = f"POST API and you have uploaded a template file to Template id: {template} (already exists)"

        return JsonResponse(
            {
                'text': response,
                'success': True,
                'created': created,
                'errors': None,
                'id' : template.id,
            },
            status=201,
        )


class UploadImage(ViewSet):
    serializer_class = UploadImageSerializer

    def list(self, request):
        return Response("GET API")

    def create(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        content_type = file_uploaded.content_type
        response = "POST API and you have uploaded a {} file".format(content_type)
        return Response(response)