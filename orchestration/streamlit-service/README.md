# CityReport Streamlit Service

## Docker Build

From the `orchestration/` directory:

```bash
docker build -t orchestration-streamlit-service -f streamlit-service/Dockerfile .
```

This uses `.` as the build context (the `orchestration/` directory) so the Dockerfile can access both the streamlit-service files and the shared `data/` directory.
