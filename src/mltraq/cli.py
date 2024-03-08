import argparse
import logging

import pandas as pd
from tabulate import tabulate

import mltraq
from mltraq.experiment import Experiment
from mltraq.opts import options
from mltraq.storage.datastream import datastream_server
from mltraq.utils.base_options import add_option_argument
from mltraq.utils.exceptions import InvalidInput
from mltraq.utils.logging import init_logging
from mltraq.utils.sequence import Sequence

log = logging.getLogger(__name__)


def print_df(df: pd.DataFrame):
    """
    Pretty prints a `df` Pandas DataFrame using tabulate.
    """

    if len(df) > 0:
        # Handling of a bug in tabulate, see https://github.com/astanin/python-tabulate/issues/315
        maxcolwidths = options().get("cli.tabulate.maxcolwidths")
    else:
        maxcolwidths = None
    print(tabulate(df, maxcolwidths=maxcolwidths, headers="keys", tablefmt="rounded_grid"))


def main():
    """
    Entry point for the CLI tool.
    """

    main_parser = argparse.ArgumentParser(description="MLtraq CLI tool.", add_help=False)
    add_option_argument(main_parser)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands", dest="cmd", required=True)
    subparsers.add_parser("dss", help="Start the DataStream server", parents=[main_parser])
    subparsers.add_parser("ls", help="List experiments", parents=[main_parser])

    # Command "exp"
    parser_cmd = subparsers.add_parser("exp", help="Show experiment", parents=[main_parser])
    group = parser_cmd.add_mutually_exclusive_group(required=True)
    group.add_argument("--uuid", dest="experiment_uuid")
    group.add_argument("--name", dest="experiment_name")

    # Command "runs"
    parser_cmd = subparsers.add_parser("runs", help="Show experiment's runs", parents=[main_parser])
    group = parser_cmd.add_mutually_exclusive_group(required=True)
    group.add_argument("--uuid", dest="experiment_uuid")
    group.add_argument("--name", dest="experiment_name")

    # Command "stats"
    parser_cmd = subparsers.add_parser("stats", help="Show experiment's stats", parents=[main_parser])
    parser_cmd.add_argument("--stat-name", dest="stat_name")
    group = parser_cmd.add_mutually_exclusive_group(required=True)
    group.add_argument("--uuid", dest="experiment_uuid")
    group.add_argument("--name", dest="experiment_name")

    # Command "options"
    parser_cmd = subparsers.add_parser("options", help="Show options", parents=[main_parser])
    parser_cmd.add_argument("--option-name", dest="option_name")

    # Parse parameters and set options
    args = parser.parse_args()
    options().set_argument_options(args.option)

    # Init logging
    init_logging()

    # Handle commands
    if args.cmd == "dss":
        datastream_server()
    elif args.cmd == "ls":
        session = mltraq.create_session()
        print_df(session.ls())
    elif args.cmd == "exp":
        session = mltraq.create_session()
        experiment = session.load(name=args.experiment_name, id_experiment=args.experiment_uuid)
        print_df(experiment.df())
    elif args.cmd == "runs":
        session = mltraq.create_session()
        experiment = session.load(name=args.experiment_name, id_experiment=args.experiment_uuid)
        print_df(experiment.runs.df())
    elif args.cmd == "options":
        df = pd.Series(options().flatten(), name="Value").to_frame()
        df.index.name = "Name"
        if args.option_name:
            df = df[df.index == args.option_name]
        print_df(df)
    elif args.cmd == "stats":
        session = mltraq.create_session()
        experiment = session.load(name=args.experiment_name, id_experiment=args.experiment_uuid)
        df = experiment_stats(experiment)
        if args.stat_name:
            df = df[df.index == args.stat_name]
        print_df(df)
    else:
        raise InvalidInput(f"Unknown command '{args.cmd}'")


def experiment_stats(experiment: Experiment) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame describing the contents of `experiment`.
    """

    stats = {
        "id_experiment": experiment.id_experiment,
        "name": experiment.name,
        "meta": experiment.get_metadata(),
        "runs": str(experiment.runs),
        "memory_usage": experiment.runs.df().memory_usage().sum(),
        "n_runs": len(experiment.runs),
        "n_fields": len(experiment.runs.first().fields),
        "fields": [(k, type(v)) for k, v in experiment.runs.first().fields.items()],
    }

    # For nested/structured fields, provide some more stats.
    for name, value in experiment.runs.first().fields.items():
        if isinstance(value, Sequence):
            if value.df().shape[0] == 0:
                stats[f"field.{name}.n_rows"] = 0
            else:
                row = value.df().iloc[0].to_dict()
                stats[f"field.{name}.columns"] = [(k, type(v)) for k, v in row.items()]
                stats[f"field.{name}.n_rows"] = sum(
                    [run.fields[name].df().shape[0] for run in experiment.runs.values()]
                )
        if isinstance(value, pd.DataFrame):
            if value.shape[0] == 0:
                stats[f"field.{name}.n_rows"] = 0
            else:
                row = value.iloc[0].to_dict()
                stats[f"field.{name}.columns"] = [(k, type(v)) for k, v in row.items()]
                stats[f"field.{name}.n_rows"] = sum([run.fields[name].shape[0] for run in experiment.runs.values()])

    df = pd.Series(stats).rename("Value").to_frame()
    df.index.name = "Name"
    return df
