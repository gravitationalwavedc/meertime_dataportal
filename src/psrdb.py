import logging
import sys

from cli.tables.pulsars import Pulsars
from cli.tables.targets import Targets
from cli.tables.pipelines import Pipelines
from cli.graphql_client import GraphQLClient

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default="http://127.0.0.1:8000/graphql/", help="GraphQL URL")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    subparsers = parser.add_subparsers(dest='command', required=True, help='Database models which can be interrogated')

    tables = [Pulsars, Targets, Pipelines]
    configured = []
    for t in tables:
        n = t.get_name()
        p = subparsers.add_parser(n, help=t.get_description())
        t.configure_parsers(p)
        configured.append({"name": n, "parser": p, "table": t})

    args = parser.parse_args()
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if args.verbose:
        logging.basicConfig(format=format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=format, level=logging.INFO)

    for c in configured:
        if args.command == c["name"]:
            client = GraphQLClient(args.url, args.very_verbose)
            table = c["table"](client, args.url, args.token[0])
            response = table.process(args)
            if args.verbose:
                import json

                print(response.status_code)
                print(json.loads(response.content))
