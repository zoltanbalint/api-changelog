# read all .json files from changelog/ folder, sorted asc and create a changelog.html file
# with all the changes from the json files
import json
import os
import re
import datetime
import markdown
from dotenv import load_dotenv

load_dotenv()

def changelog():
    branding = os.getenv("BRAND_NAME")
    apidoc_url = os.getenv("APIDOC_URL")

    changelog_rows = {}
    for file in sorted(os.listdir("../changelog/html"), reverse=True):
        if file.endswith(".html"):
            with open("../changelog/html/" + file, "r") as f:
                data = f.read()
                body = re.search(r'<body>(.*)</body>', data, re.DOTALL).group(1)
                body = re.sub(r'<div class="title">.*</div>', "", body)
                body = body.strip()

                if len(body) == 0:
                    continue

                timestamp = file.split("-")[0]

                metadata = json.load(open("../changelog/metadata/" + file.replace(".html", ".metadata.json"), "r"))

                summary = dump_section_summary(metadata)
                day = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
                if day not in changelog_rows:
                    changelog_rows[day] = []
                changelog_rows[day].append(dump_section_row(summary, body))

    section_rows = []
    for day, rows in changelog_rows.items():
        section_rows.append(dump_section(day, rows))

    with open("templates/base.html", "r") as f:
        template = f.read()
        with open("../index.html", "w") as index_f:
            index_f.write(
                template
                    .replace("{{ BRAND_NAME }}", branding)
                    .replace("{{ APIDOC_URL }}", apidoc_url)
                    .replace("{{ BODY }}", replace_jira_links("\n".join(section_rows))
            )
    )

def dump_section(day: str, rows: list) -> str:
    with open("templates/_section.html", "r") as f:
        section_template = f.read()
        return section_template.replace("{{ TITLE }}", day).replace("{{ BODY }}", "\n".join(rows))

def dump_section_summary(_metadata: dict) -> str:
    rows = []

    with open("templates/_summary.html", "r") as f:
        summary_template = f.read()

    for commit in _metadata['commits']:
        message = commit['message'].split("\n")

        title = message[0]
        content = ("\n".join(message[1:])).strip()

        rows.append(
            summary_template
                .replace("{{ TITLE }}", markdown.markdown(title))
                .replace("{{ BODY }}", markdown.markdown(content))
                .replace("{{ GITHUB_COMMIT_URL }}", commit['url'])
                .replace("{{ GITHUB_COMMIT_ID }}", commit['id'][:8])
        )
    return "\n".join(rows)

def dump_section_row(summary: str, body: str) -> str:
    with open("templates/_section_row.html", "r") as f:
        section_template = f.read()
        return section_template.replace("{{ SUMMARY }}", summary).replace("{{ BODY }}", body)

def replace_jira_links(content: str) -> str:
    jira_pattern = os.getenv("JIRA_PATTERN")
    jira_url = os.getenv("JIRA_URL")
    return re.sub(rf"({jira_pattern})", rf'''<a class="jira external-link" target="_blank" href="{jira_url}\1">\1</a>''', content)


if __name__ == "__main__":
    changelog()