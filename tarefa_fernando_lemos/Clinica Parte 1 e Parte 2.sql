-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema clinica
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema clinica
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `clinica` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `clinica` ;

-- -----------------------------------------------------
-- Table `clinica`.`pacientes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`pacientes` (
  `id_paciente` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NULL DEFAULT NULL,
  `especie` VARCHAR(50) NULL DEFAULT NULL,
  `idade` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id_paciente`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `clinica`.`veterinarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`veterinarios` (
  `id_veterinario` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NULL DEFAULT NULL,
  `especialidade` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`id_veterinario`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `clinica`.`agendamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`agendamentos` (
  `id_agendamento` INT NOT NULL AUTO_INCREMENT,
  `id_paciente` INT NULL DEFAULT NULL,
  `id_veterinario` INT NULL DEFAULT NULL,
  `data_agendamento` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id_agendamento`),
  INDEX `id_paciente` (`id_paciente` ASC),
  INDEX `id_veterinario` (`id_veterinario` ASC),
  CONSTRAINT `agendamentos_ibfk_1`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `clinica`.`pacientes` (`id_paciente`),
  CONSTRAINT `agendamentos_ibfk_2`
    FOREIGN KEY (`id_veterinario`)
    REFERENCES `clinica`.`veterinarios` (`id_veterinario`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `clinica`.`consultas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`consultas` (
  `id_consulta` INT NOT NULL AUTO_INCREMENT,
  `id_paciente` INT NULL DEFAULT NULL,
  `id_veterinario` INT NULL DEFAULT NULL,
  `data_consulta` DATE NULL DEFAULT NULL,
  `custo` DECIMAL(10,2) NULL DEFAULT NULL,
  PRIMARY KEY (`id_consulta`),
  INDEX `id_paciente` (`id_paciente` ASC),
  INDEX `id_veterinario` (`id_veterinario` ASC),
  CONSTRAINT `consultas_ibfk_1`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `clinica`.`pacientes` (`id_paciente`),
  CONSTRAINT `consultas_ibfk_2`
    FOREIGN KEY (`id_veterinario`)
    REFERENCES `clinica`.`veterinarios` (`id_veterinario`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `clinica`.`log_consultas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`log_consultas` (
  `id_log` INT NOT NULL AUTO_INCREMENT,
  `id_consulta` INT NULL DEFAULT NULL,
  `custo_antigo` DECIMAL(10,2) NULL DEFAULT NULL,
  `custo_novo` DECIMAL(10,2) NULL DEFAULT NULL,
  PRIMARY KEY (`id_log`),
  INDEX `id_consulta` (`id_consulta` ASC),
  CONSTRAINT `log_consultas_ibfk_1`
    FOREIGN KEY (`id_consulta`)
    REFERENCES `clinica`.`consultas` (`id_consulta`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `clinica`.`medicamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`medicamentos` (
  `id_medicamento` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NULL DEFAULT NULL,
  `descricao` VARCHAR(255) NULL DEFAULT NULL,
  `preco` DECIMAL(10,2) NULL DEFAULT NULL,
  PRIMARY KEY (`id_medicamento`))
ENGINE = InnoDB
AUTO_INCREMENT = 7
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `clinica`.`tratamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clinica`.`tratamentos` (
  `id_tratamento` INT NOT NULL AUTO_INCREMENT,
  `id_paciente` INT NULL DEFAULT NULL,
  `id_medicamento` INT NULL DEFAULT NULL,
  `data_inicio` DATE NULL DEFAULT NULL,
  `data_fim` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`id_tratamento`),
  INDEX `id_paciente` (`id_paciente` ASC),
  INDEX `id_medicamento` (`id_medicamento` ASC),
  CONSTRAINT `tratamentos_ibfk_1`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `clinica`.`pacientes` (`id_paciente`),
  CONSTRAINT `tratamentos_ibfk_2`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `clinica`.`medicamentos` (`id_medicamento`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

USE `clinica` ;

-- -----------------------------------------------------
-- procedure adicionar_medicamento
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `adicionar_medicamento`(
    IN p_nome VARCHAR(100),
    IN p_descricao VARCHAR(255),
    IN p_preco DECIMAL(10, 2)
)
BEGIN
    INSERT INTO Medicamentos (nome, descricao, preco)
    VALUES (p_nome, p_descricao, p_preco);
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure agendar_consulta
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `agendar_consulta`(
    IN p_id_paciente INT,
    IN p_id_veterinario INT,
    IN p_data_consulta DATE,
    IN p_custo DECIMAL(10, 2)
)
BEGIN
    INSERT INTO Consultas (id_paciente, id_veterinario, data_consulta, custo)
    VALUES (p_id_paciente, p_id_veterinario, p_data_consulta, p_custo);
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure atualizar_data_tratamento
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `atualizar_data_tratamento`(
    IN p_id_tratamento INT,
    IN p_data_inicio DATE,
    IN p_data_fim DATE
)
BEGIN
    UPDATE Tratamentos
    SET data_inicio = p_data_inicio, data_fim = p_data_fim
    WHERE id_tratamento = p_id_tratamento;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure atualizar_paciente
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `atualizar_paciente`(
    IN p_id_paciente INT,
    IN novo_nome VARCHAR(100),
    IN nova_especie VARCHAR(50),
    IN nova_idade INT
)
BEGIN
    UPDATE Pacientes
    SET nome = novo_nome, especie = nova_especie, idade = nova_idade
    WHERE id_paciente = p_id_paciente;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure listar_agendamentos_paciente
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `listar_agendamentos_paciente`(
    IN p_id_paciente INT
)
BEGIN
    SELECT * FROM Agendamentos
    WHERE id_paciente = p_id_paciente;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure listar_medicamentos
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `listar_medicamentos`()
BEGIN
    SELECT * FROM Medicamentos;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure listar_tratamentos_paciente
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `listar_tratamentos_paciente`(
    IN p_id_paciente INT
)
BEGIN
    SELECT Pacientes.nome AS nome_paciente,
           Medicamentos.nome AS nome_medicamento,
           Tratamentos.data_inicio,
           Tratamentos.data_fim
    FROM Tratamentos
    INNER JOIN Pacientes ON Tratamentos.id_paciente = Pacientes.id_paciente
    INNER JOIN Medicamentos ON Tratamentos.id_medicamento = Medicamentos.id_medicamento
    WHERE Pacientes.id_paciente = p_id_paciente;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure remover_consulta
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `remover_consulta`(
    IN p_id_consulta INT
)
BEGIN
    DELETE FROM Consultas
    WHERE id_consulta = p_id_consulta;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- function total_gasto_paciente
-- -----------------------------------------------------

DELIMITER $$
USE `clinica`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `total_gasto_paciente`(
    p_id_paciente INT
) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10, 2);
    SELECT SUM(custo) INTO total
    FROM Consultas
    WHERE id_paciente = p_id_paciente;
    RETURN IFNULL(total, 0);
END$$

DELIMITER ;
USE `clinica`;

DELIMITER $$
USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`log_alteracao_paciente`
AFTER UPDATE ON `clinica`.`pacientes`
FOR EACH ROW
BEGIN
    INSERT INTO Log_Alteracoes_Pacientes (id_paciente, nome_antigo, nome_novo, data_alteracao)
    VALUES (OLD.id_paciente, OLD.nome, NEW.nome, NOW());
END$$

USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`verificar_idade_paciente`
BEFORE INSERT ON `clinica`.`pacientes`
FOR EACH ROW
BEGIN
    IF NEW.idade <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A idade do paciente deve ser um número positivo.';
    END IF;
END$$

USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`registrar_data_agendamento`
BEFORE INSERT ON `clinica`.`agendamentos`
FOR EACH ROW
BEGIN
    SET NEW.data_agendamento = NOW();
END$$

USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`verificar_sobreposicao_agendamento`
BEFORE INSERT ON `clinica`.`agendamentos`
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM Agendamentos
        WHERE id_veterinario = NEW.id_veterinario
        AND data_agendamento = NEW.data_agendamento
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Este veterinário já tem um agendamento para este horário.';
    END IF;
END$$

USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`atualizar_custo_consulta`
AFTER UPDATE ON `clinica`.`consultas`
FOR EACH ROW
BEGIN
    IF NEW.custo <> OLD.custo THEN
        INSERT INTO Log_Consultas (id_consulta, custo_antigo, custo_novo)
        VALUES (OLD.id_consulta, OLD.custo, NEW.custo);
    END IF;
END$$

USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`atualizar_preco_medicamento`
AFTER INSERT ON `clinica`.`tratamentos`
FOR EACH ROW
BEGIN
    UPDATE Medicamentos
    SET preco = preco + (preco * 0.1)
    WHERE id_medicamento = NEW.id_medicamento;
END$$

USE `clinica`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `clinica`.`verificar_data_tratamento`
BEFORE INSERT ON `clinica`.`tratamentos`
FOR EACH ROW
BEGIN
    IF NEW.data_fim <= NEW.data_inicio THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'A data final deve ser posterior à data de início.';
    END IF;
END$$


DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
