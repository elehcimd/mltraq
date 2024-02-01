# Creating sessions

Sessions allow you to define the connection to a database that will be used to persist the state of experiments.
By default, an in-memory SQlite instance is created:

{{include_code("mkdocs/tutorial/examples/01-sessions-01.py", title="Creating a session")}}

!!! Tip
    An application can instantiate one or more sessions to implement different use cases. E.g., you might want to store experiments locally, and upstream results once you're confident in the results.

You can specify a connection string (passed to SQLAlchemy) with the `url` parameter. The password can be provided interactively by passing the option `ask_password=True`.

