# grafo_clientes_motoristas.py

import mysql.connector
from collections import defaultdict

# Tenta importar bibliotecas opcionais para visualização
try:
    import networkx as nx
    import matplotlib.pyplot as plt
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Aviso: Bibliotecas networkx e matplotlib não encontradas. A visualização do grafo não estará disponível.")
    print("Para visualizar o grafo, instale as bibliotecas: pip install networkx matplotlib")

# Importa a função de conexão do seu projeto
# Certifique-se que este script esteja no mesmo diretório que database.py
# ou ajuste o import conforme a estrutura do seu projeto.
try:
    from database import conectar
except ImportError:
    print("Erro: Não foi possível importar a função conectar() do arquivo database.py.")
    print("Certifique-se que grafo_clientes_motoristas.py está no diretório correto.")
    # Define uma função dummy para evitar erros posteriores se a importação falhar
    def conectar():
        print("ERRO FATAL: Função conectar() não encontrada.")
        return None

def obter_dados_pedidos():
    """Busca os IDs de cliente e motorista de todos os pedidos no banco de dados."""
    conn = conectar()
    if not conn:
        print("Não foi possível conectar ao banco de dados para obter dados dos pedidos.")
        return []
    
    pedidos_data = []
    cursor = conn.cursor()
    try:
        # Seleciona apenas os IDs necessários e onde ambos não são nulos
        cursor.execute("SELECT cliente_id, motorista_id FROM pedido WHERE cliente_id IS NOT NULL AND motorista_id IS NOT NULL")
        pedidos_data = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erro ao buscar dados dos pedidos: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return pedidos_data

def criar_lista_adjacencia_clientes_por_motorista(pedidos_data):
    """
    Cria uma lista de adjacências representando clientes conectados por pedidos 
    com o mesmo motorista.

    Args:
        pedidos_data: Uma lista de tuplas (cliente_id, motorista_id).

    Returns:
        Um dicionário onde as chaves são IDs de clientes e os valores são conjuntos
        de IDs de outros clientes conectados pelo mesmo motorista em algum pedido.
        Ex: {cliente1: {cliente2, cliente3}, cliente2: {cliente1}, ...}
    """
    if not pedidos_data:
        print("Não há dados de pedidos para gerar a lista de adjacências.")
        return {}

    # 1. Agrupa clientes por motorista
    motorista_para_clientes = defaultdict(set)
    for cliente_id, motorista_id in pedidos_data:
        motorista_para_clientes[motorista_id].add(cliente_id)

    # 2. Cria a lista de adjacências para clientes
    adjacencia_clientes = defaultdict(set)
    # Itera sobre cada grupo de clientes que usaram o mesmo motorista
    for motorista_id, clientes_do_motorista in motorista_para_clientes.items():
        # Se mais de um cliente usou o mesmo motorista, eles estão conectados
        if len(clientes_do_motorista) > 1:
            lista_clientes = list(clientes_do_motorista)
            # Adiciona uma aresta entre todos os pares de clientes nesse grupo
            for i in range(len(lista_clientes)):
                for j in range(i + 1, len(lista_clientes)):
                    cliente_a = lista_clientes[i]
                    cliente_b = lista_clientes[j]
                    adjacencia_clientes[cliente_a].add(cliente_b)
                    adjacencia_clientes[cliente_b].add(cliente_a)
                    
    # Garante que todos os clientes que fizeram pedidos estejam no dicionário,
    # mesmo que não tenham conexões (conjunto vazio)
    todos_clientes_com_pedido = {cliente_id for cliente_id, _ in pedidos_data}
    for cliente_id in todos_clientes_com_pedido:
        if cliente_id not in adjacencia_clientes:
            adjacencia_clientes[cliente_id] = set()

    return dict(adjacencia_clientes) # Converte de volta para dict normal

def gerar_e_mostrar_grafo(adj_list):
    """
    Cria e exibe um grafo a partir da lista de adjacências usando NetworkX e Matplotlib.
    Esta função só executa se as bibliotecas estiverem disponíveis.
    """
    if not NETWORKX_AVAILABLE:
        print("Visualização indisponível. Instale networkx e matplotlib.")
        return
        
    if not adj_list:
        print("Lista de adjacências vazia, não é possível gerar o grafo.")
        return

    G = nx.Graph()

    # Adiciona nós (todos os clientes na lista de adjacências)
    for cliente_id in adj_list.keys():
        G.add_node(cliente_id)

    # Adiciona arestas
    for cliente_id, vizinhos in adj_list.items():
        for vizinho_id in vizinhos:
            # Evita adicionar a mesma aresta duas vezes (embora nx.Graph lide com isso)
            if cliente_id < vizinho_id: 
                G.add_edge(cliente_id, vizinho_id)

    print("\n--- Informações do Grafo ---")
    print(f"Número de nós (Clientes): {G.number_of_nodes()}")
    print(f"Número de arestas (Conexões via Motorista): {G.number_of_edges()}")
    # print(f"Nós: {list(G.nodes())}")
    # print(f"Arestas: {list(G.edges())}")
    print("---------------------------")

    # Desenha o grafo
    plt.figure(figsize=(10, 8)) # Ajusta o tamanho da figura
    pos = nx.spring_layout(G, k=0.5, iterations=50) # Algoritmo de layout para melhor visualização
    nx.draw(G, pos, 
            with_labels=True,       # Mostra os IDs dos clientes nos nós
            node_color='skyblue',   # Cor dos nós
            node_size=1500,         # Tamanho dos nós
            edge_color='gray',      # Cor das arestas
            font_size=10,           # Tamanho da fonte dos rótulos
            font_weight='bold')
    plt.title("Grafo de Clientes Conectados por Pedidos com o Mesmo Motorista")
    plt.show()

# --- Exemplo de Uso --- 
def main():
    print("Buscando dados dos pedidos...")
    pedidos = obter_dados_pedidos()
    
    if not pedidos:
        print("Não foram encontrados dados de pedidos para processar.")
        return
        
    print(f"\nTotal de registros de pedidos (cliente_id, motorista_id) encontrados: {len(pedidos)}")
    # print("Dados brutos:", pedidos) # Descomente para ver os dados brutos

    print("\nGerando a lista de adjacências...")
    lista_adj = criar_lista_adjacencia_clientes_por_motorista(pedidos)
    
    if not lista_adj:
        print("Não foi possível gerar a lista de adjacências.")
        return
        
    print("\n--- Lista de Adjacências (Cliente -> {Clientes conectados}) ---")
    # Imprime de forma mais legível
    if lista_adj:
        for cliente, vizinhos in sorted(lista_adj.items()):
            print(f"  Cliente {cliente}: {vizinhos if vizinhos else '{}'}")
    else:
        print("  (Vazia)")
    print("-------------------------------------------------------------")

    print("\nTentando gerar e mostrar o grafo...")
    gerar_e_mostrar_grafo(lista_adj)

if __name__ == "__main__":
    main()

