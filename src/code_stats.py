"""Count default-branch source code without publishing repository details."""
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile
import zipfile

import requests


EXCLUDED_DIRS = "node_modules,vendor,dist,build,.venv,venv,__pycache__,coverage,.next,.nuxt"


def count_repository(repo):
    if repo.size == 0:
        return 0
    with tempfile.TemporaryDirectory(prefix="profile-loc-") as directory:
        root = Path(directory)
        archive = root / "source.zip"
        # PyGithub authenticates the archive request and returns a signed URL.
        url = repo.get_archive_link("zipball", repo.default_branch)
        with requests.get(url, stream=True, timeout=(30, 300)) as response:
            response.raise_for_status()
            with archive.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    output.write(chunk)
        source = root / "source"
        source.mkdir()
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                path = PurePosixPath(member.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in member.filename:
                    raise ValueError("Invalid archive path")
                # Ignore symlinks; only count regular files from the snapshot.
                if member.is_dir() or (member.external_attr >> 16) & 0o170000 == 0o120000:
                    continue
                target = source.joinpath(*path.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(member) as incoming, target.open("wb") as output:
                    shutil.copyfileobj(incoming, output)
        result = subprocess.run(
            ["cloc", "--json", "--quiet", "--skip-uniqueness", f"--exclude-dir={EXCLUDED_DIRS}", str(source)],
            check=True, capture_output=True, text=True, timeout=600,
        )
        return json.loads(result.stdout).get("SUM", {}).get("code", 0)


def get_code_totals(g):
    if not shutil.which("cloc"):
        raise RuntimeError("Install cloc to calculate lines of code")
    totals = {"public_lines_of_code": 0, "private_lines_of_code": 0}
    user = g.get_user()
    # Owner affiliation includes both public and private owned repositories.
    for repo in user.get_repos(affiliation="owner"):
        if repo.owner.login.lower() != user.login.lower():
            continue
        try:
            count = count_repository(repo)
        except Exception:
            # Do not leak private names, signed download URLs, or subprocess output.
            raise RuntimeError("Could not count a repository; profile update stopped to avoid incomplete totals") from None
        key = "private_lines_of_code" if repo.private else "public_lines_of_code"
        totals[key] += count
    totals["total_lines_of_code"] = sum(totals.values())
    return totals
