# Store artifacts

## How can I store large datasets and models?

In this example, we demonstrate how to store binary blobs as regular files organized in a directory structure `artifacts/{experiment_id}/{run_id}`. Similarly, you can store artifacts in CSV, JSON, Parquet, Feather and tabular formats
locally or in the cloud with [PyArrow](https://arrow.apache.org/docs/python/) or third-party solutions.

{{include_code("mkdocs/howto/examples/02-artifacts-storage-01.py", title="Example on storing artifacts", drop_comments=False)}}

