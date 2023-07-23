import graphene
from graphene import relay
from jobcontroller import request_file_list, get_fluxcal_archive_path


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
        project=graphene.String(required=True),
        jname=graphene.String(required=True),
        utc=graphene.String(required=True),
        beam=graphene.Int(required=True),
        band=graphene.Int(required=True),
    )

    def resolve_file_list(self, info, **kwargs):
        path = get_fluxcal_archive_path(**kwargs)
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
