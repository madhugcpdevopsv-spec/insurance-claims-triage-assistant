# STEP 12: local OpenTelemetry Collector + Jaeger

From the repository root, install the updated Python requirements:

```bash
python -m pip install -r requirements.txt
```

Start Jaeger and the Collector (Docker Desktop must be running):

```bash
docker compose up -d
```

Run the API from a second terminal using the active project virtual environment:

```bash
uvicorn app.main:app --reload
```

Make a synthetic triage request:

```bash
curl "http://127.0.0.1:8000/triage?claim_id=CLM-1001"
```

Open <http://localhost:16686>, select `insurance-claims-triage-assistant`, and search traces. The Collector also logs received spans. To stop the local observability stack:

```bash
docker compose down
```

The API process exports OTLP/HTTP to `http://localhost:4318/v1/traces` by default. Override with `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`; set `OTEL_TRACES_EXPORTER=console` to use console tracing instead. This setup uses synthetic data and is for local development only.
