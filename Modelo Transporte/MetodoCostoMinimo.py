import customtkinter as ctk
from tkinter import messagebox
import numpy as np

ctk.set_appearance_mode("dark")  # "light" o "dark"
ctk.set_default_color_theme("blue")  # temas: "blue", "green", "dark-blue"

class MetodoCostoMinimoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🚚 Método de Costo Mínimo - Modelo de Transporte")
        self.geometry("1000x750")
        self.minsize(900, 650)

        # Variables principales
        self.num_origenes = 0
        self.num_destinos = 0
        self.ofertas = []
        self.demandas = []
        self.costos = []

        self._build_ui()

    def _build_ui(self):
        title = ctk.CTkLabel(self, text="Método de Costo Mínimo", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(20, 10))

        config_frame = ctk.CTkFrame(self, corner_radius=15)
        config_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(config_frame, text="Número de Orígenes:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_origenes = ctk.CTkEntry(config_frame, width=100)
        self.entry_origenes.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(config_frame, text="Número de Destinos:").grid(row=0, column=2, padx=10, pady=10)
        self.entry_destinos = ctk.CTkEntry(config_frame, width=100)
        self.entry_destinos.grid(row=0, column=3, padx=10, pady=10)

        btn_configurar = ctk.CTkButton(config_frame, text="⚙️ Configurar Matriz", command=self.configurar_matriz)
        btn_configurar.grid(row=0, column=4, padx=20, pady=10)

        # Contenedor de matriz
        self.matriz_frame = ctk.CTkScrollableFrame(self, label_text="Matriz de Costos", corner_radius=15)
        self.matriz_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Botones acción
        acciones = ctk.CTkFrame(self, fg_color="transparent")
        acciones.pack(pady=10)

        self.btn_calcular = ctk.CTkButton(acciones, text="📊 Calcular Solución", command=self.calcular_solucion)
        self.btn_calcular.pack(side="left", padx=10)

        self.btn_limpiar = ctk.CTkButton(acciones, text="🧹 Limpiar", command=self.limpiar)
        self.btn_limpiar.pack(side="left", padx=10)

        # Resultados
        self.resultados_frame = ctk.CTkScrollableFrame(self, label_text="Resultados", corner_radius=15)
        self.resultados_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def configurar_matriz(self):
        for widget in self.matriz_frame.winfo_children():
            widget.destroy()

        try:
            self.num_origenes = int(self.entry_origenes.get())
            self.num_destinos = int(self.entry_destinos.get())
        except ValueError:
            messagebox.showerror("Error", "Debe ingresar números válidos.")
            return

        if self.num_origenes <= 0 or self.num_destinos <= 0:
            messagebox.showerror("Error", "Los valores deben ser mayores a 0.")
            return

        # Encabezados
        ctk.CTkLabel(self.matriz_frame, text="Origen/Destino", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=8, pady=8)
        for j in range(self.num_destinos):
            ctk.CTkLabel(self.matriz_frame, text=f"D{j+1}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=j+1, padx=8, pady=8)
        ctk.CTkLabel(self.matriz_frame, text="Oferta", font=ctk.CTkFont(weight="bold")).grid(row=0, column=self.num_destinos+1, padx=8, pady=8)

        self.entradas_costos = []
        self.entradas_ofertas = []

        # Entradas matriz
        for i in range(self.num_origenes):
            ctk.CTkLabel(self.matriz_frame, text=f"O{i+1}", font=ctk.CTkFont(weight="bold")).grid(row=i+1, column=0, padx=8, pady=5)
            fila = []
            for j in range(self.num_destinos):
                entry = ctk.CTkEntry(self.matriz_frame, width=70, justify="center")
                entry.grid(row=i+1, column=j+1, padx=5, pady=5)
                fila.append(entry)
            self.entradas_costos.append(fila)

            e_oferta = ctk.CTkEntry(self.matriz_frame, width=70, justify="center")
            e_oferta.grid(row=i+1, column=self.num_destinos+1, padx=5, pady=5)
            e_oferta.bind("<KeyRelease>", lambda e: self.actualizar_totales())
            self.entradas_ofertas.append(e_oferta)

        # Fila demanda
        ctk.CTkLabel(self.matriz_frame, text="Demanda", font=ctk.CTkFont(weight="bold")).grid(row=self.num_origenes+1, column=0, padx=8, pady=5)
        self.entradas_demandas = []
        for j in range(self.num_destinos):
            e_demanda = ctk.CTkEntry(self.matriz_frame, width=70, justify="center")
            e_demanda.grid(row=self.num_origenes+1, column=j+1, padx=5, pady=5)
            e_demanda.bind("<KeyRelease>", lambda e: self.actualizar_totales())
            self.entradas_demandas.append(e_demanda)

        # Cuadro verde
        self.total_label = ctk.CTkLabel(
            self.matriz_frame,
            text="0 / 0",
            text_color="lightgreen",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=80,
            height=30,
            corner_radius=8,
            fg_color="gray25"
        )
        self.total_label.grid(row=self.num_origenes+1, column=self.num_destinos+1, padx=5, pady=5)

    def actualizar_totales(self):
        try:
            total_oferta = sum(float(e.get()) for e in self.entradas_ofertas if e.get())
            total_demanda = sum(float(e.get()) for e in self.entradas_demandas if e.get())

            balanceado = abs(total_oferta - total_demanda) < 1e-6
            color = "lightgreen" if balanceado else "red"
            self.total_label.configure(text=f"{total_oferta:.0f} / {total_demanda:.0f}", text_color=color)
        except ValueError:
            self.total_label.configure(text="Error", text_color="red")

    def obtener_datos(self):
        try:
            self.costos = [[float(e.get()) for e in fila] for fila in self.entradas_costos]
            self.ofertas = [float(e.get()) for e in self.entradas_ofertas]
            self.demandas = [float(e.get()) for e in self.entradas_demandas]
            return True
        except ValueError:
            messagebox.showerror("Error", "Por favor complete todos los valores numéricos correctamente.")
            return False

    def calcular_solucion(self):
        if not self.obtener_datos():
            return

        total_oferta = sum(self.ofertas)
        total_demanda = sum(self.demandas)

        if abs(total_oferta - total_demanda) > 1e-6:
            messagebox.showwarning("Advertencia", "El problema no está balanceado.")

        asignaciones = self.metodo_costo_minimo()
        self.mostrar_resultados(asignaciones)

    def metodo_costo_minimo(self):
        asignaciones = np.zeros((self.num_origenes, self.num_destinos))
        ofertas_restantes = self.ofertas.copy()
        demandas_restantes = self.demandas.copy()

        celdas = [(i, j, self.costos[i][j]) for i in range(self.num_origenes) for j in range(self.num_destinos)]
        celdas.sort(key=lambda x: x[2])

        for i, j, _ in celdas:
            if ofertas_restantes[i] > 0 and demandas_restantes[j] > 0:
                cantidad = min(ofertas_restantes[i], demandas_restantes[j])
                asignaciones[i][j] = cantidad
                ofertas_restantes[i] -= cantidad
                demandas_restantes[j] -= cantidad
        return asignaciones

    def mostrar_resultados(self, asignaciones):
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()

        costo_total = 0
        for i in range(self.num_origenes):
            for j in range(self.num_destinos):
                if asignaciones[i][j] > 0:
                    costo_total += asignaciones[i][j] * self.costos[i][j]

        titulo = ctk.CTkLabel(self.resultados_frame, text=f"Costo Total: {costo_total:.2f}", font=ctk.CTkFont(size=18, weight="bold"))
        titulo.pack(pady=10)

        for i in range(self.num_origenes):
            fila_txt = f"O{i+1}:  "
            for j in range(self.num_destinos):
                if asignaciones[i][j] > 0:
                    fila_txt += f"D{j+1} → {asignaciones[i][j]:.0f}  |  "
            ctk.CTkLabel(self.resultados_frame, text=fila_txt).pack(pady=3)

    def limpiar(self):
        self.entry_origenes.delete(0, "end")
        self.entry_destinos.delete(0, "end")
        for f in [self.matriz_frame, self.resultados_frame]:
            for w in f.winfo_children():
                w.destroy()

if __name__ == "__main__":
    app = MetodoCostoMinimoApp()
    app.mainloop()
