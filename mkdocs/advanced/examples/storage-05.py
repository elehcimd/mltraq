from pprint import pprint

from mltraq import create_experiment
from mltraq.storage.serializers.datapak import UnsupportedObjectType


class SomethingNotSupported:
    pass


experiment = create_experiment("example")


with experiment.run() as run:
    run.fields.failing = SomethingNotSupported()

try:
    experiment.persist()
except UnsupportedObjectType as e:
    pprint(str(e), width=70)
