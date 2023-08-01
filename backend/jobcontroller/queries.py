import graphene
from graphene import relay
from jobcontroller import request_file_list, get_fluxcal_archive_path
from web_cache.models import FoldPulsarDetail
from graphql_jwt.decorators import login_required


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
    file_list = relay.ConnectionField(
        FileConnection,
        jname=graphene.String(required=True),
        utc=graphene.String(required=True),
        beam=graphene.Int(required=True),
    )

    @login_required
    def resolve_file_list(self, info, **kwargs):

        fold_pulsar_detail = FoldPulsarDetail.objects.get(
            fold_pulsar__jname=kwargs.get("jname"),
            utc=FoldPulsarDetail.format_utc(kwargs.get("utc")),
            beam=kwargs.get("beam"),
        )

        # Only allow files if the user passes has access to this
        # fold pulsar observation.
        if not fold_pulsar_detail.is_restricted(info.context.user):
            path = get_fluxcal_archive_path(
                project=fold_pulsar_detail.project,
                jname=kwargs.get("jname"),
                utc=kwargs.get("utc"),
                beam=kwargs.get("beam"),
                band=fold_pulsar_detail.get_band_centre_frequency(),
            )

            has_files, files = request_file_list(path, False)

            if has_files:
                return [
                    JobControllerFile(
                        id=file["path"].split("/")[-1],
                        file_size=file["fileSize"],
                        is_dir=file["isDir"],
                        path=file["path"],
                    )
                    for file in files
                ]

        return []
