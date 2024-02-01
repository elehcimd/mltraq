from mltraq import create_session


class SomethingUnsafe:
    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        print("__setstate__")


# Create session and experiment
session = create_session()
experiment = session.create_experiment("example")

with experiment.run() as run:
    # add field value with unsafe type
    run.state.unsafe = SomethingUnsafe()

# Persist experiment, pickling the Experiment object
experiment.persist(store_unsafe_pickle=True)

print("Reloading the pickled experiment from database")
experiment = session.load("example", unsafe_pickle=True)
