# Data stream
This interface lets you stream metrics of experiments safely to a database during their execution, enabling monitoring of their progress.

Data streams use UNIX (local) and INET (network) socket datagrams: independent, self-contained messages whose arrival and arrival time are not guaranteed. Their checksum ensures the integrity of the messages.

The size of each message is limited by default to `1500` bytes with INET sockets and `4096` bytes with UNIX sockets.
The operating system provides a buffer for sockets. If the buffer is full, all new messages are discarded.

The streaming of experiments transparently supports the `Sequence` objects that are stored as `run.fields` attributes.
If a message is lost, its corresponding `Sequence` will miss a row associated with its corresponding `idx` value.

!!! Tip
    An experiment can be persisted after its execution, overwriting its partially streamed state, resolving any data loss due to lost messages, and storing all other fields that were not part of the streaming data.

Streaming is possible for experiments already in the database, ensuring their consistency over time.

## Example: Streaming metrics

The following example demonstrates how to track and store metrics in the database during the execution of an experiment:

1. Configure a stream over the network, specifying the address to send the messages to, and the server address
2. Create and persist an experiment with a `"metrics"` Sequence attribute using the parametrized step `create_sequences`
3. Tracking and streaming of a metric `v`, relying on the context `run.datastream_client()`
4. Receiving the streaming data using the context `session.datastream_server()`

{{include_code("mkdocs/advanced/examples/datastream-01.py", title="Data stream example", drop_comments=False)}}

The output reports the logs to ease the understanding of what's happening in the threads: The main thread handles the execution of the experiment and the execution of the run (parallelization is turned off to simplify the example), the 2nd thread is the server listening of new messages, and a 3rd thread is in charge of updating the experiments on the database.

The sequence `run.metrics` is streamed. `run.dataset` is not streamed, as it is not a Sequence. The tracked value of `run.dataset` becomes available only once the experiment is persisted after its execution is complete.