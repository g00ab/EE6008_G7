import pytest
from unittest.mock import patch
import sys
import os

# Add the parent directory to the system path to allow importing error_handling
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from error_handling import (
    prompt_user_string,
    prompt_user_errors,
    prompt_user_cube,
    prompt_user_color,
    string_correction,
    parse_kociemba_solution,
    solving_cube,
)

# Test for prompt_user_string
@patch("builtins.input", side_effect=["UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"])
def test_prompt_user_string_valid(mock_input):
    assert prompt_user_string() == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

@patch("builtins.input", side_effect=["invalid", "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"])
def test_prompt_user_string_invalid_then_valid(mock_input):
    assert prompt_user_string() == "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

# Test for prompt_user_errors
@patch("builtins.input", side_effect=["2"])
def test_prompt_user_errors(mock_input):
    assert prompt_user_errors() == 2

# Test for prompt_user_cube
@patch("builtins.input", side_effect=["3", "5"])
def test_prompt_user_cube_valid(mock_input):
    assert prompt_user_cube() == (3, 5)

@patch("builtins.input", side_effect=["7", "3", "5"])
def test_prompt_user_cube_invalid_then_valid(mock_input):
    assert prompt_user_cube() == (3, 5)

# Test for prompt_user_color
@patch("builtins.input", side_effect=["red"])
def test_prompt_user_color_valid(mock_input):
    assert prompt_user_color() == "R"

@patch("builtins.input", side_effect=["invalid", "blue"])
def test_prompt_user_color_invalid_then_valid(mock_input):
    assert prompt_user_color() == "B"

# Test for string_correction
def test_string_correction():
    string_output = list("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
    corrected_string = string_correction(string_output, 2, 5, "G")
    assert corrected_string[13] == "G"  # 13th index corresponds to side 2, square 5

# Test for parse_kociemba_solution
def test_parse_kociemba_solution():
    solution_string = "U R2 F' D2 L B"
    parsed_moves = parse_kociemba_solution(solution_string)
    assert len(parsed_moves) == 6
    assert parsed_moves[0]["face_name"] == "Up/Top"
    assert parsed_moves[1]["modifier"] == "2"
    assert parsed_moves[2]["direction"] == "counter-clockwise (-90°)"

# Test for solving_cube
@patch("error_handling.kociemba.solve", return_value="U R2 F' D2 L B")
def test_solving_cube(mock_solve, capsys):
    solving_cube("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
    captured = capsys.readouterr()
    assert "🧩 Formatted Solution Steps:" in captured.out
    assert "📝 Solution in standard notation:" in captured.out