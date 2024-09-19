

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


CREATE SCHEMA IF NOT EXISTS `clinica` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `clinica` ;

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



CREATE TABLE IF NOT EXISTS `clinica`.`veterinarios` (
  `id_veterinario` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NULL DEFAULT NULL,
  `especialidade` VARCHAR(50) NULL DEFAULT NULL,
  PRIMARY KEY (`id_veterinario`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;



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

USE `clinica` ;



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
TRIGGER `clinica`.`atualizar_custo_consulta`
AFTER UPDATE ON `clinica`.`consultas`
FOR EACH ROW
BEGIN
    IF NEW.custo <> OLD.custo THEN
        INSERT INTO Log_Consultas (id_consulta, custo_antigo, custo_novo)
        VALUES (OLD.id_consulta, OLD.custo, NEW.custo);
    END IF;
END$$


DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
