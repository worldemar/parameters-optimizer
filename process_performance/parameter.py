#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    One parameter for command line.
    Provides generators to iterate over values.
"""

from process_performance.shape import ParameterSpaceShape


def _collapse_generator(values: list):
    """
        Yields all values starting from edges towards center
    """
    values = list(values)
    while True:
        if values:
            yield values.pop(0)
        if values:
            yield values.pop(-1)
        if not values:
            break


class Parameter():
    """
    Keeps single parameter name and values.

    Provides generators to iterate over values.
    """

    class NoValuesException(RuntimeError):
        """NoValuesException"""

    class NonStringNameException(RuntimeError):
        """NonStringNameException"""

    def __init__(self, name=None, values=None):
        self.name = name
        self.values = list(values)
        if not isinstance(name, str):
            raise Parameter.NonStringNameException(
                f'Parameter name "{name}" is not string')
        if len(self.values) < 1:
            raise Parameter.NoValuesException(
                f'Values vector "{values}" is too short ({len(self.values)})')

    def gen(self, shape: ParameterSpaceShape):
        return {
            ParameterSpaceShape.CORNERS: self.gen_corners,
            ParameterSpaceShape.EDGES: self.gen_edge,
            ParameterSpaceShape.CUBE: self.gen_cube,
        }[shape]

    def gen_corners(self):
        """
        Generates edge values of the parameter.
        """
        if len(self.values) == 1:
            yield {self.name: self.values[0]}
        else:
            yield {self.name: self.values[0]}
            yield {self.name: self.values[-1]}

    def gen_edge(self):
        """
        Generates all parameter values except.
        """
        for value in _collapse_generator(self.values[1:-1]):
            yield {self.name: value}

    def gen_cube(self):
        """
        Generates all parameter values ordered from edges towards center.
        """
        for value in _collapse_generator(self.values):
            yield {self.name: value}
