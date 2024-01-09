# Basic tracking

In the next example, we track two runs using explicit and context-based tracking, 
simulating the tracking of accuracy scores for two competing ML models.
 
{{include_code("mkdocs/tutorial/examples/track-run-001.py", title="Repeated toin cossing")}}

The run `[1]` is defined and linked explicitly to the experiment. This is the 
fastest route to add tracking to existing code with minimum code changes.
Instead, run `[2]` is implemented by using the `with` statement, resulting in more
compact and elegant code.
In both cases, the user remains in direct control of the execution flow.

!!! Note
    Once the tracking is complete, we can persist, load and query the experiment.

!!! Warning
    With explicit and context-based tracking, runs are linked to the experiment
    only once their execution is complete and you cannot benefit from the higher
    degree of automation that fully managed MLTRAQ experiments can offer.
