# Platform Pulse (app)

The dashboard deployed by the Platform Pulse POC. Shows the git SHA and
build time it was built with (baked in at image build time), the pod/node
it's running on (Kubernetes Downward API — set once the Helm chart wires
it, Phase 5), and a live hit counter in DynamoDB via IRSA (no static AWS
keys — see `Platform-pulse-infra-project`'s `modules/irsa`).

## CI

`.github/workflows/ci.yml` builds and pushes to ECR on every push to `main`,
authenticating via GitHub's OIDC provider to an IAM role scoped to this
repo's `main` branch only (`Platform-pulse-infra-project`'s `modules/github-actions-role`)
— no access keys stored in GitHub at all.

Images are tagged with the commit SHA only (never `latest` — the ECR repo
is `IMMUTABLE`, so a reused tag would fail the second push). This also
matches what Phase 6's ArgoCD GitOps tag-bump expects.

## Local run

```bash
pip install -r requirements.txt
DYNAMODB_TABLE=platform-pulse-dev-hits AWS_REGION=us-east-1 python app.py
```

Needs local AWS credentials with access to that table to actually increment
the counter; without `DYNAMODB_TABLE` set, the page still renders with
"N/A" in place of the visit count.
