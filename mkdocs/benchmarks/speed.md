# Benchmarking experiment tracking frameworks

*Latest update: 2023.03.04*

This article overviews the advantages of fast experiment tracking and presents a comparative analysis of the most widely adopted solutions and MLtraq, highlighting their strengths and weaknesses.

!!! Info "TL;DR"
    Threading, filesystem, and database management are expensive. **MLtraq is the fastest experiment-tracking solution for workloads with hundreds of thousands of runs and arbitrarily large, complex Python objects.** 

In this analysis, we compare the experiment tracking speed of:

* [Weights & Biases](https://wandb.ai/) (0.16.3)
* [MLflow](https://mlflow.org/) (2.10.2)
* [FastTrackML](https://github.com/G-Research/fasttrackml) (0.5.0b2)
* [Neptune](https://neptune.ai/) (1.9.1)
* [Aim](https://aimstack.io/) (3.18.1)
* [Comet](https://www.comet.com/) (3.38.0)
* [MLtraq](https://mltraq.com/) (0.0.118)

Varying the number of experiments, runs, and values as defined in the [key concepts](../tutorial/index.md).

We benchmark the tracking speed of `float` values and 1D `NumPy` arrays of varying size, disabling everything else, such as logs, git, code, environment, and system properties.
Experiments are executed offline with storage on the local filesystem. The system is a MacBook Pro (M2, 2022). The creation of directories and files is considered a performance cost.

For each experiment, we report the time in seconds (s). The reported results are averaged on `10` independent runs running in the foreground without parallelization.
The plots report the performance varying the number of experiments, runs, and values, with aggregates by method.

References and instructions to reproduce the results, as well as more details on the setup, can be found in the notebooks [Benchmarks rev1](https://github.com/elehcimd/mltraq/blob/devel/notebooks/07%20Tracking%20speed%20-%20Benchmarks%20rev1.ipynb) (`float`) and [Benchmarks 2](https://github.com/elehcimd/mltraq/blob/fixes/notebooks/08%20Tracking%20speed%20-%20Benchmarks%202.ipynb) (`NumPy`).

!!! Question "How can we improve this analysis?"
    In comparative analyses, there are always many nuances and little details that can make a big difference. You can [open a discussion](https://github.com/elehcimd/mltraq/discussions) to ask questions or create a change request on the [issue tracker](https://github.com/elehcimd/mltraq/issues) if you find any issues. There might be ways to tune the methods to improve their performance that we missed or other solutions worth considering.

!!! Info
    All solutions considered in this comparative analysis have positively impacted the industry and served as an inspiration to guide the design of MLtraq. The many references to W&B are a testament to their excellent community and documentation.

## Changelog

* 2024.03.04 - Added FastTrackML, improved text and plots
* 2023.02.26 - Initial publication


## Why tracking speed matters

What makes fast-tracking so crucial? Let's explore its importance by examining the advantages from various perspectives.

### Initialization

The initialization of the tracking component can take more than `1s`, in some cases increasing linearly with the number of `runs`. High initialization times severely impact your ability to experiment on hundreds of thousands of possible configurations.
Furthermore, slow imports negatively impact development, CI/CD tests, and debugging speed. E.g., see this [W&B](https://github.com/wandb/wandb/issues/5440) ticket.

Wouldn't loading and starting tracking at nearly zero time be nice?

!!! Success "A short time-to-track is instrumental for a smooth developer experience."
  
### High frequency

At times, it's necessary to record metrics that occur frequently. This situation arises when you log loss and metrics for every batch during training, rewards for each step of every episode during simulation, or outputs, media, and metrics for every input during analysis. E.g., see the notebook [Logging Strategies for High-Frequency Data](https://colab.research.google.com/github/wandb/examples/blob/master/colabs/wandb-log/Logging_Strategies_for_High_Frequency_Data.ipynb#scrollTo=1rINj_LsJfqJ) by W&B.

The fine-grained logging/debugging of complex algorithms (not necessarily AI/ML models) and handling of simulation data that changes quickly over time are other situations that require frequent tracking.

Workarounds to handle too much information come at a completeness/accuracy cost, including downsampling, summarization, and histograms. 

What if we can avoid the workarounds and track more efficiently?

!!! Success "Tracking with less limitations is more powerful and robust."

### Large, complex objects

Datasets, timeseries, forecasts, media files such as images, audio recordings, and videos can be categorized as "large, complex objects".

You might want to log a set of images at every step to inspect visually how the quality of the model is progressing, the datasets used in cross-validation with different configurations and random seeds, forecasts and other metrics, and more. Generally, you can produce a large quantity of heterogeneous information while executing complex algorithms that include, but are not limited to, ML/AI model training.

Most solutions have limited, primitive, and slow support for efficient serializing complex Python objects. What if you could track anything as frequently as you want?

!!! Success "Efficient tracking arbitrarily large, complex Python objects makes tracking more powerful."

## Tracking `float` values

In this set of experiments, we evaluate the tracking performance on `float` values varying the number of `experiments, `runs`, and `values`.

### Experiment 1 (Initialization time): How long does tracking a single value take?

We evaluate the time required to start a new experiment and track a single value. This experiment lets us compare the initialization time of the methods.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-1.svg" >
</p>

Threading and database management dominate the cost:

* WandB and MLflow are the worst performing, with threading and events management dominating time. Aim follows by spending most of the time creating and managing its embedded key-value store. They cost up to 400 times more than the other methods.

* FastTrackML is remarkably fast to create new runs, offering API compatibility with MLFlow. It is also fast because it requires a server running in the background, eliminating most of the database initialization cost.

* Comet is next, with thread management dominating the cost. Writing to SQLite is the primary cost for MLtraq. **Comet **performs best with no threading, no SQLite **database, and simply writing the tracking data to files.**

### Experiment 2: How much time does it take to track 100-10K values?

An efficient experiment tracking initialization is essential, but monitoring many values fast is critical for any tracking solution.
In this experiment, we assess the time required to track and store 1K values.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-2.svg" >
</p>

The speedup of FastTrackML is localized in the creation of new runs, but the insertion of new tracking records remains similarly expensive:

* The time cost becomes prohibitively high for some methods, with MLflow and FastTrackML performing worst.
The primary cost is due to its database model, based on the [Entity-attribute-value model](https://en.wikipedia.org/wiki/Entity–attribute–value_model).

* Aim and WandB follow at a fraction of the cost of MLflow.

* Neptune, Comet, and MLtraq form a cluster of higher-performing methods. **MLtraq is the best performing, 5x faster than Comet/Neptune and 90-700x faster than the others.**

!!! Tip
    The advantage of MLtraq is how the data is tracked and stored. It is hard to beat because it is very close to simply adding an element to an array and serializing it to an SQLite column value with the speedy [DATAPAK](../advanced/storage.md) serialization format.

### Experiment 3: How much time to track 10 runs?
Evaluating different configurations (hyperparameters, etc.) maps to multiple runs and executing many runs is critical.
This experiment compares how long it takes to execute `10` runs.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-3.svg" >
</p>

The cost of starting a new run for some methods is high and similar to starting a new experiment, scaling rather poorly.
WandB and MLflow are the worst performing, followed by Aim at a fraction of the cost.

Comet, FastTrackML, Neptune, and MLtraq are orders of magnitude faster than the methods in the first group. **MLtraq is the best-performing method in its group and is more than 300 times faster than the others.**

!!! Info
    Some methods lack an equivalent modeling of experiments, or they are defined as runs in this analysis. In general, the performance varying the number of runs is a good proxy for the time cost of changing the number of experiments.

### Experiment 4: How much time to track 100 runs?

In this experiment, we repeated Experiment 4 with 100 runs, limiting the comparison to FastTrackML, Comet, Neptune, and MLtraq.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-4.svg" >
</p>

Comet is at least `20` times slower than the other methods. FastTrackML and Neptune follow.
**MLtraq is the best performing, 13x faster than the others.**

### Experiment 5: How much time to track 1K runs and 1K values?

The two standing methods are MLtraq and Neptune. Let's look at their performance as we increase both runs and values to 500 and 1K.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-5.svg" >
</p>

As we increase the number of tracked values or runs, MLtraq becomes more and more competitive. With no threading and no filesystem database bottleneck, it is the fastest method for realistic workloads.
**MLtraq is the best performing, 23x faster than Neptune.**

## Tracking `NumPy` arrays

In this set of experiments, we evaluate the tracking performance on 1D `NumPy` arrays, varying the number of `arrays` and their `size`.

### Experiment 1: How long does tracking an array of length 1M take?

We evaluate the time required to start a new experiment and track a single array of length 1M (default dtype is `numpy.float64`), which is 8M bytes if written to disk. Most methods do not support the serialization of `NumPy` arrays, and the test procedures handle it explicitly.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-1.svg" >
</p>

The database, the filesystem, and the threading dominated the duration of the experiment.
FastTrackML and Comet have a similar performance, storing each tracked array in a separate file on the filesystem.
Neptune encodes the arrays as images, [uuencoding](https://en.wikipedia.org/wiki/Uuencoding) them and embedding
the resulting text in a single JSON-formatted file. Despite the more elaborate scheme, the fewer writes to filesystem make it competitive.

**MLtraq is the best-performing method, 3x faster than FastTrackML and 4x faster than Neptune**.
Its better performance is due to its faster serialization strategy based on safe pickling and `NumPy` native code.
See [Data store](../advanced/datastore.md) for more details.

# Experiment 2: How long does tracking 1-10 arrays with length 10K-1M take?

In this experiment, we assess the time required to track multiple arrays of varying sizes, up to 1M.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-2.svg" >
</p>

Trends remain similar to Experiment 1, except WandB whose time explodes. We suspect this is due to the threading communication.

### Experiment 3: How long does it take to track 1-10K arrays with a length of 1K?

In this experiment, we assess the time required to track a large number of small-sized arrays.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-3.svg" >
</p>

Comet and FastTrackML perform similarly, with Neptune and MLtraq being 4x faster.
**MLtraq is the best-performing method, being 5x faster than Neptune**.

## Conclusion

* **MLtraq is the fastest experiment-tracking solution for workloads with hundreds of thousands of runs and arbitrarily large, complex Python objects**. 
The primary goal of other solutions gravitates toward compatibility, dashboarding, streaming, third-party integrations, and complete model lifecycle management. Their support for rich modeling of experiments, runs, and complex Python objects is missing or limited. We believe these are essential capabilities in the experimentation phase worth optimizing.

* **Relying solely on the filesystem as a database is a recipe for low performance**.
As noted on the [SQLite website](https://www.sqlite.org/fasterthanfs.html), relying on a single file to store the local database copy could be
35% faster than a filesystem-based solution. The higher initialization cost of having a proper database pays off in scalability and reliability.
MLtraq provides the flexibility to choose where to store objects with the [Data store](../advanced/datastore.md) interface.

* **The solutions that adopt threading to incorporate streaming capabilities pay the hidden cost of IPC (Inter-Process Communication).** Further, the higher complexity results in more I/O errors and instability issues.

