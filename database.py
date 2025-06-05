import mysql.connector

def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            
            database="transportadora_db"
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        # Você pode querer tratar o erro de forma diferente, como lançar uma exceção
        # ou retornar None e verificar isso nas funções que chamam conectar()
        return None

def criar_tabelas():
    conn = conectar()
    if conn is None:
        print("Não foi possível conectar ao banco para criar tabelas.")
        return
    
    cursor = conn.cursor()

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS motorista (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            cpf VARCHAR(14) NOT NULL UNIQUE,
            cnh VARCHAR(20) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            placa VARCHAR(20) NOT NULL UNIQUE,
            categoria VARCHAR(100) NOT NULL,
            capacidade_kg FLOAT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            cpf VARCHAR(14) NOT NULL UNIQUE,
            endereco VARCHAR(255) NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedido (
            id INT AUTO_INCREMENT PRIMARY KEY,
            motorista_id INT,
            veiculo_id INT,
            cliente_id INT,
            descricao TEXT,
            FOREIGN KEY (motorista_id) REFERENCES motorista(id),
            FOREIGN KEY (veiculo_id) REFERENCES veiculo(id),
            FOREIGN KEY (cliente_id) REFERENCES cliente(id)
        );
        """)

        conn.commit()
        print("Tabelas verificadas/criadas com sucesso.")
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabelas: {err}")
    finally:
        cursor.close()
        conn.close()

# Opcional: Chamar criar_tabelas() aqui se você quiser garantir que elas existam
# na primeira vez que o módulo database for importado.
# criar_tabelas()

