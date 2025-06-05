import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
from database import conectar

# Alterado de abrir_tela para criar_frame_tela
def criar_frame_tela(master, app):
    frame_cliente = ctk.CTkFrame(master)

    # --- Funções internas do frame ---
    def atualizar_lista():
        for widget in frame_lista.winfo_children():
            widget.destroy()

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para listar clientes.", parent=frame_cliente)
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, cpf, endereco FROM cliente ORDER BY nome ASC")
            clientes = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar clientes: {err}", parent=frame_cliente)
            clientes = []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        for id_, nome, cpf, endereco in clientes:
            item_frame = ctk.CTkFrame(frame_lista)
            item_frame.pack(fill="x", padx=5, pady=2)

            texto = f"{nome} | CPF: {cpf} | Endereço: {endereco}"
            ctk.CTkLabel(item_frame, text=texto, anchor="w").pack(side="left", fill="x", expand=True, padx=5)

            botoes_frame = ctk.CTkFrame(item_frame)
            botoes_frame.pack(side="right")

            # Passar 'app' como master para a janela de edição
            ctk.CTkButton(botoes_frame, text="Editar", width=70, command=lambda i=id_: editar_cliente(i, app)).pack(side="left", padx=2)
            ctk.CTkButton(botoes_frame, text="Excluir", width=70, fg_color="red", command=lambda i=id_: excluir_cliente(i)).pack(side="left", padx=2)

    def cadastrar_cliente():
        nome = entry_nome.get()
        cpf = entry_cpf.get()
        endereco = entry_endereco.get()

        if not nome or not cpf or not endereco:
            messagebox.showwarning("Atenção", "Preencha todos os campos.", parent=frame_cliente)
            return

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para cadastrar.", parent=frame_cliente)
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cliente (nome, cpf, endereco) VALUES (%s, %s, %s)",
                           (nome, cpf, endereco))
            conn.commit()
            atualizar_lista()
            entry_nome.delete(0, 'end')
            entry_cpf.delete(0, 'end')
            entry_endereco.delete(0, 'end')
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "CPF já cadastrado.", parent=frame_cliente)
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao cadastrar cliente: {err}", parent=frame_cliente)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def excluir_cliente(id_):
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este cliente?", parent=frame_cliente):
            conn = conectar()
            if not conn:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco para excluir.", parent=frame_cliente)
                return
                
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cliente WHERE id = %s", (id_,))
                conn.commit()
                atualizar_lista()
            except mysql.connector.Error as err:
                 messagebox.showerror("Erro", f"Erro ao excluir cliente: {err}", parent=frame_cliente)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    # Janela de edição continua Toplevel, relativa à janela principal (app)
    def editar_cliente(id_, master_app):
        janela_editar = ctk.CTkToplevel(master_app)
        janela_editar.title("Editar Cliente")
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
            cursor.execute("SELECT nome, cpf, endereco FROM cliente WHERE id = %s", (id_,))
            dados = cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar dados do cliente: {err}", parent=janela_editar)
            janela_editar.destroy()
            return
        finally:
             if conn.is_connected():
                cursor.close()
                conn.close()

        if not dados:
            messagebox.showerror("Erro", "Cliente não encontrado.", parent=janela_editar)
            janela_editar.destroy()
            return

        nome_atual, cpf_atual, endereco_atual = dados

        ctk.CTkLabel(janela_editar, text="Nome:").pack(pady=(10,0))
        entry_nome_edit = ctk.CTkEntry(janela_editar, width=250)
        entry_nome_edit.insert(0, nome_atual)
        entry_nome_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="CPF:").pack(pady=(10,0))
        entry_cpf_edit = ctk.CTkEntry(janela_editar, width=250)
        entry_cpf_edit.insert(0, cpf_atual)
        entry_cpf_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="Endereço:").pack(pady=(10,0))
        entry_endereco_edit = ctk.CTkEntry(janela_editar, width=250)
        entry_endereco_edit.insert(0, endereco_atual)
        entry_endereco_edit.pack(pady=5)

        def salvar_edicao():
            novo_nome = entry_nome_edit.get()
            novo_cpf = entry_cpf_edit.get()
            novo_endereco = entry_endereco_edit.get()

            if not novo_nome or not novo_cpf or not novo_endereco:
                messagebox.showwarning("Atenção", "Preencha todos os campos.", parent=janela_editar)
                return

            conn_save = conectar()
            if not conn_save:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco para salvar.", parent=janela_editar)
                return
                
            try:
                cursor_save = conn_save.cursor()
                cursor_save.execute("""
                    UPDATE cliente
                    SET nome = %s, cpf = %s, endereco = %s
                    WHERE id = %s
                """, (novo_nome, novo_cpf, novo_endereco, id_))
                conn_save.commit()
                atualizar_lista() # Atualiza a lista no frame principal
                janela_editar.destroy()
            except mysql.connector.IntegrityError:
                messagebox.showerror("Erro", "CPF já cadastrado para outro cliente.", parent=janela_editar)
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao salvar edição: {err}", parent=janela_editar)
            finally:
                if conn_save.is_connected():
                    cursor_save.close()
                    conn_save.close()

        ctk.CTkButton(janela_editar, text="Salvar", command=salvar_edicao).pack(pady=20)

    # --- Interface Principal do Frame Cliente ---
    # Botão Voltar
    ctk.CTkButton(frame_cliente, text="< Voltar ao Menu", command=lambda: app.mostrar_frame("Menu")).pack(pady=10, padx=10, anchor="nw")

    ctk.CTkLabel(frame_cliente, text="Cadastro de Cliente", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

    # Frame para os campos de cadastro
    frame_cadastro = ctk.CTkFrame(frame_cliente)
    frame_cadastro.pack(pady=10, padx=10, fill="x")

    ctk.CTkLabel(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nome = ctk.CTkEntry(frame_cadastro, placeholder_text="Nome completo", width=300)
    entry_nome.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_cadastro, text="CPF:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_cpf = ctk.CTkEntry(frame_cadastro, placeholder_text="___.___.___-__", width=150)
    entry_cpf.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ctk.CTkLabel(frame_cadastro, text="Endereço:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_endereco = ctk.CTkEntry(frame_cadastro, placeholder_text="Rua, Número, Bairro, Cidade - UF", width=400)
    entry_endereco.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkButton(frame_cadastro, text="Cadastrar Cliente", command=cadastrar_cliente).grid(row=3, column=0, columnspan=2, pady=10)

    # Frame para a lista de clientes
    ctk.CTkLabel(frame_cliente, text="Clientes Cadastrados", font=ctk.CTkFont(size=16)).pack(pady=(10,0))
    frame_lista = ctk.CTkScrollableFrame(frame_cliente, height=250) # Ajustar altura
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    atualizar_lista() # Carrega a lista inicial

    return frame_cliente # Retorna o frame criado

