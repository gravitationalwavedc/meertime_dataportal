import logging
import sys

from tables.basebandings import Basebandings
from tables.calibrations import Calibrations
from tables.collections import Collections
from tables.ephemerides import Ephemerides
from tables.foldings import Foldings
from tables.filterbankings import Filterbankings
from tables.instrumentconfigs import Instrumentconfigs
from tables.launches import Launches
from tables.observations import Observations
from tables.pipelines import Pipelines
from tables.processingcollections import Processingcollections
from tables.processings import Processings
from tables.projects import Projects
from tables.pulsars import Pulsars
from tables.pulsartargets import Pulsartargets
from tables.targets import Targets
from tables.telescopes import Telescopes
from graphql_client import GraphQLClient

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--token", nargs=1, help="JWT token")
    parser.add_argument("-u", "--url", nargs=1, default=["http://127.0.0.1:8000/graphql/",], help="GraphQL URL")
    parser.add_argument(
        "-l",
        "--literal",
        action="store_true",
        default=False,
        help="Return literal IDs in tables instead of more human readable text",
    )
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Increase verbosity")
    parser.add_argument("-vv", "--very_verbose", action="store_true", default=False, help="Increase verbosity")

    subparsers = parser.add_subparsers(dest="command", help="Database models which can be interrogated")
    subparsers.required = True

    tables = [
        Basebandings,
        Calibrations,
        Collections,
        Ephemerides,
        Filterbankings,
        Foldings,
        Instrumentconfigs,
        Launches,
        Observations,
        Processingcollections,
        Processings,
        Projects,
        Pulsars,
        Pulsartargets,
        Pipelines,
        Telescopes,
        Targets,
    ]
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
            client = GraphQLClient(args.url[0], args.very_verbose)
            table = c["table"](client, args.url[0], args.token[0])
            table.set_literal(args.literal)
            response = table.process(args)
            if args.verbose or args.very_verbose:
                import json

                print(response.status_code)
                print(json.loads(response.content))
