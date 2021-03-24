import logging
from tables.graphql_table import GraphQLTable
from base64 import b64encode


def prepare_image(img_fn):
    """
    open a file and encode contents in base64 for submission via graphql
    this ensures that all characters we're sending are acceptable

    input:
    img_fn: string with file name to the image file (we do not verify the file is really an image)

    returns: b64-encoded string with contents of the file
    """
    img_bytes = ""
    if img_fn and img_fn != '""':
        with open(img_fn, "rb") as fh:
            img_bytes = fh.read()
    # provided file name could point to an empty file
    if img_bytes:
        # encode and strip the bytes marker
        img_bytes = str(b64encode(img_bytes))[2:-1]

    return img_bytes


class Pipelineimages(GraphQLTable):
    def __init__(self, client, url, token):
        GraphQLTable.__init__(self, client, url, token)

        # create a new record
        self.create_mutation = """
        mutation ($image: String!, $image_type: String!, $processing_id: Int!, $rank: Int!) {
            createPipelineimage (input: {image: $image, image_type: $image_type, processing_id: $processing_id, rank: $rank}) {
                pipelineimage {
                    id
                }
            }
        }
        """

        self.field_names = ["id", "image", "imageType", "rank", "processing {id}"]

    def list_graphql(self, id):
        if id is not None:
            self.list_query = self.build_list_id_query("pipelineimage", id)
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())
        else:
            self.list_query = self.build_list_all_query()
            self.list_variables = "{}"
            return GraphQLTable.list_graphql(self, ())

    def process(self, args):
        """Parse the arguments collected by the CLI."""
        if args.subcommand == "create":
            image = prepare_image(args.image)
            self.create_variables = {
                "image": image,
                "image_type": args.image_type,
                "rank": args.rank,
                "processing_id": args.processing_id,
            }
            return self.create_graphql()
        elif args.subcommand == "list":
            return self.list_graphql(args.id)

    @classmethod
    def get_name(cls):
        return "pipelineimages"

    @classmethod
    def get_description(cls):
        return "A pipelineimage with type and rank informing the position of the image"

    @classmethod
    def configure_parsers(cls, parser):
        """Add sub-parsers for each of the valid commands."""
        parser.set_defaults(command=cls.get_name())
        subs = parser.add_subparsers(dest="subcommand")
        subs.required = True

        # create the parser for the "list" command
        parser_list = subs.add_parser("list", help="list existing Pipelineimages")
        parser_list.add_argument("--id", type=int, help="list Pipelineimages matching the id")

        # create the parser for the "create" command
        parser_create = subs.add_parser("create", help="create a new pipelineimage")
        parser_create.add_argument(
            "image_type", type=str, help='description of image type, e.g., "flux" or "snr" or "bandpass"'
        )
        parser_create.add_argument("processing_id", type=int, help="id of the related processing")
        parser_create.add_argument(
            "rank", type=int, help="rank of the image, used to indicate the order of displaing the image"
        )
        parser_create.add_argument("image", type=str, help="path to the image to be uploaded")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    Pipelineimages.configure_parsers(parser)
    args = parser.parse_args()

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    from cli.graphql_client import GraphQLClient

    client = GraphQLClient(args.url, args.very_verbose)
    p = Pipelineimages(client, args.url, args.token[0])
    response = p.process(args)
