import os
import tempfile

import mltraq
from mltraq import options
from mltraq.storage.datastore import DataStore, DataStoreIO


def test_datastore():
    """
    Test: We can write/read a DataStore(Bunch) object stored to file.
    """
    with tempfile.TemporaryDirectory() as tmpdirname, options().ctx({"datastore.url": f"file:///{tmpdirname}"}):
        # Create the object
        data = DataStore()
        data.a = 123

        # Store it
        with options().ctx({"datastore.relative_path_prefix": "abc"}):
            url = data.to_url()

        # Verify path contains /abc/
        assert "/abc/" in url

        # Verify that file exists
        pathname = tmpdirname + os.sep + DataStoreIO.get_filepath(url)
        assert os.path.exists(pathname)

        # Reload it
        data = DataStore.from_url(url)
        assert data.a == 123


def test_delete():
    """
    Test: The datastore directory of the expeirment is removed
    if the experiment is deleted.
    """

    with tempfile.TemporaryDirectory() as tmpdirname, options().ctx({"datastore.url": f"file:///{tmpdirname}"}):

        session = mltraq.create_session()
        experiment = session.create_experiment()

        with experiment.run() as run:
            run.fields.ds = DataStore()
            run.fields.ds.a = 123

        # Persist the experiment, writing to database/datawtore
        experiment.persist()

        # Verify that the experiment's datastore directory exists
        pathname = tmpdirname + os.sep + str(experiment.id_experiment)
        assert os.path.exists(pathname)

        experiment.delete()

        # Verify that directory doesn't exist anymore
        assert not os.path.exists(pathname)
