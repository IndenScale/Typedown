import pytest
from typedown.core.parser.desugar import Desugarer

def test_desugar_simple_ref():
    # YAML parser might turn [[alice]] into [['alice']]
    input_data = [["alice"]]
    expected = "[[alice]]"
    assert Desugarer.desugar(input_data) == expected

def test_desugar_nested_dict():
    input_data = {
        "user": [["bob"]],
        "tags": ["friend", "colleague"]
    }
    expected = {
        "user": "[[bob]]",
        "tags": ["friend", "colleague"]
    }
    assert Desugarer.desugar(input_data) == expected

def test_desugar_list_of_refs():
    # [[a]], [[b]] parsed as [['a'], ['b']]
    input_data = [["a"], ["b"]]
    # Ideally [[a]], [[b]] in a list: [ [[a]], [[b]] ] -> [[['a']], [['b']]]
    # wait, if input is [ [[a]], [[b]] ], YAML parser gives [[['a']], [['b']]]
    
    complex_input = [[["a"]], [["b"]]]
    expected = ["[[a]]", "[[b]]"]
    assert Desugarer.desugar(complex_input) == expected

def test_desugar_deeply_nested_ref():
    input_data = {"meta": {"target": [["system/core"]]}}
    expected = {"meta": {"target": "[[system/core]]"}}
    assert Desugarer.desugar(input_data) == expected
