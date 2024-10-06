# Recent changes

## 0.1.153
* Updated dependencies

## 0.1.153
* Added Python and MLtraq version to experiment's metadata
* Added `utils/sysenv.py` to track environment stats (system, architecture, locale, time, ...)
* Added `utils/reproducibility.py`, providing a temporary seed context
* Added `utils/plotting.py`, providing a temporary plot context for a single axes
* Removed `utils/plot.py` due to lack of usage (and unlikely usage in the future)
* Improved `BaseOptions.get(...)` with `prefer` and `otherwise` parameters to make it more flexible

## 0.1.152
* Increased tests to `87%` coverage

## 0.1.149
* Using `Union[x,y]` instead of `x|y` for type definitions for increased Python 3.9 compatibility
* Added a read-only mode for `BunchStore`, preventing an unnecessary write check
* Added support for local files in `fetch` module

## 0.1.148
* Fixed a race condition in `BunchStore`
* Added support for Python 3.9
* Verified tests on latest versions of dependencies

## 0.1.146
* Added missing `__init__.py` file

## 0.1.145
* Cleanup and update of dependencies

## 0.1.143
* Improved `BunchStore` class overloading also `__delitem__` and `__iter__`
* Added SVG optimizer (smaller SVGs, no timestamps that cause git changes)

## 0.1.141
* Default value for `create_tables` of `Database` class constructor changed to False, allowing the usage of this class also for use cases beyond managing MLtraq DBs.
* Added class `BunchStore` to handle a `Bunch` class transparently on memory and filesystem.
* Added blog post on how to use `return_as=generator_unordered` and fail fast (blog/posts/011)
* Added blog post on how to handle secrets with dynamic `Options` (blog/posts/012)
* Added blog post on `BunchStore` to handle caches and more (blog/posts/013)

## 0.1.140
* Fixed some typos in tests and docs
* Added blog post on `BunchEvent` (blog/posts/010)

## 0.1.139
* Added `BunchEvent` type, a Bunch with function triggers for setters and getters

## 0.1.138
* Added utility steps `drop_fields` and `nothing`

## 0.1.137

* Fixed some quoting typos in the docs and code
* Added blog post on serializing a `Bunch` of things (blog/posts/009)
* Cleanup visibility of class methods and attributes (`_` and `__` prefix)
* Added PNG logo files with transparency for talks etc.

## 0.1.136

* Added slides from Munich MLOps Community Meetup #7, linked in the benchmarks/speed page
* Added notebooks/11 to experiment with the performance of different data storage options
* Added blog post on upstreaming experimental results (blog/posts/008)
* Renamed `session.load` to `session.load_experiment` and `session.persist` to `session.persist_experiment` for consistency

## 0.1.135

* Dropped `include_hidden` option support for archives, not supported by`glob.glob` in Python 3.10
