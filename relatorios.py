import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mysql.connector
from database import conectar

# Placeholder para o canvas do gráfico, para poder limpá-lo
canvas_grafico = None

def criar_frame_tela(master, app):
    global canvas_grafico
    frame_relatorios = ctk.CTkFrame(master)

    # --- Funções para gerar e mostrar os gráficos ---
    def mostrar_grafico_motoristas():
        limpar_grafico_anterior()
        try:
            conn = conectar()
            if not conn:
                messagebox.showerror("Erro", "Falha ao conectar ao banco (Motoristas)", parent=frame_relatorios)
                return
            cursor = conn.cursor()
            query = """
                SELECT m.nome, COUNT(p.id) as total_pedidos
                FROM motorista m
                LEFT JOIN pedido p ON m.id = p.motorista_id
                GROUP BY m.id, m.nome
                ORDER BY total_pedidos DESC
            """
            cursor.execute(query)
            dados = cursor.fetchall()
            conn.close()

            if not dados:
                messagebox.showinfo("Info", "Não há dados de pedidos para gerar o gráfico de motoristas.", parent=frame_relatorios)
                return

            nomes = [item[0] for item in dados]
            contagens = [item[1] for item in dados]

            # Criar gráfico de barras
            fig, ax = plt.subplots(figsize=(7, 4))
            bars = ax.bar(nomes, contagens, color=plt.cm.viridis(0.6))
            ax.set_ylabel("Número de Entregas")
            ax.set_title("Comparativo de Entregas por Motorista")
            # CORREÇÃO: Remover barras invertidas desnecessárias
            ax.tick_params(axis='x', rotation=45, labelsize=8) 
            ax.grid(axis='y', linestyle='--') # Corrigido linestyle e aspas
            ax.bar_label(bars, padding=3)
            fig.tight_layout()

            # Incorporar gráfico no Tkinter
            global canvas_grafico
            canvas_grafico = FigureCanvasTkAgg(fig, master=frame_grafico_container)
            canvas_grafico.draw()
            canvas_grafico.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico de motoristas: {err}", parent=frame_relatorios)
        except Exception as e:
             messagebox.showerror("Erro", f"Erro inesperado: {e}", parent=frame_relatorios)

    def mostrar_grafico_veiculos():
        limpar_grafico_anterior()
        try:
            conn = conectar()
            if not conn:
                messagebox.showerror("Erro", "Falha ao conectar ao banco (Veículos)", parent=frame_relatorios)
                return
            cursor = conn.cursor()
            query = """
                SELECT v.placa, COUNT(p.id) as total_pedidos
                FROM veiculo v
                LEFT JOIN pedido p ON v.id = p.veiculo_id
                GROUP BY v.id, v.placa
                HAVING COUNT(p.id) > 0
                ORDER BY total_pedidos DESC
            """
            cursor.execute(query)
            dados = cursor.fetchall()
            conn.close()

            if not dados:
                messagebox.showinfo("Info", "Não há dados de pedidos para gerar o gráfico de veículos.", parent=frame_relatorios)
                return

            placas = [item[0] for item in dados]
            contagens = [item[1] for item in dados]

            # Criar gráfico de pizza
            fig, ax = plt.subplots(figsize=(7, 4))
            colors = plt.cm.plasma([i/float(len(placas)) for i in range(len(placas))])
            # CORREÇÃO: Remover barras invertidas desnecessárias e ajustar autopct
            wedges, texts, autotexts = ax.pie(contagens, labels=placas, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title("Distribuição de Entregas por Veículo")
            # plt.setp(autotexts, size=8, weight="bold", color="white") # Ajustar se necessário
            fig.tight_layout()

            # Incorporar gráfico no Tkinter
            global canvas_grafico
            canvas_grafico = FigureCanvasTkAgg(fig, master=frame_grafico_container)
            canvas_grafico.draw()
            canvas_grafico.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao gerar gráfico de veículos: {err}", parent=frame_relatorios)
        except Exception as e:
             messagebox.showerror("Erro", f"Erro inesperado: {e}", parent=frame_relatorios)

    def limpar_grafico_anterior():
        global canvas_grafico
        if canvas_grafico:
            canvas_grafico.get_tk_widget().destroy()
            canvas_grafico = None
        # CORREÇÃO: Remover barras invertidas desnecessárias
        plt.close('all') 

    # --- Interface Principal do Frame Relatórios ---
    ctk.CTkButton(frame_relatorios, text="< Voltar ao Menu", command=lambda: [limpar_grafico_anterior(), app.mostrar_frame("Menu")]).pack(pady=10, padx=10, anchor="nw")
    ctk.CTkLabel(frame_relatorios, text="Relatórios Comparativos", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))
    frame_botoes = ctk.CTkFrame(frame_relatorios)
    frame_botoes.pack(pady=10, padx=10, fill="x")
    ctk.CTkButton(frame_botoes, text="Comparativo por Motorista (Barras)", command=mostrar_grafico_motoristas).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(frame_botoes, text="Comparativo por Veículo (Pizza)", command=mostrar_grafico_veiculos).pack(side="left", padx=10, pady=10)
    frame_grafico_container = ctk.CTkFrame(frame_relatorios)
    frame_grafico_container.pack(pady=10, padx=10, fill="both", expand=True)

    return frame_relatorios

