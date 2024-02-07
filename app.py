#!/usr/bin/env python3
from argparse import ArgumentParser
import os

import okta_graph.api
from okta_graph.api import OktaGraphServer
from okta_graph.cache import OktaFileCache


OKTA_TOKEN = os.environ["OKTA_TOKEN"]
graph_mod_path = os.path.abspath(os.path.dirname(okta_graph.api.__file__))

parser = ArgumentParser()
parser.add_argument(
    "--temp-dir", help="Prefix for storing temp files.", type=str, default="/tmp"
)
parser.add_argument(
    "--static-dir",
    help="The root from which static content is served.",
    type=str,
    default=os.path.join(graph_mod_path, "static"),
)
args = parser.parse_args()


cache = OktaFileCache(
    okta_org="hingehealth-wf",
    okta_token=OKTA_TOKEN,
    persist=True,
    refresh_interval=5,
    groups_file="cached_groups.json",
    rules_file="cached_rules.json",
)


def icon_selector(self: object, data: dict):
    node_images = {
        "Okta Group": f"{self.icon_dir}/group.png",
        "AWS Group": f"{self.icon_dir}/aws.png",
        "Okta Group Rule": f"{self.icon_dir}/rule.png",
        "Okta User": f"{self.icon_dir}/user.png",
        "Manual Group Assignment": f"{self.icon_dir}/manual_group.png",
    }

    if data["type"] == "Okta Group" and data["name"].startswith("AWS_"):
        icon = node_images["AWS Group"]
    else:
        icon = node_images.get(data["type"])

    return icon


def main():
    server = OktaGraphServer(
        cache=cache,
        temp_dir=args.temp_dir,
        static_content_dir=args.static_dir,
        icon_selector=icon_selector,
    )

    server.run(reload=False)


main()
