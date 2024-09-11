create schema halloween;
use halloween;
CREATE TABLE tabela_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    idade INT NOT NULL
);

-- Defina o delimitador para evitar conflitos com ponto e vírgula
DELIMITER $$

CREATE PROCEDURE InsereUsuariosAleatorios()
BEGIN
    DECLARE i INT DEFAULT 0;

    -- Loop para inserir 10.000 registros
    WHILE i < 10000 DO
        -- Gere dados aleatórios para os campos
        SET @nome := CONCAT('Usuario', i);
        SET @email := CONCAT('usuario', i, '@exemplo.com');
        SET @idade := FLOOR(RAND() * 80) + 18;  -- Gera uma idade entre 18 e 97 anos

        -- Insira o novo registro na tabela de usuários
        INSERT INTO tabela_usuarios (nome, email, idade) VALUES (@nome, @email, @idade);

        -- Incrementa o contador
        SET i = i + 1;
    END WHILE;
END$$

-- Restaure o delimitador padrão
DELIMITER ;
