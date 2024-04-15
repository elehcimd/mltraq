# Benchmarking experiment tracking frameworks

*Latest update: 2024.04.11*

This article overviews the advantages of fast experiment tracking and presents a comparative analysis of the most widely adopted solutions and MLtraq, highlighting their strengths and weaknesses.

!!! Info "TL;DR"
    Threading, filesystem, and database management are expensive and dominate the time cost. **MLtraq is the fastest experiment-tracking solution for workloads with hundreds of thousands of runs and arbitrarily large, complex Python objects.** 

In this analysis, we compare the experiment tracking speed of:

* [Weights & Biases](https://wandb.ai/) (0.16.3)
* [MLflow](https://mlflow.org/) (2.11.0)
* [FastTrackML](https://github.com/G-Research/fasttrackml) (0.5.0b2)
* [Neptune](https://neptune.ai/) (1.9.1)
* [Aim](https://aimstack.io/) (3.18.1)
* [Comet](https://www.comet.com/) (3.38.1)
* [MLtraq](https://mltraq.com/) (0.0.125)

We vary the number of runs and values as defined in the [key concepts](../tutorial/index.md).

We benchmark the tracking speed of `float` values and 1D `NumPy` arrays of varying size, turning off everything else, such as logs, git, code, environment, and system properties.
Experiments are executed offline with storage on the local filesystem. The system is a MacBook Pro (M2, 2022). The creation of directories and files is considered a performance cost.

For each experiment, we report the time in seconds (s). The reported results are averaged on `10` independent runs running in the foreground without parallelization.
The plots report the performance varying the number of experiments, runs, and values, with aggregates by method.

References and instructions to reproduce the results, as well as more details on the setup, can be found in the notebooks [Benchmarks rev1](https://github.com/elehcimd/mltraq/blob/devel/notebooks/07%20Tracking%20speed%20-%20Benchmarks%20rev1.ipynb) (`float` scalars) and [Benchmarks 2](https://github.com/elehcimd/mltraq/blob/fixes/notebooks/08%20Tracking%20speed%20-%20Benchmarks%202.ipynb) (`NumPy` arrays).

!!! Question "How can we improve this analysis?"
    In comparative analyses, there are always many nuances and little details that can make a big difference. You can [open a discussion](https://github.com/elehcimd/mltraq/discussions) to ask questions or create a change request on the [issue tracker](https://github.com/elehcimd/mltraq/issues) if you find any issues. There might be ways to tune the methods to improve their performance that we missed or other solutions worth considering
    we are not aware of.

!!! Warning
    * All solutions considered in this comparative analysis have positively impacted the industry and served as an inspiration to guide the design of MLtraq. The many references to W&B are a testament to their excellent community and documentation.
    * Mature and established solutions in the industry have needs beyond mere time performance and tend to prioritize backward compatibility, new features, and third-party integrations.

!!! Tip "Slides presenting some of the results"
    The slides from my talk at the Munich MLOps meetup on  "MLtraq: Track your AI experiments at hyperspeed" are available
    [here](../assets/pdf/2024.04.11%20mltraq_tracking_at_hyperspeed.pdf).
    


## Changelog

* 2024.04.11 - Added slides from Munich MLOps Community Meetup #7 alk "MLtraq: Track your AI experiments at hyperspeed"
* 2024.03.06 - Improved conclusions and added acknowledgments
* 2024.03.04 - Added FastTrackML, improved text and plots
* 2024.02.26 - Initial publication of results


## Why tracking speed matters

What makes fast-tracking so crucial? Let's explore its importance by examining the advantages from various perspectives.

### Initialization

The initialization of the tracking component can take more than `1s`, in some cases increasing linearly with the number of `runs`. High initialization times severely impact your ability to experiment on hundreds of thousands of possible configurations.
Furthermore, slow imports negatively impact development, CI/CD tests, and debugging speed. E.g., see this [W&B](https://github.com/wandb/wandb/issues/5440) ticket:

> [CLI]: wandb.init very slow #5440

Wouldn't loading and starting tracking at nearly zero time be nice?

!!! Success "A short time-to-track is instrumental for a smooth developer experience."
  
### High frequency

At times, it's necessary to record metrics that occur frequently. This situation arises when you log loss and metrics for every batch during training, rewards for each step of every episode during simulation, or outputs, media, and metrics for every input during analysis. E.g., see the notebook [Logging Strategies for High-Frequency Data](https://colab.research.google.com/github/wandb/examples/blob/master/colabs/wandb-log/Logging_Strategies_for_High_Frequency_Data.ipynb#scrollTo=1rINj_LsJfqJ) by W&B.

The fine-grained logging/debugging of complex algorithms (not necessarily AI/ML models) and handling of simulation data that changes quickly over time are other situations that require frequent tracking.

Workarounds to handle too much information come at a completeness/accuracy cost, including downsampling, summarization, and histograms. 

What if we can track more efficiently and avoid the workarounds?

!!! Success "Tracking with less limitations is more powerful and robust."

### Large, complex objects

Datasets, timeseries, forecasts, media files such as images, audio recordings, and videos can be categorized as "large, complex objects".

You might want to log a set of images at every step to inspect visually how the quality of the model is progressing, the datasets used in cross-validation with different configurations and random seeds, forecasts and other metrics, and more. Generally, you can produce a large quantity of heterogeneous information while executing complex algorithms that include, but are not limited to, ML/AI model training.

Most solutions have limited, primitive, and slow support for complex Python objects. What if you could track anything as frequently as you want?

!!! Success "Efficient tracking arbitrarily large, complex Python objects makes tracking more powerful."

## Tracking `float` values

In this set of experiments, we evaluate the tracking performance on `float` values varying the number of`runs` and `values`.

### Experiment 1 (Initialization time): How long does tracking a single value take?

We evaluate the time required to start a new experiment and track a single value. This experiment lets us compare the initialization time of the methods.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-1.svg" >
</p>

Threading and database management dominate the cost:

* `WandB` and `MLflow` are the worst performing, with threading and events management. `Aim` follows by spending most of the time creating and managing its embedded key-value store. They cost up to 400 times more than the other methods.

* `Comet` is next, with thread management dominating the cost.

* `FastTrackML` is remarkably fast to create new runs, offering API compatibility with MLFlow. Its efficiency is also due to the required server running in the background, eliminating most of the database initialization cost.

*  Writing to SQLite is the primary cost for `MLtraq`. **Neptune performs best with no threading, no SQLite database, and simply writing the tracking data to files.**

Lesson learned: The less you do, the faster you are!

### Experiment 2 (High frequency): How much time does it take to track 100-10K values?

An efficient experiment tracking initialization is essential, but monitoring many values fast is critical for any tracking solution.
In this experiment, we assess the time required to track and store up to 10,000 values.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-2.svg" >
</p>

* The speedup of `FastTrackML` is localized in the creation of new runs, but the insertion of new tracking records remains similarly expensive to `MLflow`. Their primary cost is due to their [entity-attribute-value](https://en.wikipedia.org/wiki/Entity–attribute–value_model) database model.

* `Aim` and `WandB` follow at a fraction of the cost.

* `Neptune`, `Comet`, and `MLtraq` are the highest-performing methods, with **MLtraq being the fastest, 100 times faster than WandB.**

!!! Tip
    The advantage of MLtraq is how the data is tracked and stored. It is hard to beat because it is very close to simply adding an element to an array and serializing it to an SQLite column value with the speedy [DATAPAK](../advanced/storage.md) serialization format.

### Experiment 3: How much time to track 10 runs?

Evaluating different configurations (hyperparameters, etc.) maps to multiple runs and executing many runs is critical.
This experiment compares how long it takes to execute `10` runs.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-3.svg" >
</p>

* Creating new runs scales poorly for some methods.
`WandB` and `MLflow` are the worst performing, followed by `Aim` at a fraction of the cost.

* `Comet`, `FastTrackML`, `Neptune`, and `MLtraq` are the best-performing methods, with **MLtraq being the fastest.**


### Experiment 4: How much time to track 100 runs?

In this experiment, we repeated Experiment 3 with `100` runs, limiting the comparison to `FastTrackML`, `Comet`, `Neptune`, and `MLtraq`.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-4.svg" >
</p>

* `Comet` is at least `20` times slower than the other methods. `FastTrackML` and `Neptune` follow, with **MLtraq being 10 times faster than the others.**


### Experiment 5: How much time to track 1K runs and 1K values?

The two standing methods are `MLtraq` and `Neptune`. Let's look at their performance as we increase runs and values.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks/exp-5.svg" >
</p>

As we increase the number of tracked values and runs, the gap between `MLtraq` and `Neptune` increases.
With no threading and no filesystem files to manage, it is the fastest method for realistic workloads.
**MLtraq is the best performing, 23 times faster than Neptune.**

## Tracking `NumPy` arrays

In this set of experiments, we evaluate the tracking performance on 1D `NumPy` arrays, varying the number of `arrays` and their `size`.
Besides initialization and high frequency, we also want to store large objects efficiently.

### Experiment 1 (Large objects): How long does tracking an array of length 1M take?

We evaluate the time required to start a new experiment and track a single array of length 1M (default dtype is `numpy.float64`), which is 8M bytes if written to disk. Most methods do not support the serialization of `NumPy` arrays, and the test procedures handle it explicitly.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-1.svg" >
</p>

* The `WandB` method is the worst performing, followed by `MLflow` and `Aim`.

* `Comet` and `Neptune` are next. `Neptune` encodes the arrays as images, [uuencoding](https://en.wikipedia.org/wiki/Uuencoding) them and embedding
the resulting text in a single JSON-formatted file. `Comet` adopts a JSON-like format, creating a single ZIP file that adds extra cost.

* `FastTrackML` is significantly faster than `MLflow` white, maintaining API compatibility, which is a remarkable result.

* **MLtraq is the best-performing method, 3 times faster than FastTrackML and 4 times faster than Neptune**.
Its higher performance is due to its speedier serialization strategy based on safe pickling and `NumPy` native binary serialization.
See [Data store](../advanced/datastore.md) for more details.

### Experiment 2: How long does tracking 1-10 arrays with length 10K-1M take?

In this experiment, we assess the time required to track multiple arrays of varying sizes, up to 1M.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-2.svg" >
</p>

Trends remain similar to Experiment 1, except `WandB` whose time explodes. We suspect this is due to the threading communication and its internal JSON serializer.

### Experiment 3: How long does it take to track 1-10K arrays with a length of 1K?

In this experiment, we assess the time required to track a large number of small-sized arrays.
The analysis is limited to the best-performing methods.

<p align="center">
  <img height="100%" width="100%" style="border-radius: 5px; border: 5px solid white;" src="/assets/img/benchmarks2/exp-3.svg" >
</p>

* `Comet` and `FastTrackML` perform similarly, followed by `Neptune`, which is `4` times faster.
* **MLtraq is the best-performing method, being 5 times faster than Neptune**.

## Conclusion

* **MLtraq is the fastest experiment-tracking solution for workloads with hundreds of thousands of runs and arbitrarily large, complex Python objects**. 
The primary goal of other solutions gravitates toward backward compatibility, third-party integrations, and complete model lifecycle management. Their support for rich modeling of experiments, runs, and complex Python objects is missing or limited. We believe these are essential capabilities in the experimentation phase worth optimizing.

* **Relying solely on the filesystem as a database is a recipe for low performance**.
As noted on the [SQLite website](https://www.sqlite.org/fasterthanfs.html), relying on a single file to store the local database copy could be
35% faster than a filesystem-based solution. The higher initialization cost of having a proper database pays off in scalability and reliability.
`MLtraq` provides the flexibility to choose where to store objects with the [Data store](../advanced/datastore.md) interface.

* If not implemented carefully, **the solutions that adopt threading to incorporate streaming capabilities pay the hidden cost of IPC (Inter-Process Communication)**. Further, the higher complexity results in more I/O errors and reliability concerns.

* The [entity-attribute-value](https://en.wikipedia.org/wiki/Entity–attribute–value_model) database model adopted by `MLflow` and `FastTrackML` requires **inserting a new record for every new tracked value**, making it painfully slow. Furthermore, the tracked value type is fixed to the SQL column type, resulting in limited flexibility.

* Most methods implement the **serialization of arrays and other complex, non-scalar objects with custom text encodings**, relying on [uuencoding](https://en.wikipedia.org/wiki/Uuencoding) and JSON-like formats. Compression is either missing or handled by creating ZIP files of artifacts stored on the filesystem. The process is slow, and the support for complex types is limited or missing: floating point and timestamp precision are ignored, etc. Arrow IPC, native serialization, zero-copy writes, and safe pickling provide superior performance and portability, as proved by `MLtraq`.

## Acknowledgments

Thank You for the constructive conversations that helped improve this analysis:

* Jonathan Giannuzzi and Alex Scammon from [FastTrackML](https://github.com/G-Research/fasttrackml) (a G-Research project)
