import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.run_query import parse_response


class FakeMessage:
    def __init__(self, content):
        self.content = content

class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)

class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


def test_parse_response_json_valido():
    contenido_valido = '{"answer": "Sí, aceptamos Yape.", "confidence": 0.9, "actions": []}'
    response = FakeResponse(contenido_valido)

    resultado = parse_response(response)

    assert "answer" in resultado
    assert "confidence" in resultado
    assert "actions" in resultado
    assert isinstance(resultado["answer"], str)
    assert isinstance(resultado["confidence"], float)
    assert isinstance(resultado["actions"], list)
    assert 0.0 <= resultado["confidence"] <= 1.0


def test_parse_response_json_invalido():
    contenido_invalido = "esto no es JSON"
    response = FakeResponse(contenido_invalido)

    resultado = parse_response(response)

    assert resultado["confidence"] == 0.0
    assert "revisar_manualmente" in resultado["actions"]