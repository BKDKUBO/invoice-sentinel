#!/usr/bin/env bash
# Deploy InvoiceSentinel (API + web) to Google Cloud Run.
# Prereqs: gcloud logged in, billing enabled, secret "gemini-api-key" exists
#   printf %s "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
set -euo pipefail
PROJECT="${PROJECT:-gen-lang-client-0252871691}"
REGION="${REGION:-asia-southeast1}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
gcloud config set project "$PROJECT" >/dev/null
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
PN=$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PN}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor >/dev/null

# --- API (FastAPI). Seed cases are baked into the image and copied on startup. ---
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -r "$ROOT/api/." "$TMP/"; rm -rf "$TMP/__pycache__"
cp "$TMP/Dockerfile.standalone" "$TMP/Dockerfile"
gcloud run deploy invoicesentinel-api --source "$TMP" --region "$REGION" \
  --port 8080 --cpu 1 --memory 512Mi --min-instances 0 --max-instances 2 --timeout 120 \
  --allow-unauthenticated --set-secrets GEMINI_API_KEY=gemini-api-key:latest --quiet
API_URL=$(gcloud run services describe invoicesentinel-api --region "$REGION" --format='value(status.url)')

# --- Web (Next.js). NEXT_PUBLIC_API_URL is inlined at build time. ---
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/cloud-run-source-deploy/invoicesentinel-web:$(date +%s)"
gcloud builds submit "$ROOT/web" --region "$REGION" --config "$ROOT/deploy/cloudbuild-web.yaml" \
  --substitutions "_IMAGE=${IMAGE},_API_URL=${API_URL}"
gcloud run deploy invoicesentinel-web --image "$IMAGE" --region "$REGION" \
  --port 3000 --cpu 1 --memory 512Mi --min-instances 0 --max-instances 2 --allow-unauthenticated --quiet
WEB_URL=$(gcloud run services describe invoicesentinel-web --region "$REGION" --format="value(status.url)")
WEB_URLS=$(gcloud run services describe invoicesentinel-web --region "$REGION" --format=json | python3 -c "import json,sys;d=json.load(sys.stdin);a=d[\"metadata\"].get(\"annotations\",{}).get(\"run.googleapis.com/urls\");print(\",\".join(json.loads(a)) if a else d[\"status\"][\"url\"])")

# --- CORS: allow the web origin on the API ---
gcloud run services update invoicesentinel-api --region "$REGION" \
  --update-env-vars "^@^CORS_ORIGINS=${WEB_URLS},http://localhost:3000" --quiet
echo "API: $API_URL"; echo "WEB: $WEB_URL"
