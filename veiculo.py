import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
from database import conectar


def criar_frame_tela(master, app):
    frame_veiculo = ctk.CTkFrame(master)

    # --- Funções internas do frame ---
    def atualizar_lista():
        for widget in frame_lista.winfo_children():
            widget.destroy()

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para listar veículos.", parent=frame_veiculo)
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, placa, categoria, capacidade_kg FROM veiculo ORDER BY placa ASC")
            veiculos = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar veículos: {err}", parent=frame_veiculo)
            veiculos = []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        for id_, placa, categoria, capacidade in veiculos:
            item_frame = ctk.CTkFrame(frame_lista)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            texto = f"{placa} | Categoria: {categoria} | Capacidade: {capacidade:.2f} kg"
            ctk.CTkLabel(item_frame, text=texto, anchor="w").pack(side="left", fill="x", expand=True, padx=5)

            botoes_frame = ctk.CTkFrame(item_frame)
            botoes_frame.pack(side="right")

            # Passar 'app' como master para a janela de edição
            ctk.CTkButton(botoes_frame, text="Editar", width=70, command=lambda i=id_: editar_veiculo(i, app)).pack(side="left", padx=2)
            ctk.CTkButton(botoes_frame, text="Excluir", width=70, fg_color="red", command=lambda i=id_: excluir_veiculo(i)).pack(side="left", padx=2)

    def cadastrar_veiculo():
        placa = entry_placa.get().upper()
        categoria = entry_categoria.get()
        capacidade_str = entry_capacidade.get()

        if not placa or not categoria or not capacidade_str:
            messagebox.showwarning("Atenção", "Preencha todos os campos.", parent=frame_veiculo)
            return

        try:
            capacidade_valor = float(capacidade_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Capacidade deve ser um número válido.", parent=frame_veiculo)
            return

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para cadastrar.", parent=frame_veiculo)
            return

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO veiculo (placa, categoria, capacidade_kg) VALUES (%s, %s, %s)",
                           (placa, categoria, capacidade_valor))
            conn.commit()
            atualizar_lista()
            entry_placa.delete(0, "end")
            entry_categoria.delete(0, "end")
            entry_capacidade.delete(0, "end")
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "Placa já cadastrada.", parent=frame_veiculo)
        except mysql.connector.Error as err:
             messagebox.showerror("Erro", f"Erro ao cadastrar veículo: {err}", parent=frame_veiculo)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def excluir_veiculo(id_):
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este veículo?", parent=frame_veiculo):
            conn = conectar()
            if not conn:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco para excluir.", parent=frame_veiculo)
                return
                
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM veiculo WHERE id = %s", (id_,))
                conn.commit()
                atualizar_lista()
            except mysql.connector.Error as err:
                 messagebox.showerror("Erro", f"Erro ao excluir veículo: {err}", parent=frame_veiculo)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    # Janela de edição continua Toplevel, relativa à janela principal (app)
    def editar_veiculo(id_, master_app):
        janela_editar = ctk.CTkToplevel(master_app)
        janela_editar.title("Editar Veículo")
        janela_editar.geometry("300x300")
        janela_editar.transient(master_app)
        janela_editar.grab_set()

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para buscar dados.", parent=janela_editar)
            janela_editar.destroy()
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT placa, categoria, capacidade_kg FROM veiculo WHERE id = %s", (id_,))
            dados = cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar dados do veículo: {err}", parent=janela_editar)
            janela_editar.destroy()
            return
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        if not dados:
            messagebox.showerror("Erro", "Veículo não encontrado.", parent=janela_editar)
            janela_editar.destroy()
            return

        placa_atual, categoria_atual, capacidade_atual = dados

        ctk.CTkLabel(janela_editar, text="Placa:").pack(pady=(10,0))
        entry_placa_edit = ctk.CTkEntry(janela_editar, width=250)
        entry_placa_edit.insert(0, placa_atual)
        entry_placa_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="Categoria:").pack(pady=(10,0))
        entry_categoria_edit = ctk.CTkEntry(janela_editar, width=250)
        entry_categoria_edit.insert(0, categoria_atual)
        entry_categoria_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="Capacidade (kg):").pack(pady=(10,0))
        entry_capacidade_edit = ctk.CTkEntry(janela_editar, width=250)
        entry_capacidade_edit.insert(0, str(capacidade_atual).replace(".", ","))
        entry_capacidade_edit.pack(pady=5)

        def salvar_edicao():
            nova_placa = entry_placa_edit.get().upper()
            nova_categoria = entry_categoria_edit.get()
            nova_capacidade_str = entry_capacidade_edit.get()

            if not nova_placa or not nova_categoria or not nova_capacidade_str:
                messagebox.showwarning("Atenção", "Preencha todos os campos.", parent=janela_editar)
                return

            try:
                capacidade_valor = float(nova_capacidade_str.replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Capacidade inválida.", parent=janela_editar)
                return

            conn_save = conectar()
            if not conn_save:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco para salvar.", parent=janela_editar)
                return
                
            try:
                cursor_save = conn_save.cursor()
                cursor_save.execute("""
                    UPDATE veiculo
                    SET placa = %s, categoria = %s, capacidade_kg = %s
                    WHERE id = %s
                """, (nova_placa, nova_categoria, capacidade_valor, id_))
                conn_save.commit()
                atualizar_lista() # Atualiza a lista no frame principal
                janela_editar.destroy()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Erro", "Placa já cadastrada para outro veículo.", parent=janela_editar)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao salvar edição: {err}", parent=janela_editar)
            finally:
                if conn_save.is_connected():
                    cursor_save.close()
                    conn_save.close()

        ctk.CTkButton(janela_editar, text="Salvar", command=salvar_edicao).pack(pady=20)

    # --- Interface Principal do Frame Veículo ---
    # Botão Voltar
    ctk.CTkButton(frame_veiculo, text="< Voltar ao Menu", command=lambda: app.mostrar_frame("Menu")).pack(pady=10, padx=10, anchor="nw")

    ctk.CTkLabel(frame_veiculo, text="Cadastro de Veículo", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

    # Frame para os campos de cadastro
    frame_cadastro = ctk.CTkFrame(frame_veiculo)
    frame_cadastro.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(frame_cadastro, text="Placa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_placa = ctk.CTkEntry(frame_cadastro, placeholder_text="AAA-0000 ou AAA0A00", width=150)
    entry_placa.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_cadastro, text="Categoria:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_categoria = ctk.CTkEntry(frame_cadastro, placeholder_text="Ex: Caminhão, Van, Moto", width=200)
    entry_categoria.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_cadastro, text="Capacidade (kg):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_capacidade = ctk.CTkEntry(frame_cadastro, placeholder_text="Ex: 1500.50", width=100)
    entry_capacidade.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkButton(frame_cadastro, text="Cadastrar Veículo", command=cadastrar_veiculo).grid(row=3, column=0, columnspan=2, pady=10)

    # Frame para a lista de veículos
    ctk.CTkLabel(frame_veiculo, text="Veículos Cadastrados", font=ctk.CTkFont(size=16)).pack(pady=(10,0))
    frame_lista = ctk.CTkScrollableFrame(frame_veiculo, height=250) # Ajustar altura
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    atualizar_lista() # Carrega a lista inicial

    return frame_veiculo # Retorna o frame criado

