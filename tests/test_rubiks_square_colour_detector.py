import pytest
from collections import OrderedDict

from rubiks_square_colour_detector import (
    classify_color,
    assign_positions,
    cube_stickers,
    cube_layout,
    fomo_post_process,
)

class MockStats:
    def __init__(self, l, a, b):
        self._l = l
        self._a = a
        self._b = b

    def l_mean(self):
        return self._l

    def a_mean(self):
        return self._a

    def b_mean(self):
        return self._b


def test_classify_color():
    assert classify_color(MockStats(95, 0, 0)) == "white"
    assert classify_color(MockStats(50, 35, 40)) == "red"
    assert classify_color(MockStats(50, 20, 50)) == "orange"
    assert classify_color(MockStats(50, -20, 50)) == "yellow"
    assert classify_color(MockStats(50, -40, 20)) == "green"
    assert classify_color(MockStats(50, 10, -30)) == "blue"
    assert classify_color(MockStats(50, 0, 0)) == "?"


def test_assign_positions():
    centers = [(10, 10), (30, 10), (50, 10), (10, 30), (30, 30), (50, 30), (10, 50), (30, 50), (50, 50)]
    expected = {
        "top_left_corner": (10, 10),
        "middle_top": (30, 10),
        "top_right_corner": (50, 10),
        "middle_left": (10, 30),
        "center": (30, 30),
        "middle_right": (50, 30),
        "bottom_left_corner": (10, 50),
        "middle_bottom": (30, 50),
        "bottom_right_corner": (50, 50),
    }
    assert assign_positions(centers) == expected


def test_cube_stickers():
    layout_str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    expected = {
        "U": "[w][w][w][w][w][w][w][w][w]",
        "R": "[r][r][r][r][r][r][r][r][r]",
        "F": "[g][g][g][g][g][g][g][g][g]",
        "D": "[y][y][y][y][y][y][y][y][y]",
        "L": "[o][o][o][o][o][o][o][o][o]",
        "B": "[b][b][b][b][b][b][b][b][b]",
    }
    assert cube_stickers(layout_str) == expected


def test_cube_layout():
    layout_str = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    expected = (
        "\n"
        "         [w][w][w]\n"
        "         [w][w][w]\n"
        "         [w][w][w]\n"
        "[o][o][o][g][g][g][r][r][r][b][b][b]\n"
        "[o][o][o][g][g][g][r][r][r][b][b][b]\n"
        "[o][o][o][g][g][g][r][r][r][b][b][b]\n"
        "         [y][y][y]\n"
        "         [y][y][y]\n"
        "         [y][y][y]\n"
    )
    assert cube_layout(layout_str) == expected


def test_fomo_post_process():
    # Mock model, inputs, and outputs
    class MockModel:
        def __init__(self):
            self.output_shape = [(1, 3, 3, 1)]

    class MockInput:
        def __init__(self):
            self.roi = [0, 0, 240, 240]

    class MockOutput:
        def __getitem__(self, idx):
            return [[[0.5]]]

    model = MockModel()
    inputs = [MockInput()]
    outputs = [MockOutput()]
    result = fomo_post_process(model, inputs, outputs)
    assert len(result) == 1
    assert len(result[0]) == 1