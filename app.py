"""Simulador gráfico de autómatas (Tkinter). Ejecutar: python app.py

Solo usa la librería estándar y funciona sin internet. La lógica vive en
automata.py; este archivo solo muestra datos y recibe acciones del usuario.
"""
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import automata as A


class Lienzo(tk.Canvas):
    """Dibuja un autómata con la notación de clase: óvalos, flechas,
    flecha de entrada al inicial y doble círculo en los finales."""

    def __init__(self, master, **kw):
        super().__init__(master, bg="white", highlightthickness=1,
                         highlightbackground="#888", **kw)
        self.af, self.titulo = None, ""
        self.bind("<Configure>", lambda e: self.redibujar())

    def dibujar(self, af, titulo=""):
        self.af, self.titulo = af, titulo
        self.redibujar()

    def redibujar(self):
        self.delete("all")
        if not self.af:
            return
        af = self.af
        w, h = max(self.winfo_width(), 300), max(self.winfo_height(), 250)
        orden = [af["inicial"]] + [e for e in af["estados"] if e != af["inicial"]]
        n = len(orden)
        R = max(22, min(42, 4 * max(len(e) for e in orden) + 10))
        radio = 0 if n == 1 else max(0, min(w, h) / 2 - R - 45)
        pos, ang = {}, {}
        for i, e in enumerate(orden):
            a = math.pi + 2 * math.pi * i / n
            pos[e] = (w / 2 + radio * math.cos(a), h / 2 + radio * math.sin(a))
            ang[e] = a
        self.create_text(8, 8, anchor="nw", text=self.titulo, font=("Arial", 10, "bold"))
        grupos = {}
        for o, s, d in af["transiciones"]:
            grupos.setdefault((o, d), []).append(s)
        for (o, d), simbolos in grupos.items():
            etiqueta = ",".join(sorted(set(simbolos)))
            if o == d:
                a = -math.pi / 2 if n == 1 else ang[o] + (1.0 if o == af["inicial"] else 0)
                self._lazo(pos[o], a, R, etiqueta)
            else:
                self._flecha(pos[o], pos[d], (d, o) in grupos, R, etiqueta)
        for e in orden:
            self._estado(e, pos[e], ang[e], R, e == af["inicial"], e in af["finales"])

    def _estado(self, nombre, p, a, R, inicial, final):
        x, y = p
        if inicial:
            self.create_line(x + (R + 45) * math.cos(a), y + (R + 45) * math.sin(a),
                             x + R * math.cos(a), y + R * math.sin(a),
                             arrow=tk.LAST, width=2)
        self.create_oval(x - R, y - R, x + R, y + R, fill="white", width=2)
        if final:
            self.create_oval(x - R + 5, y - R + 5, x + R - 5, y + R - 5, width=2)
        self.create_text(x, y, text=nombre, font=("Arial", 10, "bold"))

    def _flecha(self, s, t, doble, R, texto):
        dx, dy = t[0] - s[0], t[1] - s[1]
        d = math.hypot(dx, dy) or 1
        desv = 50 if doble else 0
        c = ((s[0] + t[0]) / 2 - dy / d * desv, (s[1] + t[1]) / 2 + dx / d * desv)
        a1 = math.atan2(c[1] - s[1], c[0] - s[0])
        a2 = math.atan2(c[1] - t[1], c[0] - t[0])
        p1 = (s[0] + R * math.cos(a1), s[1] + R * math.sin(a1))
        p2 = (t[0] + R * math.cos(a2), t[1] + R * math.sin(a2))
        self.create_line(*p1, *c, *p2, smooth=True, arrow=tk.LAST, width=1.5)
        mx = 0.25 * p1[0] + 0.5 * c[0] + 0.25 * p2[0]
        my = 0.25 * p1[1] + 0.5 * c[1] + 0.25 * p2[1]
        self.create_text(mx - dy / d * 11, my + dx / d * 11, text=texto,
                         font=("Arial", 10, "bold"))

    def _lazo(self, p, a, R, texto):
        pts = []
        for da, rr in ((-0.45, R), (-0.3, R + 30), (0.3, R + 30), (0.45, R)):
            pts += [p[0] + rr * math.cos(a + da), p[1] + rr * math.sin(a + da)]
        self.create_line(*pts, smooth=True, arrow=tk.LAST, width=1.5)
        self.create_text(p[0] + (R + 42) * math.cos(a), p[1] + (R + 42) * math.sin(a),
                         text=texto, font=("Arial", 10, "bold"))


class Pasos(ttk.Frame):
    """Muestra una lista de pasos de uno en uno (Anterior / Siguiente)."""

    def __init__(self, master, alto=8):
        super().__init__(master)
        barra = ttk.Frame(self)
        barra.pack(fill="x")
        ttk.Button(barra, text="◀ Anterior", command=lambda: self.ir(-1)).pack(side="left")
        ttk.Button(barra, text="Siguiente ▶", command=lambda: self.ir(1)).pack(side="left", padx=4)
        ttk.Button(barra, text="Ver todos", command=self.ver_todos).pack(side="left")
        self.contador = ttk.Label(barra, text="Sin pasos")
        self.contador.pack(side="right")
        self.texto = tk.Text(self, height=alto, width=60, wrap="word",
                             font=("Courier New", 10), state="disabled")
        self.texto.pack(fill="both", expand=True, pady=(4, 0))
        self.pasos, self.i = [], 0

    def cargar(self, pasos):
        self.pasos, self.i = pasos, 0
        self.mostrar()

    def ir(self, delta):
        if self.pasos:
            self.i = min(max(self.i + delta, 0), len(self.pasos) - 1)
            self.mostrar()

    def mostrar(self):
        if not self.pasos:
            self._poner("")
            self.contador.config(text="Sin pasos")
            return
        self._poner(f"Paso {self.i + 1} de {len(self.pasos)}\n\n{self.pasos[self.i]}")
        self.contador.config(text=f"{self.i + 1} / {len(self.pasos)}")

    def ver_todos(self):
        self._poner("\n\n".join(f"Paso {k + 1}: {p}" for k, p in enumerate(self.pasos)))

    def _poner(self, texto):
        self.texto.config(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.config(state="disabled")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de autómatas: AFND → AFD → ER")
        self.geometry("1150x760")
        self.afnd = self.afd = self.er = None
        cuaderno = ttk.Notebook(self)
        cuaderno.pack(fill="both", expand=True)
        self._pestana_editor(cuaderno)
        self._pestana_afd(cuaderno)
        self._pestana_er(cuaderno)
        self._pestana_verificador(cuaderno)
        self.cargar_ejemplo("Caso 1")

    # ------------------------------------------------------ pestaña 1
    def _pestana_editor(self, cuaderno):
        f = ttk.Frame(cuaderno, padding=8)
        cuaderno.add(f, text="1. Autómata (AFND)")
        izq = ttk.Frame(f)
        izq.pack(side="left", fill="y")
        self.campos = {}
        for clave, rotulo in (("estados", "Estados (separados por coma)"),
                              ("alfabeto", "Alfabeto (un carácter por símbolo)"),
                              ("inicial", "Estado inicial"),
                              ("finales", "Estados finales")):
            ttk.Label(izq, text=rotulo).pack(anchor="w")
            entrada = ttk.Entry(izq, width=36)
            entrada.pack(anchor="w", pady=(0, 6))
            self.campos[clave] = entrada
        ttk.Label(izq, text="Transiciones, una por línea: origen,símbolo,destino\n"
                            "(use ε para transiciones vacías)").pack(anchor="w")
        self.t_trans = tk.Text(izq, width=30, height=10)
        self.t_trans.pack(anchor="w", pady=(0, 8))
        ttk.Button(izq, text="Dibujar AFND", command=self.dibujar_afnd).pack(fill="x")
        for nombre in A.EJEMPLOS:
            ttk.Button(izq, text=f"Cargar: {nombre}",
                       command=lambda n=nombre: self.cargar_ejemplo(n)).pack(fill="x", pady=1)
        ttk.Button(izq, text="Guardar JSON", command=self.guardar).pack(fill="x", pady=(8, 1))
        ttk.Button(izq, text="Abrir JSON", command=self.abrir).pack(fill="x")
        self.lienzo_editor = Lienzo(f, width=620, height=460)
        self.lienzo_editor.pack(side="left", fill="both", expand=True, padx=8)

    def poner_en_editor(self, af):
        for clave in ("estados", "alfabeto", "finales"):
            self.campos[clave].delete(0, "end")
            self.campos[clave].insert(0, ",".join(af[clave]))
        self.campos["inicial"].delete(0, "end")
        self.campos["inicial"].insert(0, af["inicial"])
        self.t_trans.delete("1.0", "end")
        self.t_trans.insert("1.0", "\n".join(",".join(t) for t in af["transiciones"]))

    def leer_afnd(self):
        try:
            af = A.automata_desde_texto(
                self.campos["estados"].get(), self.campos["alfabeto"].get(),
                self.campos["inicial"].get(), self.campos["finales"].get(),
                self.t_trans.get("1.0", "end"))
        except ValueError as error:
            messagebox.showerror("Autómata inválido", str(error))
            return None
        self.afnd = af
        return af

    def cargar_ejemplo(self, nombre):
        self.poner_en_editor(A.EJEMPLOS[nombre])
        self.dibujar_afnd()

    def dibujar_afnd(self):
        af = self.leer_afnd()
        if af:
            self.afd = self.er = None
            self.lienzo_editor.dibujar(af, "AFND")

    def guardar(self):
        af = self.leer_afnd()
        ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json")])
        if af and ruta:
            A.guardar_json(af, ruta)

    def abrir(self):
        ruta = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not ruta:
            return
        try:
            self.poner_en_editor(A.cargar_json(ruta))
        except (ValueError, KeyError, OSError) as error:
            messagebox.showerror("No se pudo abrir", str(error))
            return
        self.dibujar_afnd()

    # ------------------------------------------------------ pestaña 2
    def _pestana_afd(self, cuaderno):
        f = ttk.Frame(cuaderno, padding=8)
        cuaderno.add(f, text="2. AFND → AFD")
        ttk.Button(f, text="Convertir AFND → AFD", command=self.convertir).pack(anchor="w")
        arriba = ttk.Frame(f)
        arriba.pack(fill="both", expand=True, pady=6)
        self.lienzo_afnd = Lienzo(arriba, width=420, height=300)
        self.lienzo_afnd.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self.lienzo_afd = Lienzo(arriba, width=420, height=300)
        self.lienzo_afd.pack(side="left", fill="both", expand=True, padx=(4, 0))
        abajo = ttk.Frame(f)
        abajo.pack(fill="x")
        self.tabla = ttk.Treeview(abajo, show="headings", height=8)
        self.tabla.pack(side="left", fill="y", padx=(0, 8))
        self.pasos_afd = Pasos(abajo, alto=8)
        self.pasos_afd.pack(side="left", fill="both", expand=True)

    def convertir(self):
        af = self.leer_afnd()
        if not af:
            return False
        tabla, afd, pasos = A.afnd_a_afd(af)
        self.afd, self.er = afd, None
        columnas = ["Conjunto"] + af["alfabeto"]
        self.tabla.delete(*self.tabla.get_children())
        self.tabla["columns"] = columnas
        for c in columnas:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=130 if c == "Conjunto" else 90, anchor="center")
        for fila in tabla:
            marca = ("→" if fila["conjunto"] == afd["inicial"] else "") + ("*" if fila["final"] else "")
            self.tabla.insert("", "end", values=[f"{marca} {fila['conjunto']}".strip()]
                              + [fila["destinos"][s] for s in af["alfabeto"]])
        self.lienzo_afnd.dibujar(af, "AFND de partida")
        self.lienzo_afd.dibujar(afd, "AFD resultante")
        self.pasos_afd.cargar(pasos)
        return True

    # ------------------------------------------------------ pestaña 3
    def _pestana_er(self, cuaderno):
        f = ttk.Frame(cuaderno, padding=8)
        cuaderno.add(f, text="3. Autómata → ER")
        self.origen = tk.StringVar(value="afd")
        ttk.Radiobutton(f, text="Usar el AFD del Módulo 1 (flujo AFND → AFD → ER)",
                        variable=self.origen, value="afd").pack(anchor="w")
        ttk.Radiobutton(f, text="Usar directamente el autómata del editor",
                        variable=self.origen, value="editor").pack(anchor="w")
        ttk.Button(f, text="Calcular expresión regular",
                   command=self.calcular_er).pack(anchor="w", pady=6)
        self.etiqueta_er = ttk.Label(f, text="ER: —", font=("Arial", 15, "bold"))
        self.etiqueta_er.pack(anchor="w", pady=(0, 6))
        self.pasos_er = Pasos(f, alto=22)
        self.pasos_er.pack(fill="both", expand=True)

    def calcular_er(self, reconvertir=True):
        if self.origen.get() == "afd":
            if reconvertir and not self.convertir():
                return False
            af = self.afd
        else:
            af = self.leer_afnd()
        if not af:
            return False
        self.er, pasos = A.af_a_er(af)
        self.etiqueta_er.config(text="ER: " + A.a_texto(self.er))
        self.pasos_er.cargar(pasos)
        return True

    # ------------------------------------------------------ pestaña 4
    def _pestana_verificador(self, cuaderno):
        f = ttk.Frame(cuaderno, padding=8)
        cuaderno.add(f, text="4. Verificador")
        barra = ttk.Frame(f)
        barra.pack(anchor="w")
        ttk.Label(barra, text="Longitud máxima n (mínimo 6):").pack(side="left")
        self.n = tk.StringVar(value="6")
        ttk.Spinbox(barra, from_=6, to=12, width=4, textvariable=self.n).pack(side="left", padx=6)
        ttk.Button(barra, text="Verificar AFND = AFD = ER",
                   command=self.verificar).pack(side="left")
        self.resultado = tk.Text(f, height=28, font=("Courier New", 10), state="disabled")
        self.resultado.pack(fill="both", expand=True, pady=8)

    def verificar(self):
        try:
            n = int(self.n.get())
            if n < 6:
                raise ValueError("n debe ser al menos 6.")
        except ValueError as error:
            messagebox.showerror("Valor inválido", str(error) if "6" in str(error) else "n debe ser un entero.")
            return
        if not self.convertir() or not self.calcular_er(reconvertir=False):
            return
        try:
            total, difs = A.verificar_equivalencia(self.afnd, self.afd, self.er, n)
        except ValueError as error:
            messagebox.showerror("Verificador", str(error))
            return
        lineas = [f"Cadenas del alfabeto de longitud 0 a {n}: {total}",
                  f"ER evaluada: {A.a_texto(self.er)}", ""]
        if not difs:
            lineas.append("✔ El AFND, el AFD y la ER aceptan exactamente las mismas cadenas.")
        else:
            lineas.append(f"✘ Hay {len(difs)} cadenas en las que difieren:")
            lineas.append(f"{'cadena':<14}{'AFND':<7}{'AFD':<7}ER")
            si = lambda b: "sí" if b else "no"
            for cadena, a, b, c in difs[:200]:
                lineas.append(f"{cadena or 'λ':<14}{si(a):<7}{si(b):<7}{si(c)}")
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", "end")
        self.resultado.insert("1.0", "\n".join(lineas))
        self.resultado.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()
