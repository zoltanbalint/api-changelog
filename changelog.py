# read all .json files from changelog/ folder, sorted asc and create a changelog.html file
# with all the changes from the json files
import json
import os
import re
import datetime
import markdown

def changelog():
    html_rows = []
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
                html_rows.append(f"""
                <div class="section">
                    <h2 class="title"><span class="dot"></span> {datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')}</h2>
                    {summary}
                    <div class="separator"></div>
                    {body}
                </div>
    """)

    # dump to index.html file based on template.html, replace {{ROWS}} with html_rows

    with open("template.html", "r") as f:
        template = f.read()
        with open("index.html", "w") as index_f:
            index_f.write(template.replace("{{ ROWS }}", "\n".join(html_rows))
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
            <strong>{title}</strong>
            <div class="content">
                {markdown.markdown(content)}
                <div class="link"><a target="_blank" href="{commit['url']}">View code changes [{commit['id'][:8]}]</a></div>
            </div>
        </div>
        """)
    return "\n".join(rows)


if __name__ == "__main__":
    changelog()