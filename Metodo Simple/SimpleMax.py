import re
from typing import List, Tuple

# -------------------- Funciones de utilidades --------------------

def parse_ecuacion_z(ecuacion: str) -> List[float]:
    """
    Convierte una ecuación tipo: z = 5x^1 + 2x^2 + 8x^3
    en una lista de coeficientes: [5, 2, 8]
    """
    ecuacion = ecuacion.replace(" ", "")
    coef_pattern = r"([+-]?\d*\.?\d*)x\^(\d+)"
    coeficientes = {}
    for coef, var in re.findall(coef_pattern, ecuacion):
        c = float(coef) if coef not in ["", "+", "-"] else (1.0 if coef != "-" else -1.0)
        i = int(var)
        coeficientes[i] = c
    max_var = max(coeficientes.keys())
    return [coeficientes.get(i, 0.0) for i in range(1, max_var + 1)]

def parse_restriccion(restr: str, n_vars: int) -> Tuple[List[float], float]:
    """
    Convierte una restricción tipo: 2x^1 + 2x^2 + 2x^3 <= 65
    en ([2, 2, 2], 65)
    """
    restr = restr.replace(" ", "")
    coef_pattern = r"([+-]?\d*\.?\d*)x\^(\d+)"
    coeficientes = {}
    for coef, var in re.findall(coef_pattern, restr):
        c = float(coef) if coef not in ["", "+", "-"] else (1.0 if coef != "-" else -1.0)
        i = int(var)
        coeficientes[i] = c
    b = float(re.findall(r"(<=|=|>=)(-?\d+\.?\d*)", restr)[0][1])
    return [coeficientes.get(i, 0.0) for i in range(1, n_vars + 1)], b

# -------------------- Funciones del método Simplex --------------------

def build_tableau(A: List[List[float]], b: List[float], c: List[float]) -> List[List[float]]:
    m = len(A)
    n = len(A[0])
    tableau = [[0.0] * (n + m + 1) for _ in range(m + 1)]

    for i in range(m):
        for j in range(n):
            tableau[i][j] = A[i][j]
        tableau[i][n + i] = 1.0
        tableau[i][-1] = b[i]

    for j in range(n):
        tableau[-1][j] = -c[j]
    return tableau

def mostrar_tabla(tableau: List[List[float]], encabezados: List[str], variables_basicas: List[str]):
    col_width = 10
    print("".join(h.center(col_width) for h in encabezados))
    for vb, fila in zip(variables_basicas + ["Z"], tableau):
        print(f"{vb.center(10)}" + "".join(f"{v:10.2f}" for v in fila))
    print("-" * (len(encabezados) * col_width))

def pivot(tableau: List[List[float]], row: int, col: int, encabezados: List[str]):
    pivot_val = tableau[row][col]
    print(f"\n🔸 Normalizando fila {row+1} dividiendo entre el pivote ({pivot_val:.4f})")
    tableau[row] = [v / pivot_val for v in tableau[row]]

    for i in range(len(tableau)):
        if i != row:
            factor = tableau[i][col]
            if abs(factor) > 1e-9:
                print(f"   F{i+1} = F{i+1} - ({factor:.4f}) * F{row+1}")
            tableau[i] = [tableau[i][j] - factor * tableau[row][j] for j in range(len(tableau[0]))]

def simplex(A: List[List[float]], b: List[float], c: List[float], encabezados: List[str]):
    tableau = build_tableau(A, b, c)
    m = len(A)
    n = len(A[0])
    basis = [n + i for i in range(m)]  # índices de las variables básicas (holguras)
    variables_basicas = [f"x{n+i+1}" for i in range(m)]

    iteracion = 0
    while True:
        iteracion += 1
        print(f"\n============================")
        print(f"🔹 Iteración {iteracion}")
        print("============================")
        mostrar_tabla(tableau, encabezados, variables_basicas)

        z_row = tableau[-1][:-1]
        if all(v >= -1e-9 for v in z_row):
            print("✅ Solución óptima encontrada.")
            break

        col = z_row.index(min(z_row))
        col_name = encabezados[col + 2]  # +2 por VB y Z
        ratios = []
        for i in range(m):
            if tableau[i][col] > 1e-9:
                ratios.append((tableau[i][-1] / tableau[i][col], i))
        if not ratios:
            raise ValueError("Problema ilimitado.")
        row = min(ratios)[1]

        pivot_val = tableau[row][col]
        row_name = variables_basicas[row]
        print(f"\n👉 Pivote = {pivot_val:.4f} (Fila {row+1}, Columna {col_name})")
        print(f"🔁 Variable básica que sale: {row_name}")
        print(f"🔁 Variable que entra: {col_name}\n")

        pivot(tableau, row, col, encabezados)
        variables_basicas[row] = col_name

    # leer solución
    x = [0.0] * n
    for i, vb in enumerate(variables_basicas):
        if vb.startswith("x"):
            idx = int(vb[1:]) - 1
            if idx < n:
                x[idx] = tableau[i][-1]
    z = tableau[-1][-1]

    print("\n📊 Resultado final:")
    mostrar_tabla(tableau, encabezados, variables_basicas)
    print(f"Valor óptimo Z = {z:.2f}")
    for i, val in enumerate(x, start=1):
        print(f"x{i} = {val:.2f}")

    return z, x, tableau

# -------------------- Ejecución interactiva --------------------

if __name__ == "__main__":
    print("=== MÉTODO SIMPLEX (MAXIMIZACIÓN) ===")
    ecuacion_z = input("Ingrese la ecuación de Z (ej. z=5x^1+2x^2+8x^3): ")
    c = parse_ecuacion_z(ecuacion_z)
    n_vars = len(c)
    m = int(input("¿Cuántas restricciones tiene?: "))

    A, b = [], []
    for i in range(m):
        restr = input(f"Ingrese restricción {i+1} (ej. 2x^1+2x^2+2x^3<=65): ")
        a_i, b_i = parse_restriccion(restr, n_vars)
        A.append(a_i)
        b.append(b_i)

    encabezados = ["VB", "Z"] + [f"x{i}" for i in range(1, n_vars + m + 1)] + ["b"]

    simplex(A, b, c, encabezados)
