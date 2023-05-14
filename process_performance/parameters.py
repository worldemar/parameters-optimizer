#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Parameters class providing generators to iterate over
    multi-dimensional space of several parameters
"""

import itertools
from process_performance.parameter import Parameter
from process_performance.shape import ParameterSpaceShape


def _tuple_to_dict(dicts: tuple):
    return {k: v for d in dicts for k, v in d.items()}


class Parameters():
    """
    Collection of parameters with generator helpers for iterating over
    parameter values space.
    """
    class WrongParametersType(RuntimeError):
        """WrongParametersType"""

    @classmethod
    def from_dict(cls, parameter_values_dict: dict[str:list[any]]):
        param_argv = []
        for name, values in parameter_values_dict.items():
            param_argv.append(Parameter(name=name, values=values))
        return Parameters(*param_argv)

    def __init__(self, *parameters):
        self._parameters = []
        for parameter in parameters:
            if isinstance(parameter, Parameter):
                self._parameters.append(parameter)
            else:
                raise Parameters.WrongParametersType(
                    'parameters arguments must be instances of Parameter')

    def gen(self, shape: ParameterSpaceShape):
        """
        Select generator by its string name.
        """
        return {
            ParameterSpaceShape.CORNERS: self._gen_corners,
            ParameterSpaceShape.EDGES: self._gen_edges,
            ParameterSpaceShape.CUBE: self._gen_cube
        }[shape]

    def _gen_corners(self):
        """
        Generates corners of multi-dimensional parameter cube.
        """
        generators = [p.gen_corners() for p in self._parameters]
        for value in itertools.product(*generators):
            yield _tuple_to_dict(value)

    def _gen_edges(self):
        """
            Generates edges of multi-dimensional parameter cube
            including corners.
            This generates corners more than once, they supposed
            to be skipped using value cache.
        """
        for p_line in self._parameters:
            generators = []
            for p_edge in self._parameters:
                if p_edge == p_line:
                    generators.append(p_line.gen_edge())
                else:
                    generators.append(p_edge.gen_corners())
            for value in itertools.product(*generators):
                yield _tuple_to_dict(value)

    def _gen_cube(self):
        """
        Generates all possible values of multi-dimensional parameter cube.
        """
        generators = [p.gen_cube() for p in self._parameters]
        for value in itertools.product(*generators):
            yield _tuple_to_dict(value)
