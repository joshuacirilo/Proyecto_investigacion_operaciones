import numpy as np
import matplotlib.pyplot as plt

def metodo_grafico_min(c, A, b):
    """
    Método gráfico para programación lineal (minimización).
    
    Parámetros:
    c : list -> Coeficientes de la función objetivo [c1, c2]
    A : list -> Matriz de restricciones [[a11, a12], [a21, a22], ...]
    b : list -> Lado derecho de las restricciones [b1, b2, ...]
    """

    x = np.linspace(0, max(b) * 2, 400)
    y_bounds = []

    # Dibujar restricciones
    for i in range(len(A)):
        if A[i][1] != 0:  # Restricción con x2
            y = (b[i] - A[i][0] * x) / A[i][1]
        else:  # Restricción vertical
            y = np.full_like(x, b[i] / A[i][0])
        y_bounds.append(y)
        plt.plot(x, y, label=f"Restricción {i+1}")

    # Región factible
    y_region = np.minimum.reduce(y_bounds)
    plt.fill_between(x, 0, y_region, where=(y_region >= 0), alpha=0.3)

    # Puntos factibles (intersecciones de restricciones)
    puntos = []
    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            A_sub = np.array([A[i], A[j]])
            b_sub = np.array([b[i], b[j]])
            try:
                punto = np.linalg.solve(A_sub, b_sub)
                if all(np.dot(A, punto) <= b) and all(punto >= 0):
                    puntos.append(punto)
            except np.linalg.LinAlgError:
                pass

    # Evaluar la función objetivo en los puntos factibles
    if len(puntos) > 0:
        puntos = np.array(puntos)
        valores = [np.dot(c, p) for p in puntos]
        idx = np.argmin(valores) 
        mejor = puntos[idx]
        z_opt = valores[idx]

        plt.scatter(puntos[:, 0], puntos[:, 1], color="red")
        plt.scatter(mejor[0], mejor[1], color="blue", s=100, label="Óptimo (Mínimo)")

        # Mostrar resultados
        print("\nRESULTADOS ")
        print(f"x1 óptimo = {mejor[0]:.2f}")
        print(f"x2 óptimo = {mejor[1]:.2f}")
        print(f"Valor mínimo Z = {z_opt:.2f}")

        plt.text(mejor[0]+0.5, mejor[1]+0.5, 
                 f"({mejor[0]:.2f}, {mejor[1]:.2f})\nZ={z_opt:.2f}", 
                 fontsize=10, color="blue", bbox=dict(facecolor="white", alpha=0.6))
    else:
        print("\nNo se encontraron soluciones factibles.")

    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.legend()
    plt.grid()
    plt.title("Método Gráfico - Minimización")
    plt.show()


if __name__ == "__main__":
    print("=== MÉTODO GRÁFICO - MINIMIZACIÓN ===")

    # Función objetivo
    c1 = float(input("Coeficiente de x1 en la función objetivo: "))
    c2 = float(input("Coeficiente de x2 en la función objetivo: "))
    c = [c1, c2]

    # Restricciones
    n = int(input("\n¿Cuántas restricciones deseas ingresar? "))
    A = []
    b = []
    for i in range(n):
        print(f"\nRestricción {i+1}:")
        a1 = float(input("Coeficiente de x1: "))
        a2 = float(input("Coeficiente de x2: "))
        bi = float(input("Lado derecho (<=): "))
        A.append([a1, a2])
        b.append(bi)

    metodo_grafico_min(c, A, b)
