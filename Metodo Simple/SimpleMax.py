# simplex_tableau.py
# Implementación simple del método Simplex (tableau).
# Soporta problemas con restricciones Ax <= b, x >= 0.
# NOTA: No implementa fase I/II ni variables artificiales.

from typing import Tuple, List
import copy

def build_tableau(A: List[List[float]], b: List[float], c: List[float]) -> List[List[float]]:
    """
    Construye el tableau inicial para un problema de maximización:
    Max z = c^T x  s.t.  A x <= b, x >= 0
    Tableau tiene la forma:
    [ A | I | b ]
    [ -c^T | 0..0 | 0 ]  (fila Z)
    """
    m = len(A)      # restricciones
    n = len(A[0])   # variables originales

    # tabla: m filas de restricciones + 1 fila de Z
    # columnas: n (x) + m (holgura) + 1 (b)
    tableau = [[0.0] * (n + m + 1) for _ in range(m + 1)]

    # llenar A y columnas de holgura (I)
    for i in range(m):
        for j in range(n):
            tableau[i][j] = float(A[i][j])
        tableau[i][n + i] = 1.0  # variable de holgura
        tableau[i][-1] = float(b[i])

    # fila Z (costes): -c en la parte de variables, holguras 0, b=0
    for j in range(n):
        tableau[-1][j] = -float(c[j])  # para maximizar
    # tableau[-1][-1] ya es 0
    return tableau

def pivot(tableau: List[List[float]], row: int, col: int):
    """Realiza pivot (Gauss-Jordan) en tableau sobre posición (row, col)."""
    m = len(tableau)
    n = len(tableau[0])
    pivot_val = tableau[row][col]
    if abs(pivot_val) < 1e-12:
        raise ValueError("Pivot ≈ 0, no se puede pivotear.")

    # dividir fila pivot por pivot_val
    tableau[row] = [v / pivot_val for v in tableau[row]]

    # anular columna en otras filas
    for i in range(m):
        if i == row:
            continue
        factor = tableau[i][col]
        if abs(factor) > 0:
            tableau[i] = [ tableau[i][j] - factor * tableau[row][j] for j in range(n) ]

def find_entering_variable(tableau: List[List[float]], maximize: bool = True) -> int:
    """
    Determina columna pivote (variable de entrada) según condición de optimalidad.
    Para maximizar: elegir la columna con coeficiente más negativo en fila Z.
    Para minimizar: elegir la columna con coeficiente más positivo en fila Z.
    Retorna índice de columna, o -1 si ya óptimo.
    """
    z_row = tableau[-1]
    # excluir la columna de b (última)
    coeffs = z_row[:-1]
    if maximize:
        # buscar coef < 0 (más negativo)
        min_val = min(coeffs)
        if min_val >= -1e-12:
            return -1
        return coeffs.index(min_val)
    else:
        # minimización: buscar coef > 0 (más positivo)
        max_val = max(coeffs)
        if max_val <= 1e-12:
            return -1
        return coeffs.index(max_val)

def find_leaving_row(tableau: List[List[float]], entering_col: int) -> int:
    """
    Regla del mínimo cociente (condición de factibilidad).
    Retorna la fila pivote (índice), o -1 si ilimitado.
    """
    m = len(tableau) - 1  # sin contar fila Z
    ratios = []
    for i in range(m):
        a_ij = tableau[i][entering_col]
        b_i = tableau[i][-1]
        if a_ij > 1e-12:
            ratios.append((b_i / a_ij, i))
    if not ratios:
        return -1  # ilimitado
    # tomar el mínimo ratio
    return min(ratios, key=lambda x: (x[0], x[1]))[1]

def simplex(A: List[List[float]], b: List[float], c: List[float], maximize: bool = True, max_iters: int = 1000) -> Tuple[float, List[float], List[List[float]]]:
    """
    Ejecuta Simplex sobre Ax <= b, x >= 0.
    Si maximize==False, hace minimización (usa criterio de entrada invertido).
    Retorna (valor_optimo, vector_x, tableau_final).
    NOTA: asume problema en forma que no requiere variables artificiales.
    """
    tableau = build_tableau(A, b, c if maximize else [-ci for ci in c])
    m = len(A)
    n = len(A[0])

    # base inicial: las variables de holgura (índices n..n+m-1)
    basis = [n + i for i in range(m)]

    it = 0
    while it < max_iters:
        it += 1
        col = find_entering_variable(tableau, maximize=maximize)
        if col == -1:
            # óptimo
            break
        row = find_leaving_row(tableau, col)
        if row == -1:
            raise ValueError("Problema ilimitado (no existe fila de salida).")
        # pivot y actualizar base
        pivot(tableau, row, col)
        basis[row] = col

    # leer solución
    x = [0.0] * n
    for i, bv in enumerate(basis):
        if bv < n:
            x[bv] = tableau[i][-1]
    # valor óptimo Z: fila Z, columna b
    z = tableau[-1][-1]
    # si hicimos minimización invirtiendo c, ajustar signo
    if not maximize:
        z = -z
    return z, x, tableau

# ---------- Ejemplo de uso ----------
if __name__ == "__main__":
    # Max z = 3x1 + 5x2
    # s.a.
    #  1x1 + 0x2 <= 4
    #  0x1 + 2x2 <= 12
    #  3x1 + 2x2 <= 18
    A = [
        [1, 0],
        [0, 2],
        [3, 2],
    ]
    b = [4, 12, 18]
    c = [3, 5]

    z, x, tab = simplex(A, b, c, maximize=True)
    print("Z óptimo:", z)
    print("x:", x)
