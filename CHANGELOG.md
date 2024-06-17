# Recent changes

## 0.1.138

* Added new steps `drop_fields` and `nothing`
* Added support for `return_as="generator_unordered"` for executing experiments to reduce time-to-failure

## 0.1.137

* Fixed some quoting typos in the docs and code
* Added blog post on serializing a bunch of things experimental results(blog/posts/009)
* Cleanup visibility of class methods and attributes (`_` and `__` prefix)
* Added PNG logo files with transparency for talks etc.

## 0.1.136

* Added slides from Munich MLOps Community Meetup #7, linked in the benchmarks/speed page
* Added notebooks/11 to experiment with the performance of different data storage options
* Added blog post on upstreaming experimental results (blog/posts/008)
* Renamed `session.load` to `session.load_experiment` and `session.persist` to `session.persist_experiment` for consistency

## 0.1.135

* Dropped `include_hidden` option support for archives, not supported by`glob.glob` in Python 3.10