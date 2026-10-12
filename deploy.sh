#!/usr/bin/env bash
# Deploy InvoiceSentinel (API + web) to Google Cloud Run.
# Prereqs: gcloud logged in, billing enabled, secret "gemini-api-key" exists
#   printf %s "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
set -euo pipefail
PROJECT="${PROJECT:-gen-lang-client-0252871691}"
REGION="${REGION:-asia-southeast1}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
gcloud config set project "$PROJECT" >/dev/null
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com \
  firestore.googleapis.com storage.googleapis.com
PN=$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PN}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor >/dev/null
SA="${PN}-compute@developer.gserviceaccount.com"
BUCKET="${BUCKET:-invoicesentinel-uploads-${PN}}"

# --- Firestore (Native, asia-southeast1) + private upload bucket; idempotent ---
gcloud firestore databases describe --database="(default)" >/dev/null 2>&1 || \
  gcloud firestore databases create --location="$REGION" --type=firestore-native
gcloud storage buckets describe "gs://$BUCKET" >/dev/null 2>&1 || \
  gcloud storage buckets create "gs://$BUCKET" --location "$REGION" --uniform-bucket-level-access --public-access-prevention
gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$SA" --role=roles/datastore.user --condition=None --format=none
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --member="serviceAccount:$SA" --role=roles/storage.objectAdmin --format=none

# --- API (FastAPI + Google ADK). State lives in Firestore; seeds are baked in and loaded on first start / reset-demo. ---
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
cp -r "$ROOT/api/." "$TMP/"; rm -rf "$TMP/__pycache__"
cp "$TMP/Dockerfile.standalone" "$TMP/Dockerfile"
gcloud run deploy invoicesentinel-api --source "$TMP" --region "$REGION" \
  --port 8080 --cpu 1 --memory 1Gi --min-instances 0 --max-instances 2 --timeout 300 \
  --allow-unauthenticated --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --set-env-vars "STORAGE_BACKEND=firestore,FIRESTORE_PROJECT=${PROJECT},UPLOAD_BUCKET=${BUCKET}" --quiet
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
