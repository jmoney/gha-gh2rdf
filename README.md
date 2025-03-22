# gha-gh2rdf

```plain
usage: main.py [-h] [--owner OWNER] [--repo REPO] [--org ORG] [--format FORMAT] (--issues | --pull-requests)

options:
  -h, --help       show this help message and exit
  --owner OWNER    Owner of the repo/org.
  --repo REPO      Name of the repo. Used in the context of issues to grab issues for a single repo. Multiple repos are not supported and need separate actions defined for each.
  --org ORG        Name of the org. Used in the context of pull requests. Used to grab pull requests across an organization
  --format FORMAT  Format of the output. Default is turtle. Options are xml, n3, turtle, nt, pretty-xml, trix, trig, nquads, json-ld, and hex.
  --issues         Include issues
  --pull-requests  Include pull requests
```
