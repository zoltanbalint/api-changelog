# read all .json files from changelog/ folder, sorted asc and create a changelog.html file
# with all the changes from the json files

import os
import re
import datetime

# read all json files from versions/ folder
html_rows = []
for file in os.listdir("changelog/html"):
    if file.endswith(".html"):
        with open("changelog/html/" + file, "r") as f:
            # filename = {timestamp}-{git hash}.json
            timestamp = file.split("-")[0]
            git_hash = file.split("-")[1].split(".")[0]
            # read html
            data = f.read()
            # extract content from HTML <body> tag
            body = re.search(r'<body>(.*)</body>', data, re.DOTALL).group(1)
            # remove <div class="title">...</div> from body
            body = re.sub(r'<div class="title">.*</div>', "", body)
            # html row: date, link to git commit, changes
            html_rows.append(f"""
            <div>
                <div class="title">{datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M')}</div>
                <div class="link"><a href="#{git_hash}">View code changes [{git_hash[:8]}]</a></div>
                {body}
                <ul>
            </div>
""")

# dump to index.html file based on template.html, replace {{ROWS}} with html_rows

with open("template.html", "r") as f:
    template = f.read()
    with open("index.html", "w") as index_f:
        index_f.write(template.replace("{{ROWS}}", "\n".join(html_rows))
)