<div align='center'>
  <img src='out/fetch.png' alt='Github Fetch'>
</div>

The profile shows one combined total of lines of code across all public and private
repositories owned by the authenticated user, including forks and archived repositories. It counts
the current default branch, excluding blank lines, comments, and common dependency
and build directories. This is repository code, not personal authorship or lifetime
lines added. Language statistics still cover public repositories.

The scheduled workflow installs `cloc`. For local runs, install `cloc` on your PATH
and the Python dependencies from `requirements.txt`, then run `python main.py`.
Store `GH_TOKEN` as a repository Actions secret with access to **all owned repositories**,
including private ones. Use a fine-grained token owned by your account with
All repositories selected and read-only Contents, Issues, and Pull requests
permissions (Metadata is included automatically). No account permissions are needed.
You can select No expiration. The workflow uses the separate built-in `GITHUB_TOKEN`
to push the generated image, so `GH_TOKEN` needs no write permissions. A restricted
token only counts repositories it can access. Never put a token in the README or config.

Only the combined line count is rendered; public/private breakdowns, private
repository names, and private source are not published. Downloaded snapshots are temporary. A counting failure stops the
update rather than publishing a partial total.
