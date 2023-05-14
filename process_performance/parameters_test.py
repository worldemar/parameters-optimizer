#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Tests for Parameters class
"""

import pytest

from process_performance.parameters import ParameterSpaceShape, Parameters
from process_performance.parameters import _tuple_to_dict

test_generators_data = [
    (
        {
            "x": [1],
        },
        {
            ParameterSpaceShape.CORNERS:
                [
                    {'x': 1},
                ],
            ParameterSpaceShape.EDGES:
                [
                ],
            ParameterSpaceShape.CUBE:
                [
                    {'x': 1},
                ],
        }
    ),
    (
        {
            "x": [1],
            "y": [1, 2, 3],
        },
        {
            ParameterSpaceShape.CORNERS:
                [
                    {'x': 1, 'y': 1},
                    {'x': 1, 'y': 3},
                ],
            ParameterSpaceShape.EDGES:
                [
                    {'x': 1, 'y': 2},
                ],
            ParameterSpaceShape.CUBE:
                [
                    {'x': 1, 'y': 1},
                    {'x': 1, 'y': 3},
                    {'x': 1, 'y': 2},
                ],
        }
    ),
    (
        {
            "x": [1, 2],
            "y": ['i', 'j'],
        },
        {
            ParameterSpaceShape.CORNERS:
                [
                    {'x': 1, 'y': 'i'},
                    {'x': 1, 'y': 'j'},
                    {'x': 2, 'y': 'i'},
                    {'x': 2, 'y': 'j'},
                ],
            ParameterSpaceShape.EDGES:
                [
                ],
            ParameterSpaceShape.CUBE:
                [
                    {'x': 1, 'y': 'i'},
                    {'x': 1, 'y': 'j'},
                    {'x': 2, 'y': 'i'},
                    {'x': 2, 'y': 'j'},
                ],
        }
    ),
    (
        {
            "p1": [1, 2, 3],
            "p2": ['a', 'b', 'c'],
            "p3": ['x', 'y', 'z'],
        },
        {
            ParameterSpaceShape.CORNERS:
                [
                    {'p1': 1, 'p2': 'a', 'p3': 'x'},
                    {'p1': 1, 'p2': 'a', 'p3': 'z'},
                    {'p1': 1, 'p2': 'c', 'p3': 'x'},
                    {'p1': 1, 'p2': 'c', 'p3': 'z'},

                    {'p1': 3, 'p2': 'a', 'p3': 'x'},
                    {'p1': 3, 'p2': 'a', 'p3': 'z'},
                    {'p1': 3, 'p2': 'c', 'p3': 'x'},
                    {'p1': 3, 'p2': 'c', 'p3': 'z'},
                ],
            ParameterSpaceShape.EDGES:
                [
                    {'p1': 2, 'p2': 'a', 'p3': 'x'},
                    {'p1': 2, 'p2': 'a', 'p3': 'z'},
                    {'p1': 2, 'p2': 'c', 'p3': 'x'},
                    {'p1': 2, 'p2': 'c', 'p3': 'z'},

                    {'p1': 1, 'p2': 'b', 'p3': 'x'},
                    {'p1': 1, 'p2': 'b', 'p3': 'z'},
                    {'p1': 3, 'p2': 'b', 'p3': 'x'},
                    {'p1': 3, 'p2': 'b', 'p3': 'z'},

                    {'p1': 1, 'p2': 'a', 'p3': 'y'},
                    {'p1': 1, 'p2': 'c', 'p3': 'y'},
                    {'p1': 3, 'p2': 'a', 'p3': 'y'},
                    {'p1': 3, 'p2': 'c', 'p3': 'y'}
                ],
            ParameterSpaceShape.CUBE:
                [
                    {'p1': 1, 'p2': 'a', 'p3': 'x'},
                    {'p1': 1, 'p2': 'a', 'p3': 'z'},
                    {'p1': 1, 'p2': 'a', 'p3': 'y'},

                    {'p1': 1, 'p2': 'c', 'p3': 'x'},
                    {'p1': 1, 'p2': 'c', 'p3': 'z'},
                    {'p1': 1, 'p2': 'c', 'p3': 'y'},

                    {'p1': 1, 'p2': 'b', 'p3': 'x'},
                    {'p1': 1, 'p2': 'b', 'p3': 'z'},
                    {'p1': 1, 'p2': 'b', 'p3': 'y'},

                    {'p1': 3, 'p2': 'a', 'p3': 'x'},
                    {'p1': 3, 'p2': 'a', 'p3': 'z'},
                    {'p1': 3, 'p2': 'a', 'p3': 'y'},

                    {'p1': 3, 'p2': 'c', 'p3': 'x'},
                    {'p1': 3, 'p2': 'c', 'p3': 'z'},
                    {'p1': 3, 'p2': 'c', 'p3': 'y'},

                    {'p1': 3, 'p2': 'b', 'p3': 'x'},
                    {'p1': 3, 'p2': 'b', 'p3': 'z'},
                    {'p1': 3, 'p2': 'b', 'p3': 'y'},

                    {'p1': 2, 'p2': 'a', 'p3': 'x'},
                    {'p1': 2, 'p2': 'a', 'p3': 'z'},
                    {'p1': 2, 'p2': 'a', 'p3': 'y'},

                    {'p1': 2, 'p2': 'c', 'p3': 'x'},
                    {'p1': 2, 'p2': 'c', 'p3': 'z'},
                    {'p1': 2, 'p2': 'c', 'p3': 'y'},

                    {'p1': 2, 'p2': 'b', 'p3': 'x'},
                    {'p1': 2, 'p2': 'b', 'p3': 'z'},
                    {'p1': 2, 'p2': 'b', 'p3': 'y'},
                ],
        },
    )
]


@pytest.mark.parametrize("shape", [
    ParameterSpaceShape.CORNERS,
    ParameterSpaceShape.EDGES,
    ParameterSpaceShape.CUBE])
@pytest.mark.parametrize("params,shapes", test_generators_data)
def test_generators(shape, params, shapes):
    parameters = Parameters.from_dict(parameter_values_dict=params)
    generated_parameter_space = list(parameters.gen(shape)())
    print(generated_parameter_space)
    assert generated_parameter_space == shapes[shape]


def test_wrong_parameters():
    with pytest.raises(Parameters.WrongParametersType):
        Parameters([])


tuple_to_dict_data = [
    [({'a': 1},), {'a': 1}],
    [({'a': 1}, {'b': 2}), {'a': 1, 'b': 2}],
    [({'a': 1, 'b': 2}, {'c': 3, 'b': 2}), {'a': 1, 'b': 2, 'c': 3}],
]


@pytest.mark.parametrize('tuple_data,dict_data', tuple_to_dict_data)
def test_tuple_to_dict(tuple_data, dict_data):
    assert _tuple_to_dict(tuple_data) == dict_data
