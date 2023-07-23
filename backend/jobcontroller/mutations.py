import graphene
from graphene import relay
from jobcontroller import request_file_download_id


class FileDownloadTokenMutation(relay.ClientIDMutation):
    class Input:
        path = graphene.String(required=True)

    download_token = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        success, token = request_file_download_id(input["path"])
        if success:
            return cls(download_token=token)

        return cls()


class Mutation(graphene.ObjectType):
    get_file_download_token = FileDownloadTokenMutation.Field()
