# Simulador gráfico de autómatas (AFND → AFD → ER)

Parcial 2.º corte de Teoría de la Computación. Python + Tkinter, sin internet y sin dependencias.

## Ejecutar
```
python app.py
```
Pruebas: `python -m unittest -v`

## Uso
1. **Autómata (AFND):** escribe estados, alfabeto, inicial, finales y transiciones (`origen,símbolo,destino`;
   `ε` para vacías), o carga uno de los ejemplos.
2. **AFND → AFD:** muestra tabla, ambos dibujos y el paso a paso.
3. **Autómata → ER:** sistema de ecuaciones con el nombre de cada regla; puede partir del AFD del módulo 1
   o del autómata del editor.
4. **Verificador:** compara AFND, AFD y ER con todas las cadenas hasta la longitud n elegida.

## Estructura
Ver `ARQUITECTURA.md`. Requisitos y casos límite en `SPEC.md`.
