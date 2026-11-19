"""Links from diagram text to source lines at pinned commits.

A link entry is a tuple (pattern, ref, call_ref, condition):
  pattern    text matched inside a diagram text line (word boundaries respected); earlier entries win,
             so put full-line entries first
  ref        (repo, path, first_line, last_line) of the code or definition; lines None = whole file
  call_ref   optional call site; then the name links to the call site and a "↪" marker to the definition
  condition  optional dict: "y" (exact text y position after cropping) and/or "ctx" (substring of the line)

Local clones (needed for the code excerpts) are resolved, in this order, from
  1. the environment variable COUPLING_DIAGRAM_<REPO NAME IN UPPER CASE>, e.g. COUPLING_DIAGRAM_REMIND
  2. a JSON file {"remind": "C:/.../remind", ...} passed as `local_paths`
"""
import json
import os
import subprocess


class Repo:
    def __init__(self, name, url, commit):
        self.name, self.url, self.commit = name, url, commit
        self.local = None
        self._cache = {}

    def lines(self, path):
        """File content at the pinned commit (via git show in the local clone)."""
        if path not in self._cache:
            if not self.local:
                raise RuntimeError(f"no local clone configured for repository '{self.name}' "
                                   f"(set COUPLING_DIAGRAM_{self.name.upper()} or add it to the local paths file)")
            out = subprocess.run(["git", "-C", self.local, "show", f"{self.commit}:{path}"],
                                 capture_output=True, check=True)
            self._cache[path] = out.stdout.decode("utf-8", "replace").splitlines()
        return self._cache[path]


class LinkTable:
    def __init__(self, repos, links, relabel=None, local_paths=None):
        self.repos = {r.name: r for r in repos}
        self.links = links
        self.relabel = relabel or {}
        paths = {}
        if local_paths and os.path.exists(local_paths):
            with open(local_paths, encoding="utf-8") as f:
                paths = json.load(f)
        for r in self.repos.values():
            r.local = os.environ.get(f"COUPLING_DIAGRAM_{r.name.upper()}") or paths.get(r.name)

    def ref(self, repo):
        """Helper to build refs: R = table.ref("remind"); R("core/presolve.gms", 129, 131)."""
        def make(path, a=None, b=None):
            return (repo, path, a, b if b else a)
        return make
