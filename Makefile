.PHONY: api web install-api install-web health

install-api:
	cd api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

install-web:
	cd web && npm install

api:
	cd api && DATA_DIR=../data UPLOAD_DIR=../data/uploads CORS_ORIGINS=http://localhost:3000 .venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --reload

web:
	cd web && npm run dev

health:
	curl -s http://localhost:8080/health | python3 -m json.tool
