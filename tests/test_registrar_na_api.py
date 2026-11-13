import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


def load_production_function():
    source = Path("bot.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "registrar_na_api"
    )
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"API_URL": "https://api.example.test", "requests": None}
    exec(compile(module, "bot.py", "exec"), namespace)
    return namespace


class FakeResponse:
    def __init__(self, data=None, status_error=None, json_error=None):
        self.data = data
        self.status_error = status_error
        self.json_error = json_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def json(self):
        if self.json_error:
            raise self.json_error
        return self.data


class RegistrarNaApiTests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_production_function()
        self.calls = []

        def fake_post(url, **kwargs):
            self.calls.append((url, kwargs))
            return self.response

        self.namespace["requests"] = SimpleNamespace(post=fake_post)
        self.payload = {"usuario": "Teste", "discord_id": "123", "valor": 1000}

    def test_confirma_somente_resposta_ok_true(self):
        self.response = FakeResponse(data={"ok": True})
        result = self.namespace["registrar_na_api"]("vs", self.payload)
        self.assertIs(result, True)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][0], "https://api.example.test/vs")
        self.assertEqual(self.calls[0][1]["json"], self.payload)
        self.assertEqual(self.calls[0][1]["timeout"], (5, 20))

    def test_http_error_nao_confirma_registro(self):
        self.response = FakeResponse(status_error=RuntimeError("HTTP 500"))
        with self.assertRaisesRegex(RuntimeError, "HTTP 500"):
            self.namespace["registrar_na_api"]("f1", self.payload)
        self.assertEqual(len(self.calls), 1)

    def test_resposta_json_invalida_nao_confirma_registro(self):
        self.response = FakeResponse(json_error=ValueError("JSON inválido"))
        with self.assertRaisesRegex(RuntimeError, "resposta inválida"):
            self.namespace["registrar_na_api"]("vs", self.payload)
        self.assertEqual(len(self.calls), 1)

    def test_resposta_sem_ok_true_nao_confirma_registro(self):
        for data in ({"ok": False}, {}, [], None):
            with self.subTest(data=data):
                self.response = FakeResponse(data=data)
                with self.assertRaisesRegex(RuntimeError, "não confirmou"):
                    self.namespace["registrar_na_api"]("f1", self.payload)
        self.assertEqual(len(self.calls), 4)

    def test_api_url_ausente_interrompe_sem_requisicao(self):
        self.namespace["API_URL"] = None
        with self.assertRaisesRegex(RuntimeError, "API_URL"):
            self.namespace["registrar_na_api"]("vs", self.payload)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
