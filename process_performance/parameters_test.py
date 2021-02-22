#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Tests for Parameters class
"""

import pytest
from process_performance.parameters import Parameters

test_generators_data = [
    (
        {
            "p1": [1, 2, 3],
            "p2": ["a", "b"],
            "p3": ["normal"],
        },
        [
            ({'p1': 1}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'b'}, {'p3': 'normal'})
        ],
        [
            ({'p1': 1}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 2}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 2}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'b'}, {'p3': 'normal'})
        ],
        [
            ({'p1': 1}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 1}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 2}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 2}, {'p2': 'b'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'a'}, {'p3': 'normal'}),
            ({'p1': 3}, {'p2': 'b'}, {'p3': 'normal'})
        ]
    )
]


@pytest.mark.parametrize("params,corners,cube,fill", test_data)
def test_generators(params, corners, cube, fill):
    """test_generators"""
    param_space = Parameters(params)
    assert list(param_space.gen_corners()) == corners
    assert list(param_space.gen_cube()) == cube
    assert list(param_space.gen_fill()) == fill


def test_wrong_parameters():
    """test_no_values"""
    with pytest.raises(Parameters.WrongParametersType):
        Parameters([])
