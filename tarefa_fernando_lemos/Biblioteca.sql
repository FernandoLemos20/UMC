-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE SCHEMA IF NOT EXISTS `biblioteca` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `biblioteca` ;


CREATE TABLE IF NOT EXISTS `biblioteca`.`autor` (
  `id_autor` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(255) NOT NULL,
  `data_nascimento` DATE NULL DEFAULT NULL,
  `nacionalidade` VARCHAR(100) NULL DEFAULT NULL,
  `biografia` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id_autor`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS `biblioteca`.`livro` (
  `id_livro` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(255) NOT NULL,
  `genero` VARCHAR(100) NULL DEFAULT NULL,
  `num_paginas` INT NULL DEFAULT NULL,
  `descricao` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id_livro`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;



CREATE TABLE IF NOT EXISTS `biblioteca`.`autor_livro` (
  `id_autor` INT NOT NULL,
  `id_livro` INT NOT NULL,
  `ano` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id_autor`, `id_livro`),
  INDEX `id_livro` (`id_livro` ASC) ,
  CONSTRAINT `autor_livro_ibfk_1`
    FOREIGN KEY (`id_autor`)
    REFERENCES `biblioteca`.`autor` (`id_autor`),
  CONSTRAINT `autor_livro_ibfk_2`
    FOREIGN KEY (`id_livro`)
    REFERENCES `biblioteca`.`livro` (`id_livro`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

USE `biblioteca` ;



DELIMITER $$
USE `biblioteca`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `adicionar_autor`(
    IN p_nome VARCHAR(255),
    IN p_data_nascimento DATE,
    IN p_nacionalidade VARCHAR(100),
    IN p_biografia TEXT
)
BEGIN
    INSERT INTO autor (nome, data_nascimento, nacionalidade, biografia)
    VALUES (p_nome, p_data_nascimento, p_nacionalidade, p_biografia);
END$$

DELIMITER ;



DELIMITER $$
USE `biblioteca`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `adicionar_livro`(
    IN p_titulo VARCHAR(255),
    IN p_genero VARCHAR(100),
    IN p_num_paginas INT,
    IN p_descricao TEXT
)
BEGIN
    INSERT INTO livro (titulo, genero, num_paginas, descricao)
    VALUES (p_titulo, p_genero, p_num_paginas, p_descricao);
END$$

DELIMITER ;



DELIMITER $$
USE `biblioteca`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `autor_do_livro`(
    p_id_autor INT,
    p_id_livro INT
) RETURNS tinyint(1)
    DETERMINISTIC
BEGIN
    DECLARE resultado BOOLEAN;
    
    IF EXISTS (
        SELECT 1 FROM autor_livro 
        WHERE id_autor = p_id_autor AND id_livro = p_id_livro
    ) THEN
        SET resultado = TRUE;
    ELSE
        SET resultado = FALSE;
    END IF;
    
    RETURN resultado;
END$$

DELIMITER ;



DELIMITER $$
USE `biblioteca`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `livros_por_autor`(p_id_autor INT) RETURNS int
    DETERMINISTIC
BEGIN
    DECLARE numero_livros INT;
    
    SELECT COUNT(*) INTO numero_livros
    FROM autor_livro
    WHERE id_autor = p_id_autor;
    
    RETURN numero_livros;
END$$

DELIMITER ;



DELIMITER $$
USE `biblioteca`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `testar_funcionalidade`(
    IN p_nome_autor VARCHAR(255),
    IN p_data_nascimento DATE,
    IN p_nacionalidade VARCHAR(100),
    IN p_biografia TEXT,
    IN p_titulo_livro VARCHAR(255),
    IN p_genero VARCHAR(100),
    IN p_num_paginas INT,
    IN p_descricao TEXT,
    IN p_ano INT
)
BEGIN
    DECLARE v_id_autor INT;
    DECLARE v_id_livro INT;
    DECLARE v_autor_escreveu BOOLEAN;
    DECLARE v_numero_livros INT;

   
    CALL adicionar_autor(p_nome_autor, p_data_nascimento, p_nacionalidade, p_biografia);

    
    SELECT LAST_INSERT_ID() INTO v_id_autor;

    
    CALL adicionar_livro(p_titulo_livro, p_genero, p_num_paginas, p_descricao);

    
    SELECT LAST_INSERT_ID() INTO v_id_livro;

    
    INSERT INTO autor_livro (id_autor, id_livro, ano) VALUES (v_id_autor, v_id_livro, p_ano);

    
    SET v_autor_escreveu = autor_do_livro(v_id_autor, v_id_livro);

    
    SET v_numero_livros = livros_por_autor(v_id_autor);

    
    SELECT v_id_autor AS id_autor, v_id_livro AS id_livro, v_autor_escreveu AS autor_escreveu, v_numero_livros AS total_livros;
END$$

DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
