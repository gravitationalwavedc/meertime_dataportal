from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from sentry_sdk import last_event_id

from .file_utils import serve_file
from .models import PipelineImage, PipelineRun, Project, Pulsar, PulsarFoldResult, Template
from .serializers import UploadPipelineImageSerializer, UploadTemplateSerializer
from .storage import create_file_hash


class TemplateAddPermission(BasePermission):
    """
    Custom permission to check for dataportal.add_template permission.
    """

    def has_permission(self, request, view):
        return request.user.has_perm("dataportal.add_template")


class PipelineImageAddPermission(BasePermission):
    """
    Custom permission to check for dataportal.add_pipelineimage permission.
    """

    def has_permission(self, request, view):
        return request.user.has_perm("dataportal.add_pipelineimage")


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

    return render(request, "500.html", {})


@method_decorator(csrf_exempt, name="dispatch")
class UploadTemplate(ViewSet):
    serializer_class = UploadTemplateSerializer
    permission_classes = [TemplateAddPermission]

    def create(self, request):
        template_upload = request.FILES.get("template_upload")
        pulsar_name = request.data.get("pulsar_name")
        project_code = request.data.get("project_code")
        project_short = request.data.get("project_short")
        band = request.data.get("band")

        # Get foreign key models
        try:
            pulsar = Pulsar.objects.get(name=pulsar_name)
        except Pulsar.DoesNotExist:
            return JsonResponse({"errors": f"Pulsar {pulsar_name} not found."}, status=400)
        try:
            if project_code is not None:
                project = Project.objects.get(code=project_code)
            elif project_short is not None:
                project = Project.objects.get(short=project_short)
            else:
                # Should have a project code or short so I can't create an ephemeris
                return JsonResponse({"errors": "Must include either a project_code or a project_short"}, status=400)
        except Project.DoesNotExist:
            return JsonResponse({"errors": "Project code {project_code} not found."}, status=400)

        # Create Template object
        with template_upload.open("rb") as file:
            template_hash = create_file_hash(file)
            # Check if a template with the same hash already exists
            template_check = Template.objects.filter(
                pulsar=pulsar,
                project=project,
                band=band,
                template_hash=template_hash,
            )
            if template_check.exists():
                id = template_check.first().id
                response = f"POST API and you have uploaded a template file to Template id: {id} (already exists)"
                created = False
            else:
                template = Template.objects.create(
                    pulsar=pulsar, project=project, band=band, template_hash=template_hash, template_file=file
                )
                template.save()
                id = template.id
                response = f"POST API and you have uploaded a template file to Template id: {id}"
                created = True

        return JsonResponse(
            {
                "text": response,
                "success": True,
                "created": created,
                "errors": None,
                "id": id,
            },
            status=201,
        )


@method_decorator(csrf_exempt, name="dispatch")
class UploadPipelineImage(ViewSet):
    serializer_class = UploadPipelineImageSerializer
    permission_classes = [PipelineImageAddPermission]

    def list(self, request):
        return Response("GET API")

    def create(self, request):
        pipeline_run_id = request.data.get("pipeline_run_id")
        image_upload = request.FILES.get("image_upload")
        image_type = request.data.get("image_type")
        resolution = request.data.get("resolution")
        cleaned = request.data.get("cleaned")

        # Get foreign key models
        try:
            pipeline_run = PipelineRun.objects.get(id=pipeline_run_id)
        except PipelineRun.DoesNotExist:
            response = f"PipelineRun ID {pipeline_run_id} not found."
            return JsonResponse(
                {
                    "errors": response,
                    "text": response,
                    "success": False,
                },
                status=400,
            )
        pulsar_fold_result = PulsarFoldResult.objects.get(observation=pipeline_run.observation)

        # Create Template object
        pipeline_image, created = PipelineImage.objects.get_or_create(
            pulsar_fold_result=pulsar_fold_result,
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
            response = f"POST API and you have uploaded a image overriding PipelineImage id: {pipeline_image} (already exists)"  # noqa E501

        return JsonResponse(
            {
                "text": response,
                "success": True,
                "created": created,
                "errors": None,
                "id": pipeline_image.id,
            },
            status=201,
        )


@require_GET
def download_file(request, file_path):
    """
    View to serve files from the mounted data directory

    :param request: HTTP request
    :param file_path: Path to the file to download
    :return: File download response
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    # Check if user is unrestricted (has sufficient permissions)
    if not request.user.is_unrestricted():
        return HttpResponse("Access denied", status=403)

    return serve_file(file_path)
