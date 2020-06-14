import datetime
import glob
import os
import os.path
import pprint
import subprocess
import sys
import tarfile
import tempfile
import time
from distutils.dir_util import copy_tree
from typing import List

import click
import docker  # type: ignore
import yaml
from halo import Halo  # type: ignore
from humanfriendly import format_size, parse_size  # type: ignore
from timeago import format as timeago_format  # type: ignore

from treebeard.buildtime.run_repo import run_repo
from treebeard.conf import (
    config_path,
    registry,
    treebeard_config,
    treebeard_env,
    validate_notebook_directory,
)
from treebeard.helper import CliContext, sanitise_notebook_id, update
from treebeard.secrets.helper import get_secrets_archive

pp = pprint.PrettyPrinter(indent=2)

notebook_id = treebeard_env.notebook_id
project_id = treebeard_env.project_id


@click.command()
@click.option(
    "watch", "--watch", is_flag=True, help="Run and check completed build status"
)
@click.option("-n", "--notebooks", help="Notebooks to be run", multiple=True)
@click.option(
    "-i",
    "--ignore",
    help="Don't submit unneeded virtual envs and large files",
    multiple=True,
)
@click.option(
    "--confirm/--no-confirm", default=False, help="Confirm all prompt options"
)
@click.option(
    "--push-secrets/--no-push-secrets",
    default=False,
    help="Confirm all prompt options except pushing secrets",
)
@click.option(
    "--dockerless/--no-dockerless",
    default=False,
    help="Run locally without docker container",
)
@click.option(
    "--upload/--no-upload", default=False, help="Upload outputs",
)
@click.pass_obj  # type: ignore
def run(
    cli_context: CliContext,
    watch: bool,
    notebooks: List[str],
    ignore: List[str],
    confirm: bool,
    push_secrets: bool,
    dockerless: bool,
    upload: bool,
):
    """
    Run a notebook and optionally schedule it to run periodically
    """
    notebooks = list(notebooks)
    ignore = list(ignore)

    validate_notebook_directory(treebeard_env, treebeard_config)

    # Apply cli config overrides
    treebeard_yaml_path: str = tempfile.mktemp()  # type: ignore
    with open(treebeard_yaml_path, "w") as yaml_file:
        if notebooks:
            treebeard_config.notebooks = notebooks

        yaml.dump(treebeard_config.dict(), yaml_file)  # type: ignore

    if upload or not dockerless:
        update(status="WORKING")

    if dockerless:
        click.echo(
            f"🌲  Running locally without docker using your current python environment"
        )
        if not confirm and not click.confirm(
            f"Warning: This will clear the outputs of your notebooks, continue?",
            default=True,
        ):
            sys.exit(0)

        # Note: import runtime.run causes win/darwin devices missing magic to fail at start
        import treebeard.runtime.run

        treebeard.runtime.run.start(upload_outputs=upload)  # will sys.exit

    params = {}
    if treebeard_config.schedule:
        if confirm or click.confirm(
            f"📅 treebeard.yaml contains schedule '{treebeard_config.schedule}'. Enable it?"
        ):
            params["schedule"] = treebeard_config.schedule

    if treebeard_config:
        ignore += (
            treebeard_config.ignore
            + treebeard_config.secret
            + treebeard_config.output_dirs
        )

    click.echo("🌲  Copying project to tempdir and stripping notebooks")

    temp_dir = tempfile.mkdtemp()
    copy_tree(os.getcwd(), str(temp_dir), preserve_symlinks=1)
    notebooks_files = treebeard_config.get_deglobbed_notebooks()
    for notebooks_file in notebooks_files:
        try:
            subprocess.check_output(["nbstripout"] + notebooks_file, cwd=temp_dir)
        except:
            print(f"Failed to nbstripout {notebooks_file}! Is it valid?")
    click.echo(notebooks_files)
    click.echo("🌲  Compressing Repo")

    with tempfile.NamedTemporaryFile(
        "wb", suffix=".tar.gz", delete=False
    ) as src_archive:
        with tarfile.open(fileobj=src_archive, mode="w:gz") as tar:

            def zip_filter(info: tarfile.TarInfo):
                if info.name.endswith("treebeard.yaml"):
                    return None

                for ignored in ignore:
                    if info.name in glob.glob(ignored, recursive=True):
                        return None

                # if len(git_files) > 0 and info.name not in git_files:
                #     return None
                click.echo(f"  Including {info.name}")
                return info

            tar.add(
                str(temp_dir), arcname=os.path.basename(os.path.sep), filter=zip_filter,
            )
            tar.add(config_path, arcname=os.path.basename(config_path))
            tar.add(treebeard_yaml_path, arcname="treebeard.yaml")

    if not confirm and not click.confirm(
        "Confirm source file set is correct?", default=True
    ):
        click.echo("Exiting")
        sys.exit()

    build_tag = str(time.mktime(datetime.datetime.today().timetuple()))
    repo_image_name = (
        f"{registry}/{project_id}/{sanitise_notebook_id(str(notebook_id))}:{build_tag}"
    )
    click.echo(f"🌲  Building {repo_image_name} Locally\n")
    secrets_archive = get_secrets_archive()
    repo_url = f"file://{src_archive.name}"
    secrets_url = f"file://{secrets_archive.name}"
    status = run_repo(
        str(project_id),
        str(notebook_id),
        treebeard_env.run_id,
        build_tag,
        repo_url,
        secrets_url,
        branch="cli",
    )
    click.echo(f"Local build exited with status code {status}")
    sys.exit(status)
