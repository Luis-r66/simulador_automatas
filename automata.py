"""Lógica pura del simulador de autómatas (sin interfaz, solo librería estándar).

Modelo de datos (diccionario, guardable como JSON):
    {"estados": ["q0", ...], "alfabeto": ["a", ...], "inicial": "q0",
     "finales": ["q2"], "transiciones": [["q0", "a", "q1"], ...]}
La transición vacía se escribe con el símbolo "ε".

Las expresiones regulares se guardan como árboles (tuplas) para poder
simplificarlas, mostrarlas y convertirlas al formato de la librería re.
"""
import itertools
import json
import re

EPS = "ε"
VACIO = ("vacio",)   # ∅
LAM = ("lam",)       # λ (cadena vacía)

EJEMPLOS = {
    "Caso 1": {
        "estados": ["q0", "q1", "q2"], "alfabeto": ["a", "b"], "inicial": "q0",
        "finales": ["q2"],
        "transiciones": [["q0", "a", "q0"], ["q0", "a", "q1"], ["q1", "b", "q2"]],
    },
    "Caso 2": {
        "estados": ["q0", "q1", "q2"], "alfabeto": ["x", "y"], "inicial": "q0",
        "finales": ["q1"],
        "transiciones": [["q0", "x", "q1"], ["q1", "x", "q2"],
                         ["q2", "y", "q2"], ["q2", "y", "q1"]],
    },
    "Ejemplo con ε": {
        "estados": ["q0", "q1", "q2"], "alfabeto": ["a", "b"], "inicial": "q0",
        "finales": ["q2"],
        "transiciones": [["q0", "ε", "q1"], ["q0", "a", "q0"],
                         ["q1", "b", "q2"], ["q2", "b", "q2"]],
    },
}


# ---------------------------------------------------------------- modelo
def validar(af):
    """Lanza ValueError con un mensaje claro si el autómata es inválido."""
    estados = af["estados"]
    if not estados:
        raise ValueError("Debe haber al menos un estado.")
    if len(set(estados)) != len(estados):
        raise ValueError("Hay estados repetidos.")
    if not af["alfabeto"]:
        raise ValueError("El alfabeto no puede estar vacío.")
    for s in af["alfabeto"]:
        if len(s) != 1 or s == EPS:
            raise ValueError(f"El símbolo '{s}' debe ser un solo carácter distinto de ε.")
    if af["inicial"] not in estados:
        raise ValueError("El estado inicial no está en la lista de estados.")
    for f in af["finales"]:
        if f not in estados:
            raise ValueError(f"El estado final '{f}' no existe.")
    for o, s, d in af["transiciones"]:
        if o not in estados or d not in estados:
            raise ValueError(f"La transición {o},{s},{d} usa un estado inexistente.")
        if s != EPS and s not in af["alfabeto"]:
            raise ValueError(f"La transición {o},{s},{d} usa un símbolo fuera del alfabeto.")


def automata_desde_texto(estados, alfabeto, inicial, finales, transiciones):
    """Construye y valida un autómata a partir de los textos del editor."""
    lista = lambda t: [x.strip() for x in t.replace(";", ",").split(",") if x.strip()]
    trans = []
    for linea in transiciones.splitlines():
        if not linea.strip():
            continue
        partes = [p for p in re.split(r"\s*,\s*|\s+", linea.strip()) if p]
        if len(partes) != 3:
            raise ValueError(f"Transición mal escrita: '{linea}'. Use origen,símbolo,destino.")
        o, s, d = partes
        if s.lower() in ("eps", "epsilon", "ε", "λ"):
            s = EPS
        if [o, s, d] not in trans:
            trans.append([o, s, d])
    af = {"estados": lista(estados), "alfabeto": lista(alfabeto),
          "inicial": inicial.strip(), "finales": lista(finales), "transiciones": trans}
    validar(af)
    return af


def guardar_json(af, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(af, archivo, ensure_ascii=False, indent=2)


def cargar_json(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        af = json.load(archivo)
    validar(af)
    return af


# ------------------------------------------------- AFND (con ε) → AFD
def nombre_conjunto(conjunto):
    """Nombre legible de un conjunto de estados: {q0,q1} o ∅."""
    return "∅" if not conjunto else "{" + ",".join(sorted(conjunto)) + "}"


def cerradura_e(af, conjunto):
    """Cerradura-ε: estados alcanzables desde el conjunto usando solo ε."""
    resultado, pila = set(conjunto), list(conjunto)
    while pila:
        p = pila.pop()
        for o, s, d in af["transiciones"]:
            if o == p and s == EPS and d not in resultado:
                resultado.add(d)
                pila.append(d)
    return frozenset(resultado)


def mover(af, conjunto, simbolo):
    """Estados a los que se llega desde el conjunto leyendo el símbolo."""
    return frozenset(d for o, s, d in af["transiciones"] if o in conjunto and s == simbolo)


def afnd_a_afd(afnd):
    """Método de subconjuntos. Devuelve (tabla, afd, pasos).

    tabla: lista de filas {"conjunto", "destinos": {símbolo: nombre}, "final"}
    afd:   autómata en el mismo modelo (estados con nombre {q0,q1} o ∅)
    pasos: lista de textos para el modo paso a paso
    """
    alfabeto, finales = afnd["alfabeto"], set(afnd["finales"])
    hay_eps = any(s == EPS for _, s, _ in afnd["transiciones"])
    inicio = cerradura_e(afnd, {afnd["inicial"]})
    pasos = [f"Estado inicial del AFD: " + (f"cerradura-ε({afnd['inicial']}) = " if hay_eps else "")
             + nombre_conjunto(inicio)]
    vistos, pendientes, tabla = [inicio], [inicio], []
    while pendientes:
        actual = pendientes.pop(0)
        destinos = {}
        for s in alfabeto:
            mov = mover(afnd, actual, s)
            dest = cerradura_e(afnd, mov)
            nuevo = dest not in vistos
            if nuevo:
                vistos.append(dest)
                pendientes.append(dest)
            destinos[s] = nombre_conjunto(dest)
            texto = f"Proceso {nombre_conjunto(actual)} con '{s}': mover = {nombre_conjunto(mov)}"
            if hay_eps:
                texto += f", cerradura-ε = {nombre_conjunto(dest)}"
            texto += f" → llega a {nombre_conjunto(dest)}"
            if not dest:
                texto += " (estado pozo ∅)"
            if nuevo:
                texto += " [conjunto nuevo: se agrega a pendientes]"
            pasos.append(texto)
        tabla.append({"conjunto": nombre_conjunto(actual), "destinos": destinos,
                      "final": bool(actual & finales)})
    pasos.append("No aparecen conjuntos nuevos: termina la construcción.")
    marcados = [f["conjunto"] for f in tabla if f["final"]]
    pasos.append("Estados finales (conjuntos que contienen un final del AFND): "
                 + (", ".join(marcados) if marcados else "ninguno"))
    afd = {"estados": [f["conjunto"] for f in tabla], "alfabeto": list(alfabeto),
           "inicial": nombre_conjunto(inicio), "finales": marcados,
           "transiciones": [[f["conjunto"], s, d] for f in tabla for s, d in f["destinos"].items()]}
    return tabla, afd, pasos


# ------------------------------------------- expresiones regulares (árbol)
def sim(c):
    return ("sim", c)


def cat(*xs):
    """Concatenación simplificada: ∅·r = ∅, λ·r = r, asociativa."""
    partes = []
    for x in xs:
        if x[0] == "vacio":
            return VACIO
        if x[0] == "lam":
            continue
        partes.extend(x[1] if x[0] == "cat" else [x])
    if not partes:
        return LAM
    return partes[0] if len(partes) == 1 else ("cat", tuple(partes))


def uni(*xs):
    """Unión simplificada: ∅ + r = r, r + r = r, asociativa."""
    partes = []
    for x in xs:
        if x[0] == "vacio":
            continue
        for h in (x[1] if x[0] == "uni" else (x,)):
            if h not in partes:
                partes.append(h)
    if not partes:
        return VACIO
    return partes[0] if len(partes) == 1 else ("uni", tuple(partes))


def est(x):
    """Estrella simplificada: ∅* = λ, λ* = λ, (r*)* = r*."""
    if x[0] in ("vacio", "lam"):
        return LAM
    return x if x[0] == "est" else ("est", x)


def a_texto(e):
    """ER legible: x(xy*y)*, con λ y ∅."""
    t = e[0]
    if t == "vacio":
        return "∅"
    if t == "lam":
        return "λ"
    if t == "sim":
        return e[1]
    if t == "cat":
        return "".join("(" + a_texto(h) + ")" if h[0] == "uni" else a_texto(h) for h in e[1])
    if t == "uni":
        return " + ".join(a_texto(h) for h in e[1])
    h = e[1]
    return (a_texto(h) if h[0] == "sim" else "(" + a_texto(h) + ")") + "*"


def a_regex_python(e):
    """Convierte el árbol a un patrón de la librería re (para el verificador)."""
    t = e[0]
    if t == "vacio":
        return "(?!)"
    if t == "lam":
        return "(?:)"
    if t == "sim":
        return re.escape(e[1])
    if t == "cat":
        return "".join(a_regex_python(h) for h in e[1])
    if t == "uni":
        return "(?:" + "|".join(a_regex_python(h) for h in e[1]) + ")"
    return "(?:" + a_regex_python(e[1]) + ")*"


# --------------------------------------------------- autómata → ER
def _estados_utiles(af):
    """Estados alcanzables desde el inicial y que llegan a algún final."""
    def alcanzar(inicios, pares):
        vistos, pila = set(inicios), list(inicios)
        while pila:
            x = pila.pop()
            for a, b in pares:
                if a == x and b not in vistos:
                    vistos.add(b)
                    pila.append(b)
        return vistos
    directos = [(o, d) for o, _, d in af["transiciones"]]
    inversos = [(d, o) for o, d in directos]
    ok = alcanzar({af["inicial"]}, directos) & alcanzar(set(af["finales"]), inversos)
    return [p for p in af["estados"] if p in ok]


def _ecuacion(p, E, K):
    """Texto de la ecuación de p: p = r1 q1 + r2 q2 + ... + constante."""
    terminos = []
    for q, c in E[p].items():
        if c[0] == "lam":
            terminos.append(q)
        else:
            t = a_texto(c)
            terminos.append(f"({t}) {q}" if c[0] == "uni" else f"{t} {q}")
    if K[p] != VACIO:
        terminos.append(a_texto(K[p]))
    return f"{p} = " + (" + ".join(terminos) if terminos else "∅")


def _regla_inicial(p, E, K):
    n = len(E[p])
    if K[p] == LAM:
        regla = "Estado final (p = λ)" + (" con varias transiciones" if n else "")
    elif n == 1:
        regla = "Transición simple (p = aq)"
    else:
        regla = "Varias transiciones (p = aq + br)"
    return regla + ("; contiene un bucle" if p in E[p] else "")


def af_a_er(af):
    """Sistema de ecuaciones por estado y eliminación. Devuelve (er, pasos).

    Funciona con AFD, AFND y AFND con ε (la transición ε aporta el coeficiente λ).
    """
    vivos = _estados_utiles(af)
    ini = af["inicial"]
    pasos = []
    descartados = [p for p in af["estados"] if p not in vivos]
    if ini not in vivos:
        return VACIO, ["Desde el estado inicial no se llega a ningún final: el lenguaje es vacío.\nER = ∅"]
    E = {p: {} for p in vivos}
    K = {p: VACIO for p in vivos}
    for o, s, d in af["transiciones"]:
        if o in E and d in E:
            E[o][d] = uni(E[o].get(d, VACIO), LAM if s == EPS else sim(s))
    for f in af["finales"]:
        if f in E:
            K[f] = LAM
    lineas = [f"  {_ecuacion(p, E, K)}      ← {_regla_inicial(p, E, K)}" for p in vivos]
    nota = ("\nRegla Estado inútil (p = ∅): se descartan " + ", ".join(descartados)
            + " (no alcanzables o sin camino a un final)." if descartados else "")
    pasos.append("Sistema de ecuaciones (una por estado):\n" + "\n".join(lineas) + nota)

    orden = [p for p in vivos if p != ini][::-1] + [ini]
    activos = list(vivos)
    for p in orden:
        if p in E[p]:
            antes = _ecuacion(p, E, K)
            r = est(E[p].pop(p))
            solo = not E[p] and K[p] == LAM
            regla = "Bucle (p = ap → a*)" if solo else "Bucle más salida (p = ap + bq → a*·bq)"
            E[p] = {q: cat(r, c) for q, c in E[p].items()}
            K[p] = cat(r, K[p])
            pasos.append(f"Regla: {regla}\n  {antes}\n  ⇒ {_ecuacion(p, E, K)}")
        if p == ini:
            break
        activos.remove(p)
        valor = _ecuacion(p, E, K)
        for s in activos:
            if p in E[s]:
                antes = _ecuacion(s, E, K)
                c = E[s].pop(p)
                for q, e in E[p].items():
                    E[s][q] = uni(E[s].get(q, VACIO), cat(c, e))
                K[s] = uni(K[s], cat(c, K[p]))
                pasos.append(f"Regla: Sustitución de {p} en {s} + simplificación "
                             f"(λ·r = r, ∅·r = ∅, r + r = r, asociatividad)\n"
                             f"  Valor de {valor}\n  {antes}\n  ⇒ {_ecuacion(s, E, K)}")
    pasos.append(f"Resultado: ER = {a_texto(K[ini])}")
    return K[ini], pasos


# ------------------------------------------------------------ verificador
def acepta(af, cadena):
    """Simula el autómata (AFD, AFND o con ε) sobre una cadena."""
    actual = cerradura_e(af, {af["inicial"]})
    for c in cadena:
        actual = cerradura_e(af, mover(af, actual, c))
        if not actual:
            return False
    return bool(actual & set(af["finales"]))


def verificar_equivalencia(afnd, afd, er, n):
    """Prueba todas las cadenas del alfabeto de longitud 0..n.

    Devuelve (total, diferencias); cada diferencia es (cadena, afnd, afd, er).
    """
    k = len(afnd["alfabeto"])
    if sum(k ** i for i in range(n + 1)) > 300000:
        raise ValueError("Demasiadas cadenas: reduzca n.")
    patron = re.compile(a_regex_python(er))
    diferencias, total = [], 0
    for largo in range(n + 1):
        for tupla in itertools.product(afnd["alfabeto"], repeat=largo):
            cadena = "".join(tupla)
            total += 1
            r = (acepta(afnd, cadena), acepta(afd, cadena), patron.fullmatch(cadena) is not None)
            if len(set(r)) > 1:
                diferencias.append((cadena,) + r)
    return total, diferencias
