# Arquitectura y modelo de datos

## Estructura
```
simulador_automatas/
├── app.py              # interfaz Tkinter (solo muestra datos y recibe acciones)
├── automata.py         # lógica pura, sin interfaz
├── test_automatas.py   # pruebas automáticas (unittest)
├── SPEC.md  ARQUITECTURA.md  README.md
```

## Modelo de datos del autómata (diccionario / JSON)
```json
{"estados": ["q0","q1","q2"], "alfabeto": ["a","b"], "inicial": "q0",
 "finales": ["q2"], "transiciones": [["q0","a","q0"], ["q0","a","q1"], ["q1","b","q2"]]}
```
El AFD resultante usa el mismo modelo, con estados llamados `{q0,q1}` o `∅`.

## Flujo de información
```
Editor (texto) ──automata_desde_texto──► AFND (dict)
AFND ──afnd_a_afd──► tabla + AFD (dict) + pasos ──► tabla, dibujos, paso a paso
AFD o AF ──af_a_er──► ER (árbol) + pasos ──► texto con a_texto
AFND + AFD + ER ──verificar_equivalencia(n)──► (total, diferencias)
```
- `app.py` llama funciones de `automata.py`; `automata.py` nunca importa Tkinter.
- La ER es un árbol de tuplas (`sim`, `cat`, `uni`, `est`, `lam`, `vacio`) para simplificar
  mientras se construye; `a_texto` la muestra y `a_regex_python` la pasa a `re` solo para verificar.
