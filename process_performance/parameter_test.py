#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Tests for Parameter class
"""

import pytest
from process_performance.shape import ParameterSpaceShape
from process_performance.parameter import _collapse_generator, Parameter


def test_nonstring_name():
    with pytest.raises(Parameter.NonStringNameException):
        Parameter(name=1, values=[1])


def test_no_values():
    with pytest.raises(Parameter.NoValuesException):
        Parameter(name="p1", values=[])


collapse_data = (
    ([1,2,3,4,5], [1,5,2,4,3]),
    ('abcdefg', ['a', 'g', 'b', 'f', 'c', 'e', 'd']),
)


@pytest.mark.parametrize("values,collapse", collapse_data)
def test_collapse_generator(values, collapse):
    assert list(_collapse_generator(values)) == collapse


test_generators_data = [
    (
        "p1",
        [1],
        {
            ParameterSpaceShape.CORNERS: [{"p1": 1}],
            ParameterSpaceShape.EDGES: [],
            ParameterSpaceShape.CUBE: [{"p1": 1}],
        }
    ),
    (
        "p1",
        [1, 2],
        {
            ParameterSpaceShape.CORNERS: [{"p1": 1}, {"p1": 2}],
            ParameterSpaceShape.EDGES: [],
            ParameterSpaceShape.CUBE: [{"p1": 1}, {"p1": 2}],
        }
    ),
    (
        "p1",
        [1, 2, 3, 4],
        {
            ParameterSpaceShape.CORNERS: [{"p1": 1}, {"p1": 4}],
            ParameterSpaceShape.EDGES: [{"p1": 2}, {"p1": 3}],
            ParameterSpaceShape.CUBE: [{"p1": 1}, {"p1": 4}, {"p1": 2}, {"p1": 3}],
        }
    )
]


@pytest.mark.parametrize("shape", [ParameterSpaceShape.CORNERS, ParameterSpaceShape.EDGES, ParameterSpaceShape.CUBE])
@pytest.mark.parametrize("name,values,shapes", test_generators_data)
def test_generators(shape, name, values, shapes):
    param = Parameter(name=name, values=values)
    assert list(param.gen(shape)()) == shapes[shape]
