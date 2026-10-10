# SPEC: Simulador gráfico de autómatas

## Objetivo
Aplicación local (Python + Tkinter) que convierte un AFND a AFD, obtiene la expresión
regular (ER) de un autómata finito y verifica que AFND, AFD y ER son equivalentes.

## Entradas
- Estados, alfabeto (símbolos de un carácter), estado inicial, estados finales.
- Transiciones `origen,símbolo,destino`, una por línea. `ε` (o `eps`) = transición vacía.
- Se puede guardar y abrir el autómata como JSON.

## Salidas
- **Módulo 1:** tabla de conversión, AFND y AFD dibujados (óvalos, flechas, flecha de
  entrada al inicial, doble círculo en finales) y paso a paso (conjunto, símbolo, destino).
- **Módulo 2:** sistema de ecuaciones, cada sustitución y simplificación con el nombre de
  la regla (transición simple, varias transiciones, bucle, bucle más salida, estado final)
  y la ER final. Recibe el AFD del Módulo 1 o el autómata del editor.
- **Verificador:** prueba todas las cadenas de longitud 0 a n (n ≥ 6) y lista las que difieren.

## Restricciones
Solo librería estándar, un solo stack, sin servidor, sin internet ni APIs, se abre con `python app.py`.

## Casos límite cubiertos
- Estado pozo ∅ en el AFD (solo aparece si se alcanza).
- Estados inalcanzables (no entran al AFD) y estados sin camino a un final (se descartan en la ER).
- Alfabeto de un símbolo.
- Lenguaje vacío (sin finales): ER = ∅.
- Estado inicial final (acepta la cadena vacía).
- Transiciones ε (bonus): cerradura-ε en el inicial y en cada conjunto.

## Casos de referencia (Anexo A)
1. AFND de {q0,q1,q2} → AFD de 4 estados: {q0}, {q0,q1}, {q2} (final) y ∅.
2. AF con q0–x→q1, q1–x→q2, q2–y→q2, q2–y→q1 → ER `x(xy*y)*`.
