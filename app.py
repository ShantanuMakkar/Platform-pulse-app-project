import os

import boto3
from flask import Flask, render_template_string

app = Flask(__name__)

GIT_SHA = os.environ.get("GIT_SHA", "unknown")
BUILD_TIME = os.environ.get("BUILD_TIME", "unknown")
POD_NAME = os.environ.get("POD_NAME", "unknown")
NODE_NAME = os.environ.get("NODE_NAME", "unknown")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION) if DYNAMODB_TABLE else None

PAGE = """
<!doctype html>
<html>
<head>
  <title>Platform Pulse</title>
  <style>
    body { font-family: -apple-system, sans-serif; background: #0d1117; color: #e6edf3;
           display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
    .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; width: 320px; }
    h1 { font-size: 18px; margin: 0 0 4px; }
    .sub { color: #8b949e; font-size: 13px; margin-bottom: 16px; }
    .stat { background: #0d1117; border-radius: 8px; padding: 12px 14px; margin-bottom: 8px; }
    .label { font-size: 12px; color: #8b949e; }
    .value { font-size: 20px; font-weight: 600; }
    .row { display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-top: 1px solid #21262d; }
    .row span:first-child { color: #8b949e; }
    code { font-family: monospace; font-size: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Platform Pulse</h1>
    <div class="sub">Deployed on EKS via ArgoCD</div>
    <div class="stat">
      <div class="label">Visits</div>
      <div class="value">{{ visits }}</div>
    </div>
    <div class="row"><span>Git SHA</span><span><code>{{ git_sha }}</code></span></div>
    <div class="row"><span>Built</span><span>{{ build_time }}</span></div>
    <div class="row"><span>Pod</span><span><code>{{ pod_name }}</code></span></div>
    <div class="row"><span>Node</span><span><code>{{ node_name }}</code></span></div>
  </div>
</body>
</html>
"""


def increment_visits():
    if dynamodb is None:
        return "N/A (no DYNAMODB_TABLE set)"
    table = dynamodb.Table(DYNAMODB_TABLE)
    resp = table.update_item(
        Key={"counter_id": "platform-pulse"},
        UpdateExpression="ADD visits :inc",
        ExpressionAttributeValues={":inc": 1},
        ReturnValues="UPDATED_NEW",
    )
    return int(resp["Attributes"]["visits"])


@app.route("/")
def index():
    return render_template_string(
        PAGE,
        visits=increment_visits(),
        git_sha=GIT_SHA,
        build_time=BUILD_TIME,
        pod_name=POD_NAME,
        node_name=NODE_NAME,
    )


@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
