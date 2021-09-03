
# Some fixture dump sequences

```
docker-compose run server python manage.py dumpdata dataverses.registereddataverse \
    user \
    dataset.datasetinfo \
    analysis.depositorsetupinfo \
    dataset.dataversefileinfo \
    --indent=4 \
    > server/opendp_apps/analysis/fixtures/test_analysis_001.json
```