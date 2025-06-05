import customtkinter as ctk
import tkinter as tk
from database import criar_tabelas
# Importar os módulos que contêm as funções para criar os frames
import motorista
import veiculo
import cliente
import pedido
import chatbot # Módulo do chatbot
import relatorios # Adicionado import para o novo módulo de relatórios

# Importar Gemini e CTkMessagebox para inicialização e erros
import google.generativeai as genai
from CTkMessagebox import CTkMessagebox

# --- Importar o módulo do grafo ---
import grafo_clientes_motoristas
# ---------------------------------

#Manter API Key Oculta
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== Configurações Gemini ====================
# Substitua pela sua chave de API real!


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Transportadora")
        self.geometry("800x600") # Ajustar tamanho inicial se necessário

        # Configurar tema escuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Inicialização Gemini ---
        self.gemini_model = None
        self.gemini_chat = None
        try:
            # Corrigido para comparar com o placeholder original
            gemini_api_key_from_env = os.getenv("GEMINI_API_KEY")
             
             # Verifica se a chave foi encontrada no .env
            if not gemini_api_key_from_env:
                 # Mantém o erro original se a variável não estiver no .env
                 raise ValueError("Chave da API Gemini não encontrada no arquivo .env ou nas variáveis de ambiente.")
             
             # Configura a API com a chave lida
            genai.configure(api_key=gemini_api_key_from_env)
           
            # Usar um modelo recente e válido
            nome_modelo_para_usar = "models/gemini-1.5-flash-latest" # Ou gemini-1.5-pro-latest
            print(f"Inicializando o modelo Gemini: {nome_modelo_para_usar}...")
            self.gemini_model = genai.GenerativeModel(nome_modelo_para_usar)
            self.gemini_chat = self.gemini_model.start_chat(history=[])
            print(f"Modelo {nome_modelo_para_usar} inicializado com sucesso.")
        except Exception as e:
            error_message = f"Falha ao configurar ou inicializar a API Gemini: {e}\nVerifique sua chave de API em main.py e a conexão."
            print(f"ERRO GEMINI: {error_message}")
            # Mostra o erro na inicialização, mas permite que o app continue sem o chatbot
            CTkMessagebox(title="Erro API Gemini", message=error_message, icon="cancel")
            self.gemini_chat = None # Garante que o chat está None se falhar
        # ---------------------------

        # Criar tabelas do banco (chamar apenas uma vez)
        # Movido para antes da inicialização da App se necessário, mas aqui está ok
        # criar_tabelas()

        # Container principal para alternar os frames
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dicionário para guardar os frames das telas
        self.frames = {}

        # Criar e adicionar o frame do menu principal
        self.criar_frame_menu()
        
        # Criar os frames das outras telas (mas não mostrar ainda)
        self.criar_frame_modulo("Motorista", motorista.criar_frame_tela)
        self.criar_frame_modulo("Veiculo", veiculo.criar_frame_tela)
        self.criar_frame_modulo("Cliente", cliente.criar_frame_tela)
        self.criar_frame_modulo("Pedido", pedido.criar_frame_tela)
        self.criar_frame_modulo("Relatorios", relatorios.criar_frame_tela) # Adicionado frame de Relatórios

        # Mostrar o frame inicial (Menu)
        self.mostrar_frame("Menu")

    def criar_frame_menu(self):
        frame = ctk.CTkFrame(self.container)
        self.frames["Menu"] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(frame, text="Menu Principal", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=25) # Ajuste pady

        ctk.CTkButton(frame, text="Motoristas", command=lambda: self.mostrar_frame("Motorista")).pack(pady=8)
        ctk.CTkButton(frame, text="Veículos", command=lambda: self.mostrar_frame("Veiculo")).pack(pady=8)
        ctk.CTkButton(frame, text="Clientes", command=lambda: self.mostrar_frame("Cliente")).pack(pady=8)
        ctk.CTkButton(frame, text="Pedidos", command=lambda: self.mostrar_frame("Pedido")).pack(pady=8)
        ctk.CTkButton(frame, text="Relatórios", command=lambda: self.mostrar_frame("Relatorios")).pack(pady=8) # Adicionado botão Relatórios
        
        # --- Botão Chatbot ---
        estado_botao_chat = tk.NORMAL if self.gemini_chat else tk.DISABLED
        texto_botao_chat = "Abrir Chatbot Assistente" if self.gemini_chat else "Chatbot Indisponível (Erro API)"
        ctk.CTkButton(frame, text=texto_botao_chat, command=self.abrir_chatbot, state=estado_botao_chat).pack(pady=15) # Espaçamento maior
        # ---------------------

    def criar_frame_modulo(self, nome_frame, funcao_criar_frame):
        # A função criar_frame_tela de cada módulo deve aceitar 'master' e 'app' (ou 'controller')
        frame = funcao_criar_frame(master=self.container, app=self)
        self.frames[nome_frame] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, nome_frame):
        # Atualizar listas antes de mostrar (se a função existir no frame)
        # if nome_frame in self.frames and hasattr(self.frames[nome_frame], "atualizar_lista_publica"):
        #      self.frames[nome_frame].atualizar_lista_publica()
             
        frame = self.frames[nome_frame]
        frame.tkraise() # Traz o frame para a frente

    # --- Função para abrir o Chatbot ---
    def abrir_chatbot(self):
        if not self.gemini_chat:
             CTkMessagebox(title="Erro", message="O chatbot não pôde ser inicializado devido a um erro na API Gemini.", icon="cancel")
             return
             
        # Cria uma nova janela Toplevel para o chatbot
        janela_chat = ctk.CTkToplevel(self)
        # Passa a janela Toplevel e o objeto de chat para a função de criação da interface
        chatbot.criar_interface_chatbot(janela_chat, self.gemini_chat)
    # ----------------------------------

if __name__ == "__main__":
    # --- Geração Automática do Grafo --- 
    print("--- Iniciando Geração Automática do Grafo Clientes-Motoristas ---")
    # Garante que as tabelas existam antes de buscar dados
    print("Verificando/Criando tabelas do banco de dados...")
    criar_tabelas()
    
    print("Buscando dados dos pedidos para o grafo...")
    pedidos_grafo = grafo_clientes_motoristas.obter_dados_pedidos()
    
    if pedidos_grafo:
        print("Gerando a lista de adjacências...")
        lista_adj_grafo = grafo_clientes_motoristas.criar_lista_adjacencia_clientes_por_motorista(pedidos_grafo)
        
        print("\n--- Lista de Adjacências (Cliente -> {Clientes conectados}) ---")
        if lista_adj_grafo:
            for cliente_id, vizinhos in sorted(lista_adj_grafo.items()):
                print(f"  Cliente {cliente_id}: {vizinhos if vizinhos else {}}")

        else:
            print("  (Vazia ou nenhum cliente conectado)")
        print("-------------------------------------------------------------")

        print("\nTentando gerar e mostrar o grafo (feche a janela do grafo para continuar)...")
        grafo_clientes_motoristas.gerar_e_mostrar_grafo(lista_adj_grafo)
        print("--- Geração do Grafo Concluída ---")
    else:
        print("Não foram encontrados dados de pedidos válidos para gerar o grafo.")
    # -------------------------------------

    # --- Inicialização da Aplicação Principal ---
    print("\nIniciando a aplicação principal...")
    app = App()
    app.mainloop()
    # -------------------------------------------
