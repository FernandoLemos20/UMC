import customtkinter as ctk
import tkinter as tk
import google.generativeai as genai
import threading
import time
from CTkMessagebox import CTkMessagebox

# Variáveis globais para os widgets da interface do chatbot
txt_chat_historico = None
txt_chat_usuario = None
btn_enviar = None
janela_chatbot = None
gemini_chat_obj = None
gemini_model = None  # Adicionado para ter acesso ao modelo

# Constantes para controle de fallback
MODELO_PRINCIPAL = "models/gemini-1.5-flash"  
MODELO_FALLBACK = "models/gemini-1.5-flash-latest"   
usando_modelo_fallback = False

def processar_mensagem_em_thread(texto_usuario):
    """Processa a mensagem em uma thread separada para não congelar a interface"""
    global txt_chat_historico, janela_chatbot, gemini_chat_obj, gemini_model, usando_modelo_fallback
    
    # Envia para a API Gemini e obtém a resposta
    texto_resposta = ""
    try:
       
        resposta = gemini_chat_obj.send_message(texto_usuario)
        texto_resposta = resposta.text
    except Exception as e:
        erro_str = str(e)
        print(f"Erro Gemini API: {erro_str}")
        
        # Verifica se é erro de cota (código 429) ou modelo não encontrado (404)
        if ("429" in erro_str or "404" in erro_str) and not usando_modelo_fallback:
            try:
                # Tenta alternar para o modelo fallback
                usando_modelo_fallback = True
                texto_resposta = f"⚠️ Detectei um erro com o modelo atual. Vou tentar usar um modelo alternativo...\n\n"
                
                # Inicializa o modelo fallback
                novo_modelo = genai.GenerativeModel(MODELO_FALLBACK)
                novo_chat = novo_modelo.start_chat(history=[])
                
                # Substitui o modelo e chat atuais
                gemini_model = novo_modelo
                gemini_chat_obj = novo_chat
                
                # Tenta novamente com o modelo fallback
                resposta_fallback = gemini_chat_obj.send_message(texto_usuario)
                texto_resposta += resposta_fallback.text
            except Exception as e2:
                texto_resposta = f"Não foi possível obter uma resposta.\n\nErro: {str(e2)}\n\nSugestões:\n1. Aguarde alguns minutos e tente novamente\n2. Verifique sua conexão com a internet\n3. A API gratuita do Google tem limites de uso - considere uma versão paga para uso intensivo"
        else:
            # Formata uma mensagem de erro mais amigável
            texto_resposta = f"Não foi possível obter uma resposta do assistente.\n\n"
            
            if "429" in erro_str:
                texto_resposta += "Você atingiu o limite de solicitações da API gratuita do Google. Sugestões:\n"
                texto_resposta += "1. Aguarde alguns minutos antes de tentar novamente\n"
                texto_resposta += "2. Faça perguntas mais curtas e objetivas\n"
                texto_resposta += "3. Para uso intensivo, considere configurar uma chave de API paga"
            else:
                texto_resposta += f"Erro: {erro_str}"
    
    # Atualiza a interface na thread principal
    if janela_chatbot and janela_chatbot.winfo_exists():
        janela_chatbot.after(0, atualizar_chat_com_resposta, texto_resposta)

def atualizar_chat_com_resposta(texto_resposta):
    """Atualiza o chat com a resposta obtida (chamada na thread principal)"""
    global txt_chat_historico, btn_enviar
    
    # Habilita o botão de enviar novamente
    if btn_enviar:
        btn_enviar.configure(state=tk.NORMAL, text="Enviar")
    
    # Substitui "Pensando..." pela resposta real
    if txt_chat_historico:
        txt_chat_historico.configure(state=tk.NORMAL)
        
        # Encontra e remove a última linha "Bot: Pensando..."
        conteudo = txt_chat_historico.get("1.0", tk.END)
        linhas = conteudo.split('\n')
        for i in range(len(linhas)-1, -1, -1):
            if linhas[i].startswith("Bot: Pensando..."):
                # Encontrou a linha "Pensando..."
                txt_chat_historico.delete("1.0", tk.END)  # Limpa tudo
                # Reinsere tudo exceto a linha "Pensando..."
                for j in range(len(linhas)):
                    if j != i and linhas[j]:
                        txt_chat_historico.insert(tk.END, linhas[j] + "\n")
                break
        
        # Insere a resposta
        txt_chat_historico.insert(tk.END, f"Bot: {texto_resposta}\n\n")
        txt_chat_historico.see(tk.END)
        txt_chat_historico.configure(state=tk.DISABLED)

def enviar_mensagem_chat():
    """Função chamada quando o usuário envia uma mensagem"""
    global txt_chat_historico, txt_chat_usuario, janela_chatbot, gemini_chat_obj, btn_enviar

    if not gemini_chat_obj:
        CTkMessagebox(master=janela_chatbot, title="Erro Gemini", 
                     message="Chatbot Gemini não inicializado corretamente.", icon="cancel")
        return

    texto_usuario = txt_chat_usuario.get("1.0", tk.END).strip()
    if not texto_usuario:
        CTkMessagebox(master=janela_chatbot, title="Atenção", 
                     message="Digite uma mensagem para enviar ao bot.", icon="warning")
        return

    # Desabilita o botão de enviar durante o processamento
    btn_enviar.configure(state=tk.DISABLED, text="Aguarde...")

    # Exibe a mensagem do usuário
    txt_chat_historico.configure(state=tk.NORMAL)
    txt_chat_historico.insert(tk.END, f"Você: {texto_usuario}\n")
    txt_chat_historico.see(tk.END)
    txt_chat_usuario.delete("1.0", tk.END)
    txt_chat_historico.configure(state=tk.DISABLED)
    janela_chatbot.update_idletasks()

    # Mostra "Pensando..."
    txt_chat_historico.configure(state=tk.NORMAL)
    txt_chat_historico.insert(tk.END, "Bot: Pensando...\n")
    txt_chat_historico.see(tk.END)
    txt_chat_historico.configure(state=tk.DISABLED)
    janela_chatbot.update_idletasks()

    # Inicia uma thread para processar a mensagem
    threading.Thread(target=processar_mensagem_em_thread, args=(texto_usuario,), daemon=True).start()

def criar_interface_chatbot(master, chat_obj):
    """Cria a interface do chatbot dentro da janela master (Toplevel)."""
    global txt_chat_historico, txt_chat_usuario, btn_enviar, janela_chatbot, gemini_chat_obj, gemini_model

    janela_chatbot = master
    gemini_chat_obj = chat_obj
    gemini_model = master.master.gemini_model if hasattr(master.master, 'gemini_model') else None

    master.title("Chatbot Assistente")
    master.geometry("600x500")
    master.resizable(True, True)
    master.transient(master.master)
    master.grab_set()

    # Frame principal
    frame_chatbot = ctk.CTkFrame(master)
    frame_chatbot.pack(pady=10, padx=10, fill="both", expand=True)

    # Histórico da conversa (somente leitura)
    txt_chat_historico = ctk.CTkTextbox(frame_chatbot, wrap="word", state=tk.DISABLED)
    txt_chat_historico.pack(pady=(0, 10), padx=10, fill="both", expand=True)

    # Frame para entrada do usuário e botão
    frame_entrada = ctk.CTkFrame(frame_chatbot)
    frame_entrada.pack(pady=(0, 10), padx=10, fill="x")

    # Entrada de texto do usuário
    txt_chat_usuario = ctk.CTkTextbox(frame_entrada, height=80, wrap="word")
    txt_chat_usuario.pack(side=tk.LEFT, pady=0, padx=(0, 10), fill="x", expand=True)
    # Bind Enter para enviar mensagem
    txt_chat_usuario.bind("<Return>", lambda event: enviar_mensagem_chat())
    txt_chat_usuario.bind("<Shift-Return>", lambda event: txt_chat_usuario.insert(tk.INSERT, '\n'))

    # Botão Enviar
    btn_enviar = ctk.CTkButton(frame_entrada, text="Enviar", width=80, command=enviar_mensagem_chat)
    btn_enviar.pack(side=tk.RIGHT, pady=0, padx=0)

    # Foco inicial na caixa de texto do usuário
    txt_chat_usuario.focus_set()

    # Adiciona uma mensagem inicial do bot
    modelo_nome = MODELO_PRINCIPAL.split('/')[-1]
    txt_chat_historico.configure(state=tk.NORMAL)
    txt_chat_historico.insert(tk.END, f"Bot: Olá! Como posso ajudar você hoje? (usando modelo {modelo_nome})\n\n")
    txt_chat_historico.configure(state=tk.DISABLED)
