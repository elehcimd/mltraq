from mltraq import create_experiment, options
from mltraq.steps.sleep import sleep

# Activate the system monitor, specifying the frequency to sample the stats
with options().ctx({"sysmon.disable": False, "sysmon.interval": 0.1}):

    # Create a new experiment
    experiment = create_experiment()

    # Wait enough time to track a few timestamps, and report the contents
    print(experiment.execute(sleep(0.3)).runs.first().fields.sysmon.df())
