create schema transportadora_db;

CREATE TABLE motorista (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    cnh VARCHAR(20) NOT NULL
);

CREATE TABLE veiculo (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10) NOT NULL UNIQUE,
    categoria VARCHAR(50) NOT NULL,
    capacidade_kg FLOAT NOT NULL
);

CREATE TABLE cliente (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    endereco VARCHAR(200) NOT NULL
);

CREATE TABLE pedido (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    motorista_id INT,
    veiculo_id INT,
    cliente_id INT,
    descricao TEXT,
    FOREIGN KEY (motorista_id) REFERENCES motorista(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculo(id),
    FOREIGN KEY (cliente_id) REFERENCES cliente(id)
);