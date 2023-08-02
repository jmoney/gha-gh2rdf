import argparse
import rdflib

from ghapi.all import GhApi

GITHUB_NS = rdflib.Namespace("https://api.github.com/")

if __name__ == "__main__":

    prog = argparse.ArgumentParser()
    prog.add_argument("--owner", type=str, required=True, help="Owner of the repo", dest="owner")
    prog.add_argument("--repo", type=str, required=True, help="Name of the repo", dest="repo")
    prog.add_argument("--format", type=str, required=False, default="turtle", help="Format of the output", dest="format")
    args = prog.parse_args()

    api = GhApi(owner=args.owner, repo=args.repo)
    # print(api.full_docs())

    default_ns = rdflib.Namespace(f"https://github.com/{args.owner}/{args.repo}/issues/")
    g = rdflib.Graph()
    g.bind("github", GITHUB_NS)
    g.bind("", default_ns)

    current_page = 1
    while True:
        issues = api.issues.list_for_repo(state="all", per_page=100, page=current_page)
        if len(issues) == 0:
            break

        print(current_page)

        for issue in issues:
            if "pull_request" in issue:
                continue

            iri = rdflib.URIRef(default_ns[str(issue.number)])
            g.add((iri, rdflib.RDF.type, rdflib.URIRef(GITHUB_NS.Issue)))
            g.add((iri, GITHUB_NS.issue_number, rdflib.Literal(issue.number)))
            g.add((iri, GITHUB_NS.url, rdflib.Literal(issue.html_url)))
            g.add((iri, GITHUB_NS.title, rdflib.Literal(issue.title)))
            g.add((iri, GITHUB_NS.state, rdflib.Literal(issue.state)))
            for assignee in issue.assignees:
                g.add((iri, GITHUB_NS.assignee, rdflib.Literal(assignee.login)))
            g.add((iri, GITHUB_NS.created_at, rdflib.Literal(issue.created_at, datatype=rdflib.XSD.dateTime)))
            g.add((iri, GITHUB_NS.updated_at, rdflib.Literal(issue.updated_at, datatype=rdflib.XSD.dateTime)))
            if issue.closed_at:
                g.add((iri, GITHUB_NS.closed_at, rdflib.Literal(issue.closed_at, datatype=rdflib.XSD.dateTime)))

        current_page += 1

    print(g.serialize(format=args.format))
