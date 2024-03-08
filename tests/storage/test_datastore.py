import os

import mltraq
from mltraq import options
from mltraq.storage.datastore import DataStore, DataStoreIO
from mltraq.utils.fs import tmpdir_ctx


def test_datastore():
    """
    Test: We can write/read a DataStore(Bunch) object stored to file.
    """
    with tmpdir_ctx():
        # Create the object
        data = DataStore()
        data.a = 123

        # Store it
        with options().ctx({"datastore.relative_path_prefix": "abc"}):
            url = data.to_url()

        # Verify path is int he shape of "/abc/.....""
        assert "/abc/" in url

        # Verify that file exists
        pathname = DataStoreIO.get_filepath(options().get("datastore.url")) + os.sep + DataStoreIO.get_filepath(url)
        assert os.path.exists(pathname)

        # Reload it
        data = DataStore.from_url(url)
        assert data.a == 123


def test_delete():
    """
    Test: The datastore directory of the expeirment is removed
    if the experiment is deleted.
    """

    with tmpdir_ctx():

        session = mltraq.create_session()
        experiment = session.create_experiment()

        with experiment.run() as run:
            run.fields.ds = DataStore()
            run.fields.ds.a = 123

        # Persist the experiment, writing to database/datawtore
        experiment.persist()

        # Verify that the experiment's datastore directory exists
        pathdir = DataStoreIO.get_filepath(options().get("datastore.url")) + os.sep + str(experiment.id_experiment)
        assert os.path.exists(pathdir)

        experiment.delete()

        # Verify that directory doesn't exist anymore
        assert not os.path.exists(pathdir)
