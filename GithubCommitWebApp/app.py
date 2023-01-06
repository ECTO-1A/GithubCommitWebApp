import requests
import json

from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index2.html")


@app.route("/commits", methods=["POST"])
def fetch_commit_links():
    # Get the repository URL from the form
    repo_url = request.form["repo_url"]

    # Extract the repository owner and name from the URL
    parts = repo_url.split("/")
    owner = parts[3]
    repo = parts[4]

    # Get the security token from the form
    token = request.form["token"]

    # Get the start and end dates for the commit search
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    if token != "":
        # Add the Authorization header with the bearer token
        headers = {"Authorization": f"Bearer {token}"}
    else:
        # Don't include the Authorization header
        headers = {}

    # Make a request to the GitHub API to get the list of commits
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {"since": start_date, "until": end_date}
    response = requests.get(api_url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Load the response data
        data = json.loads(response.text)

        # Create a list of commit links
        commit_links = []
        for commit in data:
            commit_url = commit["html_url"]
            api_url = commit["url"]
            commit_links.append(api_url)

        # Retrieve the commit statistics for each commit
        commit_stats = []
        for api_url in commit_links:
            response = requests.get(api_url)
            data2 = response.json()
            stats = data2["stats"]["total"]
            commit_stats.append(stats)

        commit_data = []
        for i, commit in enumerate(data):
            commit_url = commit["html_url"]
            api_url = commit["url"]
            stats = commit_stats[i]
            commit_data.append({"url": commit_url, "stats": stats})

        return render_template(
            "commits.html",
            commit_data=commit_data,
        )
    else:
        return render_template(
            "error.html",
            error="An error occurred while trying to fetch the commit links.",
        )


if __name__ == "__main__":
    app.run()
