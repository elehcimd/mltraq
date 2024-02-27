# Benchmarking experiment tracking frameworks

*Latest update: 2023.02.26*

This article overviews the advantages of fast experiment tracking and presents a comparative analysis of the most widely adopted solutions, and MLtraq, highlighting their strengths and weaknesses.

!!! Info "TL;DR"
    **MLtraq is the fastest experiment tracking solution for **workloads with hundreds of** thousands of runs and arbitrarily large, complex Python objects.** However, it lacks the streaming of tracking data and a web dashboard.

In this analysis, we compare the experiment tracking speed of:

* [Weights & Biases](https://wandb.ai/) (0.16.3)
* [MLflow](https://mlflow.org/) (2.10.2)
* [Neptune](https://neptune.ai/) (1.9.1)
* [Aim](https://aimstack.io/) (3.18.1)
* [Comet](https://www.comet.com/) (3.38.0)
* [MLtraq](https://mltraq.com/) (0.0.118)

Varying the number of experiments, runs and values as defined in the [key concepts](../tutorial/index.md).

We benchmark the tracking speed of `float` values and 1D `NumPy` arrays of varying size, disabling everything else such as logs, git, code, environment and system properties.
Experiments are executed offline with storage on the local filesystem. The system is a MacBook Pro (M2, 2022). The creation of directories and files is taken into account as a performance cost.

For each experiment, we report the time in seconds (s). The reported results are averaged on `10` independent runs running in foreground, no parallelization.
The plots report the performance varying the number of experiments, runs and values, with aggregates by method.

References and instructions to reproduce the results, and more details on the setup, can be found in notebooks [Benchmarks](https://github.com/elehcimd/mltraq/blob/devel/notebooks/07%20Tracking%20speed%20-%20Benchmarks.ipynb) (`float`) and [Benchmarks 2](https://github.com/elehcimd/mltraq/blob/fixes/notebooks/08%20Tracking%20speed%20-%20Benchmarks%202.ipynb) (`NumPy`).

!!! Question "How can we improve this analysis?"
    In comparative analyses, there are always many nuances and little details that can make a big difference. You can [open a discussion](https://github.com/elehcimd/mltraq/discussions) to ask a question, or create a change request on the [issue tracker](https://github.com/elehcimd/mltraq/issues) if you find any issues. There might be ways to tune the methods to improve their performance that we missed, or other solutions worth considering.

!!! Info
    All solutions considered in this comparative analysis have made a positive impact in the industry and served as inspiration to guide the design of MLtraq.
    The many references to W&B are a testament to their very good community and documentation, and should not be considered as a criticism.


## Why tracking speed matters

What makes fast tracking so crucial? Let's explore its importance by examining the advantages from various perspectives.

### Start up

The initialization of the tracking component can take more than `1s`, in some cases increasing linearly with the number of `runs`. High initialization times impact severely on your ability to experiment on hundreds of thousands of possible configurations.
Furthermore, slow imports impact negatively on development, CI/CD tests and debugging speed. E.g., see this [W&B](https://github.com/wandb/wandb/issues/5440) ticket.

Wouldn't be nice to load and start tracking at nearly zero time?

!!! Success "A short time-to-track is instrumental for a smooth developer experience."
  
### High frequency

At times, it's necessary to record metrics that occur frequently. This situation arises when you log loss and metrics for every batch during training, rewards for each step of every episode during simulation, or outputs, media, and metrics for every input during analysis. E.g., see the notebook [Logging Strategies for High-Frequency Data](https://colab.research.google.com/github/wandb/examples/blob/master/colabs/wandb-log/Logging_Strategies_for_High_Frequency_Data.ipynb#scrollTo=1rINj_LsJfqJ) by W&B.

The fine-grained logging/debugging of complex algorithms (not necessarily AI/ML models) and handling of simulations data that changes quickly over time are other situations that require frequent tracking.

Workarounds to handle too much information come at a completeness/accuracy cost and include downsampling, summarization and histograms. 

What if we can avoid the workarounds and track more efficiently?

!!! Success "Tracking with less limitations is more powerful and robust."

### Large, complex objects

Datasets, timeseries, forecasts, media files such as images, audio recordings and videos can be categorized as "large, complex objects".

You might want to log a set of images at every step to inspect visually how the quality of the model is progressing, the datasets used in cross-validation with different configurations and random seeds, forecasts and other metrics, and more. Generally, you can produce a large quantity of heterogeneous information during the execution of complex algorithms that include, but it is not limited to, ML/AI model training.

Most solutions have limited, very primitive and slow support for efficient serialization of complex Python objects. What if you could track anything as frequently as you want?

!!! Success "Efficient tracking arbitrarily large, complex Python objects makes tracking more powerful."

## Tracking `float` values

In this set of experiments, we evaluate the tracking performance on `float` values varying the number of `experiments`, `runs` and `values`.

### Experiment 1: How long does tracking a single value take?

We evaluate the time required to start a new experiment and track a single value. This experiment lets us compare the start-up time of the methods.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-1.svg" >
</p>

Threading and database management dominate the cost:

* WandB and MLflow are the worst performing, with time dominated by threading and events management. Aim follows by spending most of the time creating and managing its embedded key-value store. They cost up to 400 times more than the other methods.

* Comet is next, with thread management dominating the cost. Writing to SQLite is the key cost for MLtraq. **Comet is the best performing, with no threading, no SQLite database, simply writing the tracking data to files.**

### Experiment 2: How much time to track 10K values?

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


### Experiment 3: How much time to track 10 runs?

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

### Experiment 4: How much time to track 100 runs?

In this experiment, we repeat Experiment 4 but with 100 runs, limiting the comparison to Comet, Neptune and MLtraq.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-4.svg" >
</p>

The time cost is sublinear for MLtraq, and superlinear (higher than linear) for the others.
**MLtraq is the best performing, 14x faster than Neptune, 637x faster than Comet.**

### Experiment 5: How much time to track 1K runs and 1K values?

The two standing methods are MLtraq and Neptune, let's look at their performance as we increase both runs and values to 500 and 1K.

<p align="center">
  <img height="70%" width="70%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-5.svg" >
</p>

As we increase the number of tracked values or runs, MLtraq becomes more and more competitive. With no threading and no filesystem database bottleneck, it is the fastest method for realistic workloads.
**MLtraq is the best performing, 26x faster than Neptune.**

## Tracking `NumPy` arrays

In this set of experiments, we evaluate the tracking performance on 1D `NumPy` arrays varying the number of `arrays` and their `size`.

### Experiment 1: How long does tracking an array of length 1M take?

We evaluate the time required to start a new experiment and track a single array of length 1M (default dtype is `numpy.float64`), which is 8M bytes if written to disk.

<p align="center">
  <img height="90%" width="90%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-1.svg" >
</p>

The time cost is dominated by database, filesystem and threads initialization.
**MLtraq is the best performing, 3x faster than Neptune** due to its inefficient serialization strategy, that relies on a string format to encode the contents of the array with `neptune.types.File.as_image`.

### Experiment 2: How much time to track 1-10 arrays with length 10K-1M?

In this experiment, we assess the time required to track multiple arrays of varying size, up to 1M.

<p align="center">
  <img height="90%" width="90%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-2.svg" >
</p>

* WandB performs poorly poorly due to its JSON-based serialization to text files.
* MLflow and Aim follow with similar performance, despite working rather differently: MLflow stores artifacts on the filesystem and Aim in its embedded RocksDB.
* The third, faster, cluster includes Comet, Neptune and MLtraq. **MLtraq is the best performing method, 4x faster than Neptune**. How is this possible? MLtraq serializes bags of objects together to disk for maximum efficiency using its [Data store](../advanced/datastore.md) interface. Neptune relies on an inefficient text encoding, incurring in a high performance penalty.

### Experiment 3: How much time to track 1-10K arrays with length 1K?

In this experiment, we assess the time required to track a large number of arrays of small size.

<p align="center">
  <img height="90%" width="90%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-3.svg" >
</p>

**MLtraq is 6x faster than Neptune and 20x faster than Comet**, thanks to its optimized serialization/storage strategy.

## Conclusion

* **MLtraq is the fastest experiment tracking solution for workloads with up to hundreds of thousands of runs and arbitrarily large, complex Python objects**. The primary goal of other solutions gravitates toward dashboarding, streaming, third-party integrations and the complete model lifecycle management. Their support for rich modeling of experiments, runs and complex Python objects is missing or rather limited. We believe that these are important capabilities in the experimentation phase, worth optimizing.

* **Relying solely on the filesystem as a database is a recipe for low performance**.
As noted on the [SQLite website](https://www.sqlite.org/fasterthanfs.html), relying on a single file to store the local database copy could be
35% faster than a filesystem-based solution. The higher start-up cost of having a proper database pays off in scalability and reliability.
MLtraq provides the flexibility to choose where to store objects with the [Data store](../advanced/datastore.md) interface.

* **The solutions that adopt threading to incorporate streaming capabilities pay the hidden cost of IPC (Inter-Process Communication) and the generally poor performance of threads in Python.** Further, the higher complexity results in threading-related failures, which we encountered and fighted with even in these simple comparative experiments.
