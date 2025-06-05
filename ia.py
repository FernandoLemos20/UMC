import google.generativeai as genai
# REMOVA a linha genai.configure daqui

# A função agora recebe o 'model' como primeiro argumento
def gerar_descricao_pedido(model, cliente_nome, motorista_nome, veiculo_placa):
    """Gera a descrição do pedido usando um modelo Gemini já inicializado."""
    if not model:
        # Retorna um erro se o modelo não for passado corretamente
        return "Erro: Modelo Gemini não fornecido para gerar descrição."
        
    prompt = f"""
    Crie uma descrição resumida, clara e profissional para um pedido de transporte:
    - Cliente: {cliente_nome}
    - Motorista: {motorista_nome}
    - Veículo: {veiculo_placa}
    """

    try:
        # Usa o modelo recebido como argumento
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro na API Gemini ao gerar descrição: {e}")
        # Retorna uma mensagem de erro ou lança a exceção
        # return f"Erro ao contatar a IA: {e}"
        # É melhor tratar o erro onde a função é chamada (em pedido.py)
        raise e 
