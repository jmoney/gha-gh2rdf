import argparse
import datetime
import dateutil.parser
import rdflib
import time

from ghapi.all import GhApi

GITHUB_NS = rdflib.Namespace("https://api.github.com/")

def issues(g: rdflib.Graph, owner: str, repo: str):
    api = GhApi(owner=owner, repo=repo)
    # print(api.full_docs())

    default_ns = rdflib.Namespace(f"https://github.com/{owner}/{repo}/issues/")
    g.bind("", default_ns)

    current_page = 1
    while True:
        issues = api.issues.list_for_repo(state="all", per_page=100, page=current_page)
        if len(issues) == 0:
            break

        for issue in issues:
            if "pull_request" in issue:
                continue

            iri = rdflib.URIRef(default_ns[str(issue.number)])
            
            iso_created_at = dateutil.parser.isoparse(issue.created_at)
            iso_updated_at = dateutil.parser.isoparse(issue.updated_at)
            iso_closed_at = dateutil.parser.isoparse(issue.closed_at) if issue.closed_at else None
            g.add((iri, rdflib.RDF.type, rdflib.URIRef(GITHUB_NS.Issue)))
            g.add((iri, GITHUB_NS.issue_number, rdflib.Literal(issue.number)))
            g.add((iri, GITHUB_NS.url, rdflib.Literal(issue.html_url)))
            g.add((iri, GITHUB_NS.title, rdflib.Literal(issue.title)))
            g.add((iri, GITHUB_NS.state, rdflib.Literal(issue.state)))
            for assignee in issue.assignees:
                g.add((iri, GITHUB_NS.assignee, rdflib.Literal(assignee.login)))
            g.add((iri, GITHUB_NS.created_at, rdflib.Literal(issue.created_at, datatype=rdflib.XSD.dateTime)))
            g.add((iri, GITHUB_NS.created_on, rdflib.Literal(iso_created_at.date(), datatype=rdflib.XSD.date)))
            g.add((iri, GITHUB_NS.updated_at, rdflib.Literal(issue.updated_at, datatype=rdflib.XSD.dateTime)))
            g.add((iri, GITHUB_NS.updated_on, rdflib.Literal(iso_updated_at.date(), datatype=rdflib.XSD.date)))
            if issue.closed_at:
                g.add((iri, GITHUB_NS.closed_at, rdflib.Literal(issue.closed_at, datatype=rdflib.XSD.dateTime)))
                g.add((iri, GITHUB_NS.closed_on, rdflib.Literal(iso_closed_at.date(), datatype=rdflib.XSD.date)))

        current_page += 1

def pull_requests(g: rdflib.Graph, owner: str, org: str):
    api = GhApi(owner=owner)
    # print(api.full_docs())

    default_ns = rdflib.Namespace(f"https://github.com/{owner}/pulls/")
    g.bind("", default_ns)

    current_page = 1
    search_strings = {
        "created": f"is:pr archived:false user:{org} author:{owner} ",
        "assigned": f"is:pr archived:false user:{org} assignee:{owner}",
        "mentioned": f"is:pr archived:false user:{org} mentioned:{owner}",
        "review-requested": f"is:pr archived:false user:{org} review-requested:{owner}",
    }
    for type, search_string in search_strings.items():
        current_page = 1
        while True:
            if current_page >= 10:
                break

            pulls = api.search.issues_and_pull_requests(q=search_string, per_page=100, page=current_page)
            if len(pulls) == 0:
                break

            for pull in pulls['items']:

                iri = rdflib.URIRef(default_ns[str(pull.number)])
                g.add((iri, GITHUB_NS.search_string, rdflib.Literal(search_string)))
                g.add((iri, GITHUB_NS.search_type, rdflib.Literal(type)))
                
                iso_created_at = dateutil.parser.isoparse(pull.created_at)
                iso_updated_at = dateutil.parser.isoparse(pull.updated_at)
                iso_closed_at = dateutil.parser.isoparse(pull.closed_at) if pull.closed_at else None
                iso_merged_at = dateutil.parser.isoparse(pull.pull_request.merged_at) if pull.pull_request.merged_at else None
                g.add((iri, rdflib.RDF.type, rdflib.URIRef(GITHUB_NS.PullRequest)))
                g.add((iri, GITHUB_NS.pull_number, rdflib.Literal(pull.number)))
                g.add((iri, GITHUB_NS.repo, rdflib.Literal("/".join(pull.repository_url.split("/")[-2:]))))
                g.add((iri, GITHUB_NS.url, rdflib.Literal(pull.html_url)))
                g.add((iri, GITHUB_NS.title, rdflib.Literal(pull.title)))
                g.add((iri, GITHUB_NS.state, rdflib.Literal(pull.state)))
                g.add((iri, GITHUB_NS.state_reason, rdflib.Literal(pull.state_reason)))
                g.add((iri, GITHUB_NS.merged, rdflib.Literal(pull.pull_request.merged_at is not None, datatype=rdflib.XSD.boolean)))
                if pull.pull_request.merged_at is not None:
                    g.add((iri, GITHUB_NS.merged_at, rdflib.Literal(pull.pull_request.merged_at, datatype=rdflib.XSD.dateTime)))
                    g.add((iri, GITHUB_NS.merged_on, rdflib.Literal(iso_merged_at.date(), datatype=rdflib.XSD.date)))
                for assignee in pull.assignees:
                    g.add((iri, GITHUB_NS.assignee, rdflib.Literal(assignee.login)))
                g.add((iri, GITHUB_NS.created_at, rdflib.Literal(pull.created_at, datatype=rdflib.XSD.dateTime)))
                g.add((iri, GITHUB_NS.created_on, rdflib.Literal(iso_created_at.date(), datatype=rdflib.XSD.date)))
                g.add((iri, GITHUB_NS.updated_at, rdflib.Literal(pull.updated_at, datatype=rdflib.XSD.dateTime)))
                g.add((iri, GITHUB_NS.updated_on, rdflib.Literal(iso_updated_at.date(), datatype=rdflib.XSD.date)))
                if pull.closed_at:
                    g.add((iri, GITHUB_NS.closed_at, rdflib.Literal(pull.closed_at, datatype=rdflib.XSD.dateTime)))
                    g.add((iri, GITHUB_NS.closed_on, rdflib.Literal(iso_closed_at.date(), datatype=rdflib.XSD.date)))

            current_page += 1
        time.sleep(60)

if __name__ == "__main__":

    prog = argparse.ArgumentParser()
    prog.add_argument("--owner", type=str, required=False, help="Owner of the repo", dest="owner")
    prog.add_argument("--repo", type=str, required=False, help="Name of the repo", dest="repo")
    prog.add_argument("--org", type=str, required=False, help="Name of the org", dest="org")
    prog.add_argument("--format", type=str, required=False, default="turtle", help="Format of the output", dest="format")

    type_group = prog.add_mutually_exclusive_group(required=True)
    type_group.add_argument("--issues", action="store_true", help="Include issues", dest="issues")
    type_group.add_argument("--pull-requests", action="store_true", help="Include pull requests", dest="pull_requests")

    args = prog.parse_args()

    g = rdflib.Graph()
    g.bind("github", GITHUB_NS)

    if args.issues:
        issues(g, args.owner, args.repo)
    elif args.pull_requests:
        pull_requests(g, owner=args.owner, org=args.org)

    print(g.serialize(format=args.format))