import os
from pathlib import Path
from datetime import datetime, timezone

from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone as django_timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from sentry_sdk import last_event_id
from zipstream import ZipStream
import logging

from .file_utils import get_file_list, get_file_path, serve_file
from .models import (
    Observation,
    PipelineImage,
    PipelineRun,
    Project,
    ProjectMembership,
    Pulsar,
    PulsarFoldResult,
    Template,
)
from .serializers import UploadPipelineImageSerializer, UploadTemplateSerializer
from .storage import create_file_hash

logger = logging.getLogger("dataportal.media")


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
def download_observation_files(request, jname, observation_timestamp, beam, file_type):
    """
    View to serve files for a specific observation using new URL format

    :param request: HTTP request
    :param jname: Name of the pulsar (e.g., 'J1227-6208')
    :param observation_timestamp: UTC timestamp in format 'YYYY-MM-DD-HH:MM:SS'
    :param beam: Beam number
    :param file_type: Type of file to download ('full', 'decimated', or 'toas')
    :return: File download response
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized - please log in", status=401)

    # Validate file type
    if file_type not in ["full", "decimated", "toas"]:
        return HttpResponse("Invalid file type specified", status=400)

    try:
        # Parse the timestamp and make it timezone-aware (UTC)
        naive_dt = datetime.strptime(observation_timestamp, "%Y-%m-%d-%H:%M:%S")
        utc_start = naive_dt.replace(tzinfo=timezone.utc)

        # Find the observation by pulsar name, timestamp, and beam
        observation = Observation.objects.get(pulsar__name=jname, utc_start=utc_start, beam=beam)

        # Check if the observation is restricted for this user
        if observation.is_restricted(request.user):
            return HttpResponse("Access denied - data is under embargo. Please request to join project.", status=403)

        # Construct the relative path for the observation
        base_path = Path(
            f"{observation.pulsar.name}/{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}/{observation.beam}"
        )

        if file_type == "full":
            # Full resolution file
            file_path = (
                base_path / f"{observation.pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
            )
        elif file_type == "decimated":
            # Decimated file
            file_path = (
                base_path
                / "decimated"
                / f"{observation.pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.1ch_1p_1t.ar"
            )
        elif file_type == "toas":
            # ToAs file
            file_path = (
                base_path
                / "timing"
                / f"{observation.pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
            )

        return serve_file(str(file_path))

    except Observation.DoesNotExist:
        return HttpResponse("Observation not found", status=404)
    except ValueError:
        return HttpResponse("Invalid timestamp format", status=400)


@require_GET
def download_pulsar_files(request, jname, file_type):
    """
    View to serve files for a specific pulsar using new URL format

    :param request: HTTP request
    :param jname: Name of the pulsar (e.g., 'J1227-6208')
    :param file_type: Type of file to download ('full', 'decimated', or 'toas')
    :return: File download response
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized - please log in", status=401)

    # Validate file type
    if file_type not in ["full", "decimated", "toas"]:
        return HttpResponse("Invalid file type specified", status=400)

    try:
        pulsar = Pulsar.objects.get(name=jname)
        observations = Observation.objects.filter(pulsar=pulsar).order_by("utc_start")

        # If there are no observations, return 404
        if not observations.exists():
            return HttpResponse("No observations found for this pulsar", status=404)

        # Check if all observations are restricted for this user
        all_restricted = all(obs.is_restricted(request.user) for obs in observations)
        if all_restricted:
            return HttpResponse(
                "Access denied - all data is under embargo. Please request to join project(s).", status=403
            )

        def generate_zip():
            # Create a ZipStream for streaming
            zs = ZipStream()

            for observation in observations:
                # Check if the observation is restricted for this user
                if observation.is_restricted(request.user):
                    continue

                # Construct the relative path for the observation
                base_path = Path(
                    f"{pulsar.name}/{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}/{observation.beam}"
                )

                if file_type == "full":
                    # Add full resolution file
                    full_res_path = (
                        base_path / f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
                    )
                    full_res_abs_path = Path(settings.MEERTIME_DATA_DIR) / full_res_path
                    if full_res_abs_path.exists():
                        timestamp_dir = observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                        beam_dir = str(observation.beam)
                        full_filename = f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
                        zs.add_path(str(full_res_abs_path), f"{timestamp_dir}/{beam_dir}/{full_filename}")

                elif file_type == "decimated":
                    # Add decimated file
                    decimated_path = (
                        base_path
                        / "decimated"
                        / f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.1ch_1p_1t.ar"
                    )
                    decimated_abs_path = Path(settings.MEERTIME_DATA_DIR) / decimated_path
                    if decimated_abs_path.exists():
                        timestamp_dir = observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                        beam_dir = str(observation.beam)
                        decimated_filename = f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.1ch_1p_1t.ar"
                        zs.add_path(str(decimated_abs_path), f"{timestamp_dir}/{beam_dir}/{decimated_filename}")

                elif file_type == "toas":
                    # Add ToAs file only
                    toas_path = (
                        base_path
                        / "timing"
                        / f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
                    )
                    toas_abs_path = Path(settings.MEERTIME_DATA_DIR) / toas_path
                    if toas_abs_path.exists():
                        timestamp_dir = observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                        beam_dir = str(observation.beam)
                        toas_filename = f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
                        zs.add_path(str(toas_abs_path), f"timing/{timestamp_dir}/{beam_dir}/{toas_filename}")

            # Stream the ZIP data
            for chunk in zs:
                yield chunk

        response = StreamingHttpResponse(generate_zip(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="pulsar_{pulsar.name}_{file_type}_files.zip"'
        return response

    except Pulsar.DoesNotExist:
        return HttpResponse("Pulsar not found", status=404)


@require_GET
def serve_protected_media(request, file_path):
    """
    Serve media files with access control based on embargo and project membership.

    Images:
    - Anonymous users can access non-embargoed images
    - Authenticated users can access non-embargoed images and embargoed images if they are:
      * Superusers, OR
      * Members of the observation's project

    Templates:
    - Require authentication for all downloads (like ephemeris)
    - Authenticated users can access templates if they are:
      * Superusers, OR
      * Members of the template's project (for embargoed templates), OR
      * Any authenticated user (for non-embargoed templates)

    Looks up the file in the database to find associated observation/template,
    then checks access permissions before serving.
    """
    # Validate path security
    full_path = Path(settings.MEDIA_ROOT) / file_path
    try:
        full_path = full_path.resolve()
        media_root = Path(settings.MEDIA_ROOT).resolve()
        if not str(full_path).startswith(str(media_root)):
            logger.warning(f"Path traversal attempt: {request.user} -> {file_path}")
            return HttpResponse("Access denied", status=403)
    except Exception:
        return HttpResponse("Invalid path", status=400)

    if not full_path.exists():
        return HttpResponse("File not found", status=404)

    # Normalize the file_path for database lookup
    lookup_path = file_path.lstrip("/")

    # Try to find as PipelineImage
    try:
        pipeline_image = PipelineImage.objects.select_related(
            "pulsar_fold_result__observation__project", "pulsar_fold_result__observation"
        ).get(image=lookup_path)

        observation = pipeline_image.pulsar_fold_result.observation

        # Use observation's is_restricted method
        if observation.is_restricted(request.user):
            if not request.user.is_authenticated:
                logger.warning(f"Anonymous user denied embargoed image: {file_path}")
                return HttpResponse("Unauthorized - please log in", status=401)
            else:
                logger.warning(f"Unauthorized image access request: {request.user} -> {file_path}")
                return HttpResponse(
                    "Access denied - data is under embargo. Please request to join project.", status=403
                )

        return FileResponse(full_path.open("rb"), as_attachment=False, filename=full_path.name)

    except PipelineImage.DoesNotExist:
        pass

    # Try to find as Template
    try:
        template = Template.objects.select_related("project", "pulsar").get(template_file=lookup_path)

        # Use template's is_restricted method
        if template.is_restricted(request.user):
            if not request.user.is_authenticated:
                logger.warning(f"Anonymous user denied template download: {file_path}")
                return HttpResponse("Unauthorized - please log in", status=401)
            else:
                logger.warning(f"Unauthorized template access request: {request.user} -> {file_path}")
                return HttpResponse(
                    "Access denied - data is under embargo. Please request to join project.", status=403
                )

        return FileResponse(full_path.open("rb"), as_attachment=False, filename=full_path.name)

    except Template.DoesNotExist:
        pass

    # File exists but not in database - deny access
    logger.warning(f"File not in database: {request.user} -> {file_path}")
    return HttpResponse("File not found", status=404)
