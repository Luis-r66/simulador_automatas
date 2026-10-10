"""Pruebas de la lógica pura. Ejecutar: python -m unittest -v"""
import copy
import re
import unittest

import automata as A

CASO1 = A.EJEMPLOS["Caso 1"]
CASO2 = A.EJEMPLOS["Caso 2"]
CON_EPS = A.EJEMPLOS["Ejemplo con ε"]


def flujo(afnd, n=8):
    """AFND → AFD → ER y verificación. Devuelve (afd, er, total, diferencias)."""
    _, afd, _ = A.afnd_a_afd(afnd)
    er, _ = A.af_a_er(afd)
    total, dif = A.verificar_equivalencia(afnd, afd, er, n)
    return afd, er, total, dif


class PruebasAnexoA(unittest.TestCase):
    def test_caso1_afd_esperado(self):
        tabla, afd, _ = A.afnd_a_afd(CASO1)
        self.assertEqual(set(afd["estados"]), {"{q0}", "{q0,q1}", "{q2}", "∅"})
        self.assertEqual(afd["inicial"], "{q0}")
        self.assertEqual(afd["finales"], ["{q2}"])
        esperado = {("{q0}", "a"): "{q0,q1}", ("{q0}", "b"): "∅",
                    ("{q0,q1}", "a"): "{q0,q1}", ("{q0,q1}", "b"): "{q2}",
                    ("{q2}", "a"): "∅", ("{q2}", "b"): "∅",
                    ("∅", "a"): "∅", ("∅", "b"): "∅"}
        obtenido = {(o, s): d for o, s, d in afd["transiciones"]}
        self.assertEqual(obtenido, esperado)

    def test_caso2_er_esperada(self):
        er, _ = A.af_a_er(CASO2)
        self.assertEqual(A.a_texto(er), "x(xy*y)*")
        esperada = re.compile(r"x(?:xy*y)*")
        patron = re.compile(A.a_regex_python(er))
        for largo in range(9):
            for t in __import__("itertools").product("xy", repeat=largo):
                c = "".join(t)
                self.assertEqual(bool(patron.fullmatch(c)), bool(esperada.fullmatch(c)), c)

    def test_caso2_pasos_nombran_reglas(self):
        _, pasos = A.af_a_er(CASO2)
        texto = "\n".join(pasos)
        for regla in ("Transición simple", "Varias transiciones", "Estado final",
                      "Bucle más salida", "Sustitución"):
            self.assertIn(regla, texto)


class PruebasVerificador(unittest.TestCase):
    def test_flujo_caso1_equivalente(self):
        _, er, total, dif = flujo(CASO1)
        self.assertEqual(dif, [])
        self.assertEqual(total, 2 ** 9 - 1)

    def test_flujo_caso2_equivalente(self):
        self.assertEqual(flujo(CASO2)[3], [])

    def test_con_transiciones_epsilon(self):
        afd, _, _, dif = flujo(CON_EPS)
        self.assertEqual(dif, [])
        self.assertTrue(A.acepta(CON_EPS, "b"))      # q0 -ε-> q1 -b-> q2
        self.assertTrue(A.acepta(CON_EPS, "aabb"))
        self.assertFalse(A.acepta(CON_EPS, "a"))

    def test_detecta_diferencias(self):
        afd, er, _, _ = flujo(CASO1)
        roto = copy.deepcopy(afd)
        roto["finales"].append("{q0,q1}")
        _, dif = A.verificar_equivalencia(CASO1, roto, er, 6)
        self.assertTrue(dif)
        self.assertIn("a", [d[0] for d in dif])


class PruebasCasosLimite(unittest.TestCase):
    def test_alfabeto_de_un_simbolo(self):
        af = {"estados": ["p", "q"], "alfabeto": ["a"], "inicial": "p",
              "finales": ["q"], "transiciones": [["p", "a", "q"]]}
        afd, er, _, dif = flujo(af)
        self.assertEqual(dif, [])
        self.assertEqual(A.a_texto(er), "a")

    def test_estado_inalcanzable_no_aparece(self):
        af = copy.deepcopy(CASO1)
        af["estados"].append("q9")
        af["transiciones"].append(["q9", "a", "q2"])
        afd, _, _, dif = flujo(af)
        self.assertNotIn("q9", "".join(afd["estados"]))
        self.assertEqual(dif, [])

    def test_lenguaje_vacio(self):
        af = copy.deepcopy(CASO1)
        af["finales"] = []
        _, er, _, dif = flujo(af)
        self.assertEqual(A.a_texto(er), "∅")
        self.assertEqual(dif, [])

    def test_estado_inicial_final_acepta_vacia(self):
        af = {"estados": ["p"], "alfabeto": ["a"], "inicial": "p", "finales": ["p"],
              "transiciones": [["p", "a", "p"]]}
        afd, er, _, dif = flujo(af)
        self.assertEqual(A.a_texto(er), "a*")
        self.assertEqual(dif, [])

    def test_validacion(self):
        with self.assertRaises(ValueError):
            A.automata_desde_texto("q0,q1", "a", "q9", "q1", "q0,a,q1")
        with self.assertRaises(ValueError):
            A.automata_desde_texto("q0,q1", "a", "q0", "q1", "q0,z,q1")

    def test_lectura_de_texto(self):
        af = A.automata_desde_texto("q0, q1", "a, b", "q0", "q1", "q0,a,q1\nq0,eps,q1\n")
        self.assertIn(["q0", "ε", "q1"], af["transiciones"])


if __name__ == "__main__":
    unittest.main()
