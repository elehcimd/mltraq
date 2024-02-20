# Tracking speed

*Latest update: 2023.02.20*

In this analysis, we compare the experiment tracking speed of
[Weights & Biases](https://wandb.ai/) (0.16.3), [MLflow](https://mlflow.org/) (2.10.2), [Neptune](https://neptune.ai/) (1.9.1),
[Aim](https://aimstack.io/) (3.18.1), [Comet](https://www.comet.com/) (3.38.0) and [MLtraq](https://mltraq.com/) (0.0.118) by varying the number of experiments, runs and values as defined in the [key concepts](../tutorial/index.md).

The analysis is limited to benchmarking the tracking speed of scalar values, disabling everything else such as logs, git, code, environment and system properties.
Experiments are executed offline with storage on the local filesystem. The system is a MacBook Pro (M2, 2022). The creation of directories and files is taken into account as a performance cost.

For each experiment, we report the time in seconds (s). The reported results are averaged on `10` independent runs running in foreground, no parallelization.
The plots report the performance varying the number of experiments, runs and values, with aggregates by method.

References and instructions to reproduce the results, and more details on the setup, can be found in [this notebook](https://github.com/elehcimd/mltraq/blob/devel/notebooks/07%20Tracking%20speed%20-%20Benchmarks.ipynb).

!!! Question "How can we improve this analysis?"
    In comparative analyses, there are always many nuances and little details that can make a big difference. You can [open a discussion](https://github.com/elehcimd/mltraq/discussions) to ask a question, or create a change request on the [issue tracker](https://github.com/elehcimd/mltraq/issues) if you find any issues. There might be ways to tune the methods to improve their performance that we missed, or other solutions worth considering.


## Experiment 1: How long does tracking a single value take?

We evaluate the time required to start a new experiment and track a single value. This experiment lets us compare the start-up time of the methods.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-1.svg" >
</p>

Threading and database management dominate the cost:

* WandB and MLflow are the worst performing, with time dominated by threading and events management. Aim follows by spending most of the time creating and managing its embedded key-value store. They cost up to 400 times more than the other methods.

* Comet is next, with thread management dominating the cost. Writing to SQLite is the key cost for MLtraq. **Comet is the best performing, with no threading, no SQLite database, simply writing the tracking data to files.**

## Experiment 2: How much time to track 10K values?

Having an efficient experiment tracking start-up is important, but being able to track many values fast is key for any tracking solution.
In this experiment, we assess the time required to track and store 1K values.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-2a.svg" >
</p>

The time cost becomes prohibitively high for some methods, with MLflow being the worst performing, mostly
due to how the tracking data is stored with the [Entity-attribute-value model](https://en.wikipedia.org/wiki/Entity–attribute–value_model).
Aim and WandB follow at a fraction of the cost of MLflow.

Neptune, Comet and MLtraq form a cluster of higher-performing methods. **MLtraq is the best performing, 12x faster than Comet/Neptune and 90-700x faster than the others.**

!!! Tip
    The advantage of MLtraq is in how the data is tracked and stored. Being very close to simply adding an element to an array and serializing it to an SQLite column value with the speedy [DATAPAK](../advanced/storage.md) serialization format, it is hard to beat.


## Experiment 3: How much time to track 10 runs?

The evaluation of different configurations (hyperparameters, ...) maps to multiple runs and it is key to be able to execute efficiently a large number of runs.
In this experiment, we compare how much time it takes to start `10` runs.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-3.svg" >
</p>

The cost of starting a new run for some methods is really high and similar to starting a new experiment, scaling rather poorly.
WandB and MLflow are the worst performing, followed by Aim at a fraction of the cost.

Comet, Neptune and MLtraq are 5x faster than the methods in the first group. **MLtraq is the best performing, 43x faster than Comet, 1.7x faster than Neptune and 296-1300x faster than the others.**

!!! Info
    Some methods lack an equivalent modeling of experiments, or they are modeled as runs in this analysis. In general, the performance varying the number of runs is a good proxy to the time cost of varying the number of experiments.

## Experiment 4: How much time to track 100 runs?

In this experiment, we repeat Experiment 4 but with 100 runs, limiting the comparison to Comet, Neptune and MLtraq.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-4.svg" >
</p>

The time cost is sublinear for MLtraq, and superlinear (higher than linear) for the others.
**MLtraq is the best performing, 14x faster than Neptune, 637x faster than Comet.**

## Experiment 5: How much time to track 1K runs and 1K values?

The two standing methods are MLtraq and Neptune, let's look at their performance as we increase both runs and values to 500 and 1K.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-5.svg" >
</p>

As we increase the number of tracked values or runs, MLtraq becomes more and more competitive. With no threading and no filesystem database bottleneck, it is the fastest method for realistic workloads.
**MLtraq is the best performing, 26x faster than Neptune.**

## Conclusion

* **MLtraq is the fastest experiment tracking solution for workloads with hundreds of thousands of runs and values.** Incorporating streaming capabilities and implementing a comprehensive web dashboard could make it even more competitive, especially if done without compromising its really good time performance metrics.

* **Relying on the filesystem as a database is a recipe for low performance**.
As noted on the [SQLite website](https://www.sqlite.org/fasterthanfs.html), relying on a single file to store the local database copy could be
35% faster than a filesystem-based solution. The higher start-up cost of having a proper database pays off in scalability and reliability.

* **The solutions that adopt threading to incorporate streaming capabilities pay the hidden cost of IPC (Inter-Process Communication) and the generally poor performance of threads in Python.** Further, the higher complexity results in threading-related failures, which we encountered and fighted with even in these simple comparative experiments.
