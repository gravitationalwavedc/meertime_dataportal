import os
from pathlib import Path
from datetime import datetime, timezone
import logging

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
    Toa,
)
from .serializers import UploadPipelineImageSerializer, UploadTemplateSerializer
from .storage import create_file_hash

logger = logging.getLogger("dataportal.media")


def get_accessible_toa_files(user, observations):
    """
    Query Toa model for all accessible 32ch_1p_1t timing files for one or more observations.

    TWO-GATE ACCESS CONTROL:
    This function implements the second gate of ToA access control. The first gate
    (observation-level embargo) must be checked by the caller using observation.is_restricted().

    Gate 1 (Caller responsibility): Observation-level embargo
    - Checks if observation is embargoed AND user is in observation's primary project
    - If observation is restricted, NO ToAs are accessible regardless of ToA projects

    Gate 2 (This function): Per-project ToA access
    - Each observation can have ToAs from multiple projects (TPA, TPA2, GC, etc.)
    - Each ToA project has its own embargo period
    - User must be member of each ToA's project to access embargoed files from that project

    Example scenario:
    - Observation taken yesterday by TPA project (accessible to TPA members)
    - Observation has ToAs from both TPA and GC projects
    - User is member of TPA but NOT GC
    - Result: User gets TPA ToAs only, GC ToAs are filtered out

    Another example:
    - Observation taken yesterday by TPA project
    - User is member of GC but NOT TPA
    - Result: Gate 1 blocks access - user gets NO ToAs at all (observation is restricted)

    Returns ToAs filtered by:
    - dm_corrected=False (non-DM-corrected ToAs)
    - nsub_type='1' (single time bin)
    - obs_nchan=32 (32-channel observations)
    - obs_npol=1 (single polarization)
    - Per-project embargo and membership checks

    Note: Multiple ToA database entries (32 for 32ch files, one per frequency channel)
    map to a single .tim file per project per observation.

    Args:
        user: Django User instance
        observations: List or QuerySet of Observation instances (must already pass Gate 1)

    Returns:
        Dict mapping observations to their accessible ToA files:
        {observation: [(project, file_path), ...], ...}
    """
    base_path = Path(settings.MEERTIME_DATA_DIR)

    # Query distinct (observation, project) combinations for ToAs matching the required pattern
    # This groups 32 ToA database entries (one per channel) that map to a single .tim file
    toa_groups = (
        Toa.objects.filter(
            observation__in=observations,
            dm_corrected=False,
            nsub_type="1",
            obs_nchan=32,
            obs_npol=1,
        )
        .values("observation_id", "project_id")
        .distinct()
    )

    # Pre-fetch user's active project memberships to avoid N queries in the loop below
    # For non-authenticated users or superusers, this remains empty (they have different access rules)
    # Structure: {project_id1, project_id2, ...}
    user_project_ids = set()
    if user.is_authenticated and not user.is_superuser:
        user_project_ids = set(
            ProjectMembership.objects.filter(
                user=user,
                is_active=True,
            ).values_list("project_id", flat=True)
        )

    # Fetch related objects for the unique (observation, project) combinations
    # We need one representative ToA per group to access embargo status via the project relationship
    observation_map = {obs.id: obs for obs in observations}
    project_ids = {group["project_id"] for group in toa_groups}
    project_map = {p.id: p for p in Project.objects.filter(id__in=project_ids)}

    # Build result dictionary: for each observation, collect accessible ToA files
    # Gate 2 logic: Filter ToAs by per-project embargo and membership
    result = {obs: [] for obs in observations}

    for group in toa_groups:
        observation = observation_map[group["observation_id"]]
        project = project_map[group["project_id"]]

        # Gate 2: Check per-project ToA access
        # Check if this project's ToAs are embargoed for this observation
        is_embargoed = observation.is_embargoed_for_project(project)

        if is_embargoed:
            # ToA is embargoed - check membership
            # Superusers bypass all embargo restrictions
            if user.is_authenticated and user.is_superuser:
                has_access = True
            # Authenticated users must be active members of the ToA's project
            elif user.is_authenticated:
                has_access = project.id in user_project_ids
            # Anonymous users cannot access embargoed ToAs
            else:
                has_access = False

            if not has_access:
                # Log denial for debugging/audit purposes
                logger.warning(
                    f"User {user.username if user.is_authenticated else 'anonymous'} denied access to "
                    f"ToA files for observation {observation.pulsar.name} {observation.utc_start} beam {observation.beam} "
                    f"project {project.short}"
                )
                continue
        # If ToA is not embargoed, everyone can access (public data)

        # Construct full file path with project folder in the structure
        # Note: This represents a single .tim file that contains 32 ToA entries in the database
        toa_file = (
            base_path
            / observation.pulsar.name
            / observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
            / str(observation.beam)
            / "timing"
            / project.short
            / f"{observation.pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap_chopped.32ch_1p_1t.ar.tim"
        )

        # Verify file exists on disk
        if toa_file.exists():
            result[observation].append((project, toa_file))

    return result


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

        # Gate 1: Check observation-level embargo for all file types
        # This is the primary gate - if observation is restricted, NO data products are accessible
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
            # Gate 2: Get ToAs with per-project access control
            # Gate 1 (observation embargo) was already checked above
            # This handles filtering ToAs by individual project memberships
            accessible_files_dict = get_accessible_toa_files(request.user, [observation])
            accessible_files = accessible_files_dict[observation]

            # If no accessible files, return message instead of empty zip
            if not accessible_files:
                return HttpResponse(
                    "No ToA files are available for download. Files may be under embargo or not yet processed.",
                    status=404,
                )

            # Generate ZIP file with accessible ToAs
            def generate_zip():
                zs = ZipStream()
                for project, toa_file in accessible_files:
                    zip_path = f"timing/{project.short}/{toa_file.name}"
                    zs.add_path(str(toa_file), zip_path)
                for chunk in zs:
                    yield chunk

            filename = f"{observation.pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_{observation.beam}_toas.zip"
            response = StreamingHttpResponse(generate_zip(), content_type="application/zip")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

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
        observations = Observation.objects.filter(
            pulsar=pulsar, project__main_project__name__iexact="MeerTime", obs_type="fold"
        ).order_by("utc_start")

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
            has_files = False

            if file_type == "toas":
                # Gate 1: Filter observations by observation-level embargo
                # Gate 2: get_accessible_toa_files handles per-project ToA access
                accessible_observations = [obs for obs in observations if not obs.is_restricted(request.user)]
                obs_toa_files = get_accessible_toa_files(request.user, accessible_observations)

                for observation, toa_files in obs_toa_files.items():
                    timestamp_dir = observation.utc_start.strftime("%Y-%m-%d-%H:%M:%S")
                    beam_dir = str(observation.beam)

                    for project, toa_file in toa_files:
                        # Nested structure: timing/{timestamp}/{beam}/timing/{project}/{filename}
                        zip_path = f"timing/{timestamp_dir}/{beam_dir}/timing/{project.short}/{toa_file.name}"
                        zs.add_path(str(toa_file), zip_path)
                        has_files = True
            else:
                # Handle full and decimated files
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
                            full_filename = (
                                f"{pulsar.name}_{observation.utc_start.strftime('%Y-%m-%d-%H:%M:%S')}_zap.ar"
                            )
                            zs.add_path(str(full_res_abs_path), f"{timestamp_dir}/{beam_dir}/{full_filename}")
                            has_files = True

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
                            has_files = True

            # Add README if no files were added
            if not has_files:
                readme_content = (
                    "No files are available for download. Files may be under embargo or not yet processed."
                )
                zs.add(readme_content.encode("utf-8"), "README.txt")

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
