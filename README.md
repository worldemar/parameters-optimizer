![Python test and lint](https://github.com/worldemar/process-performance/workflows/Python%20test%20and%20lint/badge.svg)
[![codecov](https://codecov.io/gh/worldemar/process-performance/branch/master/graph/badge.svg?token=W8XKDQ2YIC)](https://codecov.io/gh/worldemar/process-performance)

# Process performance analysis tool

## What

Python-based tool to facilitate finding optimal parameters for executable.

## Why

There are situations when optimal parameters of certain process is unclear. Notable examples are:
- Packing firmware for embedded devices

  - There are several options that control both speed of compression and final firmware size

  - For production environment it may be beneficial to have smallest possible firmware in order to reduce flashing time, but wasting hours of CI time for it may not be desirable

  - For development environment it may be beneficial to have shortest packaging time to reduce testing time, but resulting firmware could be too big to efficiently handle

  All of those factors require finding "sweet spot" within all possible compression flags combinations.

- Archiving specific content

  There is no guarantee that archiver will find best possible algorithm for compressing your data and meet requirements of compression time and file size.

- Compiling specific code

  Since there are many options for optimizing C/C++ code, it may be time consuming to find optimal ones for your specific code. As an example, try to answer "When `-O3` is better than `-Os`?".

## Usage example

See [example_xz.py](example_xz.py), demonstrating implementation for xz compression.

To use it:
- **Implement InvokeContextInterface interface in a custom class**. That will allow you to define starting conditions for an executable, collect data and format parameters for it.
- **Instantiate Parameters class**. That will alow you to define possible parameter values for your executable.
- **call `run`**. That will run executable and collect data, calling methods in your custom class. You can specify different methods of iterating over parameter space: checking corner cases, checking edges or entire space. `run` returns list of data points for you to analyze. Those can be easily saved to csv for exporting to other software or analyzed directly with matplotlib.


