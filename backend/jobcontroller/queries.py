from datetime import datetime

import graphene
from graphene import relay
from jobcontroller import request_file_list, get_fluxcal_archive_path
from graphql_jwt.decorators import login_required

from dataportal.models import PulsarFoldResult


class JobControllerFile(graphene.ObjectType):
    class Meta:
        interfaces = (relay.Node,)

    file_size = graphene.Int()
    is_dir = graphene.Boolean()
    path = graphene.String()


class FileConnection(relay.Connection):
    class Meta:
        node = JobControllerFile


class Query(graphene.ObjectType):
    file_single_list = relay.ConnectionField(
        FileConnection,
        jname=graphene.String(required=True),
        utc=graphene.String(required=True),
        beam=graphene.Int(required=True),
    )

    @login_required
    def resolve_file_single_list(self, info, **kwargs):

        pulsar_fold_result = PulsarFoldResult.objects.get(
            pulsar__name=kwargs.get("jname"),
            observation__utc_start=datetime.strptime(kwargs.get("utc"), "%Y-%m-%d-%H:%M:%S"),
            observation__beam=kwargs.get("beam"),
        )

        # Only allow files if the user passes has access to this
        # fold pulsar observation.
        if not pulsar_fold_result.observation.is_restricted(info.context.user):
            path = get_fluxcal_archive_path(
                jname=kwargs.get("jname"),
                utc=kwargs.get("utc"),
                beam=kwargs.get("beam"),
            )

            has_files, files = request_file_list(path, True)

            if has_files:
                returned_files = []
                for file in files:
                    if file["path"].endswith(".ar"):
                        returned_files.append(
                            JobControllerFile(
                                id=file["path"].split("/")[-1],
                                file_size=file["fileSize"],
                                is_dir=file["isDir"],
                                path=file["path"],
                            )
                        )
                return returned_files

        return []

    file_pulsar_list = relay.ConnectionField(
        FileConnection,
        jname=graphene.String(required=True),
    )

    @login_required
    def resolve_file_pulsar_list(self, info, **kwargs):

        path = get_fluxcal_archive_path(
            jname=kwargs.get("jname"),
        )
        has_files, files = request_file_list(path, True)

        if has_files:
            returned_files = []
            for file in files:
                if file["path"].endswith(".ar"):
                    returned_files.append(
                        JobControllerFile(
                            id=file["path"].split("/")[-1],
                            file_size=file["fileSize"],
                            is_dir=file["isDir"],
                            path=file["path"],
                        )
                    )
            return returned_files

        return []
