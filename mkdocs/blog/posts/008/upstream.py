from mltraq import create_session
from mltraq.utils.fs import tmpdir_ctx

with tmpdir_ctx():

    # Creating a session to a local MLtraq db
    local = create_session("sqlite:///local.db")

    # Working on a new experiment ...
    local.create_experiment("iris").persist()

    # Upstreaming results to a (simulated) remote db ...
    remote = create_session("sqlite:///remote.db")
    remote.persist_experiment(local.load_experiment("iris"), if_exists="replace")
