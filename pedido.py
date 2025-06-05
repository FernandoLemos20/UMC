import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from database import conectar
from ia import gerar_descricao_pedido

# Alterado de abrir_tela para criar_frame_tela
def criar_frame_tela(master, app):
    frame_pedido = ctk.CTkFrame(master)
    
    # Variáveis globais para o frame
    combo_motorista = None
    combo_veiculo = None
    combo_cliente = None
    motoristas_data = []
    veiculos_data = []
    clientes_data = []

    # --- Funções Auxiliares para buscar dados relacionados ---
    def buscar_motoristas():
        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Falha ao conectar ao banco (Motoristas)", parent=frame_pedido)
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome FROM motorista ORDER BY nome ASC")
            motoristas = cursor.fetchall()
            return motoristas
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar motoristas: {err}", parent=frame_pedido)
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def buscar_veiculos():
        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Falha ao conectar ao banco (Veículos)", parent=frame_pedido)
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, placa FROM veiculo ORDER BY placa ASC")
            veiculos = cursor.fetchall()
            return veiculos
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar veículos: {err}", parent=frame_pedido)
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def buscar_clientes(): # Modificado para buscar nome e endereço
        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Falha ao conectar ao banco (Clientes)", parent=frame_pedido)
            return []
        try:
            cursor = conn.cursor()
            # Buscar ID, Nome e Endereço para uso posterior
            cursor.execute("SELECT id, nome, endereco FROM cliente ORDER BY nome ASC") 
            clientes = cursor.fetchall()
            # Formato: [(id1, nome1, end1), (id2, nome2, end2)]
            return clientes
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao buscar clientes: {err}", parent=frame_pedido)
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    # --- Função para atualizar os ComboBoxes ---
    def atualizar_combos():
        nonlocal motoristas_data, veiculos_data, clientes_data
        nonlocal combo_motorista, combo_veiculo, combo_cliente
        
        # Buscar dados atualizados
        motoristas_data = buscar_motoristas()
        veiculos_data = buscar_veiculos()
        clientes_data = buscar_clientes()
        
        # Atualizar valores nos ComboBoxes
        motorista_nomes = [m[1] for m in motoristas_data]
        veiculo_placas = [v[1] for v in veiculos_data]
        cliente_nomes = [c[1] for c in clientes_data]
        
        # Configurar os ComboBoxes com os novos valores
        combo_motorista.configure(values=motorista_nomes)
        combo_veiculo.configure(values=veiculo_placas)
        combo_cliente.configure(values=cliente_nomes)
        
        # Limpar seleções atuais
        combo_motorista.set("")
        combo_veiculo.set("")
        combo_cliente.set("")

    # --- Função pública para atualizar lista quando o frame for mostrado ---
    def atualizar_lista_publica():
        atualizar_combos()
        atualizar_lista()

    # --- Funções Principais do CRUD ---
    def atualizar_lista():
        for widget in frame_lista.winfo_children():
            widget.destroy()

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para listar pedidos.", parent=frame_pedido)
            return
        
        try:
            cursor = conn.cursor()
            # Modificado para incluir c.endereco
            query = """
                SELECT p.id, m.nome, v.placa, c.nome, c.endereco, p.descricao
                FROM pedido p
                LEFT JOIN motorista m ON p.motorista_id = m.id
                LEFT JOIN veiculo v ON p.veiculo_id = v.id
                LEFT JOIN cliente c ON p.cliente_id = c.id
                ORDER BY p.id DESC
            """
            cursor.execute(query)
            pedidos = cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao listar pedidos: {err}", parent=frame_pedido)
            pedidos = []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        for id_, motorista_nome, veiculo_placa, cliente_nome, cliente_endereco, descricao in pedidos:
            motorista_display = motorista_nome if motorista_nome else "N/A"
            veiculo_display = veiculo_placa if veiculo_placa else "N/A"
            cliente_display = cliente_nome if cliente_nome else "N/A"
            endereco_display = cliente_endereco if cliente_endereco else "N/A" # Adicionado endereço
            desc_display = descricao if descricao else ""
            
            # Atualizado para incluir endereço
            texto = f"ID: {id_} | Mot: {motorista_display} | Veic: {veiculo_display} | Cli: {cliente_display} (End: {endereco_display}) | Desc: {desc_display[:30]}..."
            
            item_frame = ctk.CTkFrame(frame_lista)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(item_frame, text=texto, anchor="w", justify="left").pack(side="left", fill="x", expand=True, padx=5)

            botoes_frame = ctk.CTkFrame(item_frame)
            botoes_frame.pack(side="right", padx=5)

            # Passar app como master para janela de edição
            ctk.CTkButton(botoes_frame, text="Editar", width=70, command=lambda i=id_: editar_pedido(i, app)).pack(side="left", padx=2)
            ctk.CTkButton(botoes_frame, text="Excluir", width=70, fg_color="red", command=lambda i=id_: excluir_pedido(i)).pack(side="left", padx=2)

    def cadastrar_pedido():
        motorista_selecionado = combo_motorista.get()
        veiculo_selecionado = combo_veiculo.get()
        cliente_selecionado = combo_cliente.get()
        descricao = entry_descricao.get("1.0", tk.END).strip()

        motorista_id = None
        for mid, mnome in motoristas_data:
            if mnome == motorista_selecionado:
                motorista_id = mid
                break
        
        veiculo_id = None
        for vid, vplaca in veiculos_data:
            if vplaca == veiculo_selecionado:
                veiculo_id = vid
                break

        cliente_id = None
        # Agora clientes_data tem (id, nome, endereco), pegar só id e nome
        for cid, cnome, _ in clientes_data: 
            if cnome == cliente_selecionado:
                cliente_id = cid
                break

        if not motorista_id or not veiculo_id or not cliente_id:
            messagebox.showwarning("Atenção", "Selecione um motorista, veículo e cliente válidos.", parent=frame_pedido)
            return

        conn = conectar()
        if not conn:
             messagebox.showerror("Erro", "Não foi possível conectar ao banco para cadastrar.", parent=frame_pedido)
             return
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pedido (motorista_id, veiculo_id, cliente_id, descricao) VALUES (%s, %s, %s, %s)",
                           (motorista_id, veiculo_id, cliente_id, descricao))
            conn.commit()
            atualizar_lista()
            combo_motorista.set("")
            combo_veiculo.set("")
            combo_cliente.set("")
            entry_descricao.delete("1.0", tk.END)
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao cadastrar pedido: {err}", parent=frame_pedido)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def excluir_pedido(id_):
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este pedido?", parent=frame_pedido):
            conn = conectar()
            if not conn:
                 messagebox.showerror("Erro", "Não foi possível conectar ao banco para excluir.", parent=frame_pedido)
                 return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pedido WHERE id = %s", (id_,))
                conn.commit()
                atualizar_lista()
            except mysql.connector.Error as err:
                 messagebox.showerror("Erro", f"Erro ao excluir pedido: {err}", parent=frame_pedido)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    # Janela de edição Toplevel relativa à janela principal (app)
    def editar_pedido(id_, master_app):
        janela_editar = ctk.CTkToplevel(master_app)
        janela_editar.title("Editar Pedido")
        janela_editar.geometry("400x400")
        janela_editar.transient(master_app)
        janela_editar.grab_set()

        conn = conectar()
        if not conn:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco para buscar dados do pedido.", parent=janela_editar)
            janela_editar.destroy()
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT motorista_id, veiculo_id, cliente_id, descricao FROM pedido WHERE id = %s", (id_,))
            dados = cursor.fetchone()
        except mysql.connector.Error as err:
             messagebox.showerror("Erro", f"Erro ao buscar dados do pedido: {err}", parent=janela_editar)
             janela_editar.destroy()
             return
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        if not dados:
            messagebox.showerror("Erro", "Pedido não encontrado.", parent=janela_editar)
            janela_editar.destroy()
            return

        motorista_id_atual, veiculo_id_atual, cliente_id_atual, descricao_atual = dados

        # Buscar dados atualizados para os ComboBoxes de edição
        motoristas_edit_data = buscar_motoristas()
        veiculos_edit_data = buscar_veiculos()
        clientes_edit_data = buscar_clientes() # Já busca endereço, mas só precisamos do nome para o combo

        motorista_nomes_edit = [m[1] for m in motoristas_edit_data]
        veiculo_placas_edit = [v[1] for v in veiculos_edit_data]
        cliente_nomes_edit = [c[1] for c in clientes_edit_data] # Apenas nomes para o combo

        motorista_atual_nome = next((m[1] for m in motoristas_edit_data if m[0] == motorista_id_atual), "")
        veiculo_atual_placa = next((v[1] for v in veiculos_edit_data if v[0] == veiculo_id_atual), "")
        cliente_atual_nome = next((c[1] for c in clientes_edit_data if c[0] == cliente_id_atual), "")

        ctk.CTkLabel(janela_editar, text="Motorista:").pack(pady=(10,0))
        combo_motorista_edit = ctk.CTkComboBox(janela_editar, values=motorista_nomes_edit, width=300)
        combo_motorista_edit.set(motorista_atual_nome)
        combo_motorista_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="Veículo:").pack(pady=(10,0))
        combo_veiculo_edit = ctk.CTkComboBox(janela_editar, values=veiculo_placas_edit, width=300)
        combo_veiculo_edit.set(veiculo_atual_placa)
        combo_veiculo_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="Cliente:").pack(pady=(10,0))
        combo_cliente_edit = ctk.CTkComboBox(janela_editar, values=cliente_nomes_edit, width=300)
        combo_cliente_edit.set(cliente_atual_nome)
        combo_cliente_edit.pack(pady=5)

        ctk.CTkLabel(janela_editar, text="Descrição:").pack(pady=(10,0))
        entry_descricao_edit = ctk.CTkTextbox(janela_editar, height=80, width=300)
        entry_descricao_edit.insert("1.0", descricao_atual if descricao_atual else "")
        entry_descricao_edit.pack(pady=5)

        def salvar_edicao():
            novo_motorista_selecionado = combo_motorista_edit.get()
            novo_veiculo_selecionado = combo_veiculo_edit.get()
            novo_cliente_selecionado = combo_cliente_edit.get()
            nova_descricao = entry_descricao_edit.get("1.0", tk.END).strip()

            novo_motorista_id = next((m[0] for m in motoristas_edit_data if m[1] == novo_motorista_selecionado), None)
            novo_veiculo_id = next((v[0] for v in veiculos_edit_data if v[1] == novo_veiculo_selecionado), None)
            novo_cliente_id = next((c[0] for c in clientes_edit_data if c[1] == novo_cliente_selecionado), None)

            if not novo_motorista_id or not novo_veiculo_id or not novo_cliente_id:
                messagebox.showwarning("Atenção", "Selecione um motorista, veículo e cliente válidos.", parent=janela_editar)
                return

            conn_save = conectar()
            if not conn_save:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco para salvar.", parent=janela_editar)
                return
            try:
                cursor_save = conn_save.cursor()
                cursor_save.execute("""
                    UPDATE pedido
                    SET motorista_id = %s, veiculo_id = %s, cliente_id = %s, descricao = %s
                    WHERE id = %s
                """, (novo_motorista_id, novo_veiculo_id, novo_cliente_id, nova_descricao, id_))
                conn_save.commit()
                atualizar_lista()
                janela_editar.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Erro", f"Erro ao salvar edição: {err}", parent=janela_editar)
            finally:
                 if conn_save.is_connected():
                    cursor_save.close()
                    conn_save.close()

        ctk.CTkButton(janela_editar, text="Salvar", command=salvar_edicao).pack(pady=20)

    # --- Interface Principal do Frame Pedido ---
    # Botão Voltar
    ctk.CTkButton(frame_pedido, text="< Voltar ao Menu", command=lambda: app.mostrar_frame("Menu")).pack(pady=10, padx=10, anchor="nw")

    ctk.CTkLabel(frame_pedido, text="Gerenciamento de Pedidos", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

    # Frame para os campos de cadastro
    frame_cadastro = ctk.CTkFrame(frame_pedido)
    frame_cadastro.pack(pady=10, padx=10, fill="x")

    # Inicializar os dados para os ComboBoxes
    motoristas_data = buscar_motoristas()
    veiculos_data = buscar_veiculos()
    clientes_data = buscar_clientes() # Retorna (id, nome, endereco)

    motorista_nomes = [m[1] for m in motoristas_data]
    veiculo_placas = [v[1] for v in veiculos_data]
    cliente_nomes = [c[1] for c in clientes_data] # Apenas nomes para o combo

    ctk.CTkLabel(frame_cadastro, text="Motorista:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_motorista = ctk.CTkComboBox(frame_cadastro, values=motorista_nomes, width=250)
    combo_motorista.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_cadastro, text="Veículo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    combo_veiculo = ctk.CTkComboBox(frame_cadastro, values=veiculo_placas, width=250)
    combo_veiculo.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_cadastro, text="Cliente:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    combo_cliente = ctk.CTkComboBox(frame_cadastro, values=cliente_nomes, width=250)
    combo_cliente.grid(row=2, column=1, padx=5, pady=5)

    ctk.CTkLabel(frame_cadastro, text="Descrição:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky="nw")
    entry_descricao = ctk.CTkTextbox(frame_cadastro, height=100, width=300)
    entry_descricao.grid(row=0, column=3, rowspan=3, padx=5, pady=5, sticky="nsew")

    def gerar_descricao():
        # Pega os valores selecionados nos ComboBoxes
        cliente_selecionado = combo_cliente.get()
        motorista_selecionado = combo_motorista.get()
        veiculo_selecionado = combo_veiculo.get()

        # Verifica se todos os campos foram selecionados
        if not app.gemini_model:
           # Mostra um erro se o modelo não foi inicializado corretamente no main.py
           messagebox.showerror("Erro IA", 
                                "O modelo de IA não foi inicializado corretamente. Verifique a API Key em .env e reinicie.", 
                                parent=frame_pedido) # Certifique-se que frame_pedido é o nome correto do frame
           return

        try:
            # Limpa a caixa de texto e mostra mensagem de "Gerando..."
            entry_descricao.delete("1.0", tk.END)
            entry_descricao.insert("1.0", "Gerando descrição com IA...")
            app.update_idletasks() # Atualiza a interface para mostrar a mensagem

            # Chama a função da IA com os argumentos corretos
            descricao_gerada = gerar_descricao_pedido(app.gemini_model, cliente_selecionado, motorista_selecionado, veiculo_selecionado)
            
            # Limpa a caixa de texto e insere a descrição gerada
            entry_descricao.delete("1.0", tk.END)
            entry_descricao.insert("1.0", descricao_gerada)
        except Exception as e:
            # Mostra erro se a geração falhar
            messagebox.showerror("Erro IA", f"Falha ao gerar descrição: {e}", parent=frame_pedido)
            entry_descricao.delete("1.0", tk.END) # Limpa a caixa de texto em caso de erro

    # Cria o botão e associa a função gerar_descricao
    btn_gerar_ia = ctk.CTkButton(frame_cadastro, text="Gerar com IA", command=gerar_descricao)
    btn_gerar_ia.grid(row=3, column=3, pady=(0, 15), sticky="e")

    # Botão para atualizar manualmente os ComboBoxes
    btn_atualizar = ctk.CTkButton(frame_cadastro, text="Atualizar Listas", command=atualizar_combos)
    btn_atualizar.grid(row=3, column=1, pady=(0, 15), sticky="w")

    # Ajustar columnspan e posicionamento do botão
    frame_cadastro.grid_columnconfigure(3, weight=1) # Permitir que a coluna da descrição expanda
    ctk.CTkButton(frame_cadastro, text="Cadastrar Pedido", command=cadastrar_pedido).grid(row=3, column=0, columnspan=4, pady=15)

    # Frame para a lista de pedidos
    ctk.CTkLabel(frame_pedido, text="Pedidos Cadastrados", font=ctk.CTkFont(size=16)).pack(pady=(10,0))
    frame_lista = ctk.CTkScrollableFrame(frame_pedido, height=300)
    frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

    # Adicionar método para atualização pública
    frame_pedido.atualizar_lista_publica = atualizar_lista_publica

    atualizar_lista() # Carrega a lista inicial

    return frame_pedido # Retorna o frame criado
