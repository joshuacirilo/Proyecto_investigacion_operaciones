import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import List
import numpy as np
import re

# Clase Simplex (para maximización)
class SimplexMaximizacion:
    def __init__(self):
        self.max_iterations = 1000
    
    def parse_ecuacion_z(self, ecuacion: str) -> List[float]:
        ecuacion = ecuacion.strip().replace(" ", "").lower()
        if not ecuacion.startswith('z='):
            raise ValueError("La ecuación debe comenzar con 'z='")
        ecuacion = ecuacion[2:]
        pattern = r'([+-]?\d*\.?\d*)?x\^?(\d+)'
        matches = re.findall(pattern, ecuacion)
        max_index = max(int(idx) for _, idx in matches)
        coeficientes = [0.0] * max_index
        for coef_str, idx_str in matches:
            idx = int(idx_str) - 1
            if not coef_str or coef_str == '+':
                coeficientes[idx] = 1.0
            elif coef_str == '-':
                coeficientes[idx] = -1.0
            else:
                coeficientes[idx] = float(coef_str)
        return coeficientes
    
    def parse_restriccion(self, restr: str, n_vars: int):
        restr = restr.strip().replace(" ", "")
        operator_match = re.search(r'([<=>]=?)(-?\d*\.?\d*)$', restr)
        if not operator_match:
            raise ValueError(f"Formato de restricción inválido: {restr}")
        operator, rhs_str = operator_match.groups()
        rhs = float(rhs_str)
        left_side = restr[:operator_match.start()]
        pattern = r'([+-]?\d*\.?\d*)?x\^?(\d+)'
        matches = re.findall(pattern, left_side)
        coeficientes = [0.0] * n_vars
        for coef_str, idx_str in matches:
            idx = int(idx_str) - 1
            if not coef_str or coef_str == '+':
                coeficientes[idx] = 1.0
            elif coef_str == '-':
                coeficientes[idx] = -1.0
            else:
                coeficientes[idx] = float(coef_str)
        return coeficientes, rhs, operator
    
    def build_tableau(self, A, b, c, operators):
        m, n = len(A), len(c)
        slack_vars = sum(1 for op in operators if op in ['<=', '<', '='])
        tableau = np.zeros((m + 1, n + slack_vars + 1))
        slack_idx = n
        for i in range(m):
            tableau[i, :n] = A[i]
            if operators[i] in ['<=', '<', '=']:
                tableau[i, slack_idx] = 1.0
                slack_idx += 1
            tableau[i, -1] = b[i]
        tableau[-1, :n] = [-ci for ci in c]
        return tableau
    
    def _find_pivot_column(self, z_row):
        min_val = 0
        pivot_col = None
        for j in range(len(z_row)-1):
            if z_row[j] < min_val - 1e-9:
                min_val = z_row[j]
                pivot_col = j
        return pivot_col
    
    def _find_pivot_row(self, tableau, pivot_col):
        m = len(tableau)-1
        min_ratio = float('inf')
        pivot_row = None
        for i in range(m):
            if tableau[i,pivot_col] > 1e-9:
                ratio = tableau[i,-1]/tableau[i,pivot_col]
                if ratio >=0 and ratio < min_ratio-1e-9:
                    min_ratio = ratio
                    pivot_row = i
        return pivot_row
    
    def _pivot(self, tableau, pivot_row, pivot_col):
        pivot_element = tableau[pivot_row,pivot_col]
        tableau[pivot_row] /= pivot_element
        for i in range(len(tableau)):
            if i!=pivot_row:
                factor = tableau[i,pivot_col]
                tableau[i] -= factor*tableau[pivot_row]
    
    def _get_basic_variables(self, tableau, n_vars):
        """Obtiene las variables básicas del tableau actual"""
        m, n_total = tableau.shape
        basic_vars = []
        
        for i in range(m-1):  # Excluir la fila Z
            # Buscar la columna que tiene 1 en esta fila y 0 en las demás
            for j in range(n_total-1):  # Excluir la columna b
                if abs(tableau[i, j] - 1.0) < 1e-9:
                    # Verificar que en las otras filas sea 0
                    is_basic = True
                    for k in range(m-1):
                        if k != i and abs(tableau[k, j]) > 1e-9:
                            is_basic = False
                            break
                    if is_basic:
                        if j < n_vars:
                            basic_vars.append(f"x{j+1}")
                        else:
                            basic_vars.append(f"s{j+1 - n_vars}")
                        break
            else:
                # Si no se encontró variable básica, poner placeholder
                basic_vars.append(f"F{i+1}")
        
        return basic_vars
    
    def _extract_solution(self, tableau, n_original):
        m,n = tableau.shape
        solution = [0.0]*n
        for j in range(n):
            col = tableau[:-1,j]
            if np.sum(np.abs(col))>1e-9:
                ones = np.where(np.abs(col-1)<1e-9)[0]
                zeros = np.where(np.abs(col)<1e-9)[0]
                if len(ones)==1 and len(zeros)==len(col)-1:
                    solution[j] = tableau[ones[0],-1]
        optimal_value = tableau[-1,-1]
        return solution, optimal_value
    
    def solve(self, A,b,c,operators, show_iterations=True):
        tableau = self.build_tableau(A,b,c,operators)
        n_original = len(c)
        iterations = 0
        history = []
        while iterations < self.max_iterations:
            z_row = tableau[-1,:-1]  # Excluir la columna b para buscar pivote
            pivot_col = self._find_pivot_column(z_row)
            if pivot_col is None:
                break
            pivot_row = self._find_pivot_row(tableau,pivot_col)
            if pivot_row is None:
                messagebox.showerror("Error","Problema ilimitado")
                return None, None, history
            
            # Obtener variables básicas antes del pivoteo
            basic_vars = self._get_basic_variables(tableau, n_original)
            if show_iterations:
                history.append((iterations+1, tableau.copy(), pivot_row, pivot_col, basic_vars))
            
            self._pivot(tableau,pivot_row,pivot_col)
            iterations +=1
        
        # Agregar el tableau final a la historia
        basic_vars_final = self._get_basic_variables(tableau, n_original)
        history.append((iterations+1, tableau.copy(), None, None, basic_vars_final))
        
        solution, opt_val = self._extract_solution(tableau,n_original)
        return solution, opt_val, history

# ---------------- GUI ----------------
class SimplexGUI:
    def __init__(self, master):
        self.master = master
        master.title("Método Simplex - Maximización")
        master.geometry("700x700")

        self.label_z = tk.Label(master, text="Función objetivo Z:")
        self.label_z.pack()
        self.entry_z = tk.Entry(master, width=50)
        self.entry_z.pack()
        
        self.label_m = tk.Label(master, text="Número de restricciones:")
        self.label_m.pack()
        self.entry_m = tk.Entry(master, width=10)
        self.entry_m.pack()
        
        self.btn_generar = tk.Button(master, text="Generar campos de restricciones", command=self.generar_restricciones)
        self.btn_generar.pack()
        
        self.restricciones_frame = tk.Frame(master)
        self.restricciones_frame.pack()
        
        self.btn_solve = tk.Button(master, text="Resolver Simplex", command=self.resolver)
        self.btn_solve.pack()
        
        self.result_text = scrolledtext.ScrolledText(master, width=85, height=25)
        self.result_text.pack()
        
        self.entries_restricciones = []
    
    def generar_restricciones(self):
        for widget in self.restricciones_frame.winfo_children():
            widget.destroy()
        self.entries_restricciones = []
        try:
            m = int(self.entry_m.get())
            for i in range(m):
                label = tk.Label(self.restricciones_frame, text=f"Restricción {i+1}:")
                label.grid(row=i, column=0)
                entry = tk.Entry(self.restricciones_frame, width=50)
                entry.grid(row=i, column=1)
                self.entries_restricciones.append(entry)
        except:
            messagebox.showerror("Error","Número de restricciones inválido")
    
    def _print_tableau_gui(self, tableau, n_vars, iteration, pivot_row, pivot_col, basic_vars):
        m, n = tableau.shape
        n_slack = n - n_vars - 1  # -1 para la columna b
        
        self.result_text.insert(tk.END, f"\n--- Iteración {iteration} ---\n")
        
        # Encabezados
        headers = ["VB"] + [f"x{i+1}" for i in range(n_vars)] + [f"s{i+1}" for i in range(n_slack)] + ["b"]
        self.result_text.insert(tk.END, "   " + " ".join(f"{h:>8}" for h in headers) + "\n")
        self.result_text.insert(tk.END, "-" * (len(headers) * 9 + 3) + "\n")
        
        # Filas de restricciones
        for i in range(m-1):
            # Variable básica
            vb = basic_vars[i] if i < len(basic_vars) else f"F{i+1}"
            row_str = f"{vb:>3}"
            
            # Valores de la fila
            for j in range(n):
                row_str += f"{tableau[i,j]:>8.2f}"
            
            # Marcar fila pivote
            if i == pivot_row:
                row_str += "  ← fila pivote"
            self.result_text.insert(tk.END, row_str + "\n")
        
        # Fila Z
        z_row_str = "  Z"
        for j in range(n):
            z_row_str += f"{tableau[-1,j]:>8.2f}"
        self.result_text.insert(tk.END, z_row_str + "\n")
        
        # Información del pivote
        if pivot_col is not None:
            if pivot_col < n_vars:
                var_name = f"x{pivot_col+1}"
            else:
                var_name = f"s{pivot_col+1 - n_vars}"
            self.result_text.insert(tk.END, f"Variable entrante: {var_name}\n")
        
        self.result_text.insert(tk.END, "-" * (len(headers) * 9 + 3) + "\n")
    
    def resolver(self):
        solver = SimplexMaximizacion()
        try:
            z = self.entry_z.get()
            c = solver.parse_ecuacion_z(z)
            n_vars = len(c)
            A, b, operators = [], [], []
            for entry in self.entries_restricciones:
                restr = entry.get()
                a_i, b_i, op = solver.parse_restriccion(restr, n_vars)
                A.append(a_i)
                b.append(b_i)
                operators.append(op)
            
            solution, opt_val, history = solver.solve(A,b,c,operators, show_iterations=True)
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "=== MÉTODO SIMPLEX - MAXIMIZACIÓN ===\n")
            self.result_text.insert(tk.END, f"Función objetivo: Z = {z}\n")
            self.result_text.insert(tk.END, f"Variables: {n_vars} de decisión + {len(A)} de holgura\n\n")
            
            # Mostrar todas las iteraciones
            for iteration, tableau, pivot_row, pivot_col, basic_vars in history:
                self._print_tableau_gui(tableau, n_vars, iteration, pivot_row, pivot_col, basic_vars)
            
            # Mostrar solución final
            self.result_text.insert(tk.END, f"\n🎯 SOLUCIÓN ÓPTIMA ENCONTRADA\n")
            self.result_text.insert(tk.END, f"Valor óptimo Z = {opt_val:.2f}\n\n")
            
            self.result_text.insert(tk.END, "VARIABLES DE DECISIÓN:\n")
            for i in range(n_vars):
                self.result_text.insert(tk.END, f"x{i+1} = {solution[i]:.4f}\n")
            
            self.result_text.insert(tk.END, "\nVARIABLES DE HOLGURA:\n")
            n_slack = len(solution) - n_vars - 1  # -1 porque solution incluye la columna b
            for i in range(n_slack):
                self.result_text.insert(tk.END, f"s{i+1} = {solution[n_vars + i]:.4f}\n")
            
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    gui = SimplexGUI(root)
    root.mainloop()