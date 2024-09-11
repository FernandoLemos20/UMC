-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


CREATE SCHEMA IF NOT EXISTS `teatro` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `teatro` ;

CREATE TABLE IF NOT EXISTS `teatro`.`pecas_teatro` (
  `id_peca` INT NOT NULL AUTO_INCREMENT,
  `nome_peca` VARCHAR(100) NULL DEFAULT NULL,
  `descricao` TEXT NULL DEFAULT NULL,
  `duracao` INT NULL DEFAULT NULL,
  `data_hora` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id_peca`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

USE `teatro` ;



DELIMITER $$
USE `teatro`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `calcular_media_duracao`(id INT) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN
    DECLARE media DECIMAL(10,2);
    SELECT AVG(duracao) INTO media
    FROM pecas_teatro
    WHERE id_peca = id;
    RETURN media;
END$$

DELIMITER ;


DELIMITER $$
USE `teatro`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `verificar_disponibilidade`(p_data_hora DATETIME) RETURNS tinyint(1)
    DETERMINISTIC
BEGIN
    DECLARE existe INT;
    
    -- Contar quantas entradas existem para a data e hora fornecidas
    SELECT COUNT(*) INTO existe
    FROM pecas_teatro
    WHERE data_hora = p_data_hora;
    
    -- Verificar se existe alguma entrada para a data e hora fornecidas
    IF existe > 0 THEN
        RETURN FALSE;  -- Não está disponível
    ELSE
        RETURN TRUE;   -- Está disponível
    END IF;
END$$

DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
