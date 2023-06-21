from django.conf import settings
from sentry_sdk import last_event_id
from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from .serializers import UploadTemplateSerializer, UploadPipelineImageSerializer
from .storage import create_file_hash
from .models import (
    Template,
    Pulsar,
    Project,
    PipelineImage,
    PipelineRun,
    FoldPulsarResult,
)


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


class UploadPipelineImage(ViewSet):
    serializer_class = UploadPipelineImageSerializer

    def list(self, request):
        return Response("GET API")


    def create(self, request):
        pipeline_run_id = request.data.get('pipeline_run_id')
        image_upload    = request.FILES.get('image_upload')
        image_type      = request.data.get('image_type')
        resolution      = request.data.get('resolution')
        cleaned         = request.data.get('cleaned')

        # Get foreign key models
        try:
            pipeline_run  = PipelineRun.objects.get(id=pipeline_run_id)
        except PipelineRun.DoesNotExist:
            return JsonResponse({'error': f'PipelineRun ID {pipeline_run} not found.'}, status=400)
        fold_pulsar_result = FoldPulsarResult.objects.get(observation=pipeline_run.observation)

        # Create Template object
        pipeline_image, created = PipelineImage.objects.get_or_create(
            fold_pulsar_result=fold_pulsar_result,
            cleaned=cleaned,
            image_type=image_type,
            resolution=resolution,
        )
        pipeline_image.save()
        # We use the save() method of the FileField to save the file.
        # This ensures that the file object remains open until the file is properly saved to the disk.
        pipeline_image.image.save(image_upload.name, image_upload, save=True)
        if created:
            response = f"POST API and you have uploaded a new image to PipelineImage id: {pipeline_image}"
        else:
            response = f"POST API and you have uploaded a image overriding PipelineImage id: {pipeline_image} (already exists)"

        return JsonResponse(
            {
                'text': response,
                'success': True,
                'created': created,
                'errors': None,
                'id' : pipeline_image.id,
            },
            status=201,
        )