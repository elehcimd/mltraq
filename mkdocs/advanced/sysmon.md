# System monitor

You can monitor the CPU, memory, disk, and network usage during the execution of experiments.
The tracking is done transparently in a thread, adding the stats to the `run` field `sysmon`.

The monitor operates at the `run` level and also works in distributed environments.

!!! Tip
    The statistics are streamed if the [datastream](./datastream.md) is enabled.

## Example: Monitoring the system

{{include_code("mkdocs/advanced/examples/sysmon-01.py", title="Monitoring the system", 
drop_comments=False)}}

