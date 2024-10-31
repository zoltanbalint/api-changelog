# read all .json files from changelog/ folder, sorted asc and create a changelog.html file
# with all the changes from the json files
import json
import os
import re
import datetime
import markdown
from dotenv import load_dotenv

def changelog():
    load_dotenv()
    branding = os.getenv("BRAND_NAME")
    apidoc_url = os.getenv("APIDOC_URL")

    changelog_rows = {}
    for file in sorted(os.listdir("changelog/html"), reverse=True):
        if file.endswith(".html"):
            with open("changelog/html/" + file, "r") as f:
                # read html
                data = f.read()
                # extract content from HTML <body> tag
                body = re.search(r'<body>(.*)</body>', data, re.DOTALL).group(1)
                # remove <div class="title">...</div> from body
                body = re.sub(r'<div class="title">.*</div>', "", body)
                body = body.strip()

                if len(body) == 0:
                    continue

                # filename = {timestamp}-{git hash}.json
                timestamp = file.split("-")[0]
                git_hash = file.split("-")[1].split(".")[0]

                # load metadata json
                metadata = json.load(open("changelog/metadata/" + file.replace(".html", ".metadata.json"), "r"))

                # html row: date, link to git commit, changes
                summary = dump_summary(metadata)
                day = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
                if day not in changelog_rows:
                    changelog_rows[day] = []
                changelog_rows[day].append(f"""
                <div class="section">
                    {summary}
                    <div class="separator"></div>
                    {body}
                </div>
    """)

    # dump to index.html file based on template.html, replace {{ROWS}} with html_rows

    html_rows = []
    for day, rows in changelog_rows.items():
        row = f"""<h2 class="title"><span class="dot"></span> {day}</h2>"""
        html_rows.append(
            f"""<h2 class="title"><span class="dot"></span> {day}</h2>""" +
            "\n".join(rows)
        )

    with open("template.html", "r") as f:
        template = f.read()
        with open("index.html", "w") as index_f:
            index_f.write(
                template
                    .replace("{{ BRAND_NAME }}", branding)
                    .replace("{{ APIDOC_URL }}", apidoc_url)
                    .replace("{{ ROWS }}", "\n".join(html_rows)
            )
    )


def dump_summary(_metadata: dict) -> str:
    rows = []


    for commit in _metadata['commits']:
        message = commit['message'].split("\n")
        # extract first line from commit message
        title = message[0]
        content = "\n".join(message[1:])

        rows.append(f"""
        <div class="summary">
            <a class="small d-block" target="_blank" href="{commit['url']}">view on GitHub &raquo; {commit['id'][:8]}</a>
            <strong>{title}</strong>
            <div class="content">
                {markdown.markdown(content)}
            </div>
        </div>
        """)
    return "\n".join(rows)


if __name__ == "__main__":
    changelog()