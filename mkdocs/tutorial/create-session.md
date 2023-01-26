# Creating sessions

A session allows you establish a connection to the database where the tracking data is stored.
An application can instantiate one or more MLTRAQ sessions to store and manage experiments
across different databases.
If no database is specified, an SQLite in-memory instance is used by default:

{{include_code("mkdocs/tutorial/examples/create-session-001.py", title="Creating a local session")}}

You have the option to specify a different database connection URL with the `url` parameter.

Additionally, you can choose to input the password interactively by setting `ask_password=True`: 
this is useful to not leak credentials in shared notebooks, increasing your level of security.

!!! Note
    * **SQLite** is a self-contained, file-based SQL database, bundled with Python. This means that
    you can use MLTRAQ anywhere without the burden of creating and managing other databases.

    * You can experiment with shared experiments using a free-tier PostgreSQL instance offered
    at [render.com](https://render.com/).

