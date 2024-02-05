import hashlib
import os
import tempfile

from mltraq import Bunch, Run, create_session


def generate_artifacts(run: Run):
    # Generate two random binary blobs as example of artifacts we want to persist.
    run.vars.artifacts = Bunch()
    run.vars.artifacts.B1 = os.urandom(10**6)
    run.vars.artifacts.B2 = os.urandom(10**6)

    # Persist names of blobs we want to reload
    run.fields.artifact_keys = list(run.vars.artifacts.keys())

    # Compute checksums, s.t. we can verify them later upon loading.
    run.fields.cks1 = hashlib.sha256(run.vars.artifacts.B1).hexdigest()
    run.fields.cks2 = hashlib.sha256(run.vars.artifacts.B2).hexdigest()


def dump_artifacts(run: Run):
    # Artifacts path reserved for experiment's run.
    run.fields.pathdir = f"{run.config.artifacts_dir}/{run.id_experiment}/{run.id_run}/"

    # Create directory if missing
    try:
        os.makedirs(run.fields.pathdir)
    except FileExistsError:
        pass

    # Dump blobs
    for name, value in run.vars.artifacts.items():
        with open(f"{run.fields.pathdir}/{name}", "wb") as f:
            f.write(value)


def load_artifacts(run: Run):

    # Reload blobs
    run.vars.artifacts = Bunch()
    for name in run.fields.artifact_keys:
        with open(f"{run.fields.pathdir}/{name}", "rb") as f:
            run.vars.artifacts[name] = f.read()

    # Check hashes
    cks1 = hashlib.sha256(run.vars.artifacts.B1).hexdigest()
    cks2 = hashlib.sha256(run.vars.artifacts.B2).hexdigest()
    run.fields.blobs_match = run.fields.cks1 == cks1 and run.fields.cks2 == cks2


# Create experiment
session = create_session()

# Temporary directory to store artifacts
temp_dir = tempfile.TemporaryDirectory()

# Add 5 runs
experiment = session.create_experiment("example").add_runs(i=range(5))

# Generate and dump artifacts in ./artifacts/experiment_id/run_id/*
experiment.execute(
    [generate_artifacts, dump_artifacts], config={"artifacts_dir": f"{temp_dir.name}/artifacts"}, args_field="args"
)
experiment.persist()

# Reload experiment with artifacts
experiment = session.load("example")
experiment.execute([load_artifacts], args_field="args")

# Verify hashes of reloaded binary blobs
print(experiment.runs.df()[["cks1", "cks2", "blobs_match"]])

# Remove temporary directory
temp_dir.cleanup()