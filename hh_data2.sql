SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
CREATE SCHEMA IF NOT EXISTS `hh_office` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;
USE `mydb` ;
USE `hh_office` ;

-- -----------------------------------------------------
-- Table `hh_office`.`Officer`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`Officer` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `email` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `id_zoho` VARCHAR(45) NULL ,
  `id_dabble` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = MyISAM
AUTO_INCREMENT = 428
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`Client`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`Client` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `insurance` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `approval` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `DX` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `note` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `address` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `phone` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `DOB` DATE NULL DEFAULT NULL ,
  `file` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `file_site` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `file_opened` DATE NULL DEFAULT NULL ,
  `Officer_id` INT(11) NULL ,
  `id_zoho` VARCHAR(45) NULL ,
  `id_dabble` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_Client_Officer1` (`Officer_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  CONSTRAINT `fk_Client_Officer1`
    FOREIGN KEY (`Officer_id` )
    REFERENCES `hh_office`.`Officer` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = MyISAM
AUTO_INCREMENT = 1006
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`Group`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`Group` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `rate` DECIMAL(6,2) NOT NULL ,
  `evaluation` TINYINT(1)  NOT NULL ,
  `id_zoho` VARCHAR(45) NULL ,
  `id_dabble` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = MyISAM
AUTO_INCREMENT = 63
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`Therapist`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`Therapist` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `Therapist_name` (`name` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = MyISAM
AUTO_INCREMENT = 25
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`Session`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`Session` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `Group_id` INT(11) NOT NULL ,
  `Therapist_id` INT(11) NULL ,
  `session_date` DATE NOT NULL ,
  `time` VARCHAR(20) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `id_zoho` VARCHAR(45) NULL ,
  `id_dabble` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_Session_Group1` (`Group_id` ASC) ,
  INDEX `fk_Session_Therapist1` (`Therapist_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  CONSTRAINT `fk_Session_Group1`
    FOREIGN KEY (`Group_id` )
    REFERENCES `hh_office`.`Group` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Session_Therapist1`
    FOREIGN KEY (`Therapist_id` )
    REFERENCES `hh_office`.`Therapist` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = MyISAM
AUTO_INCREMENT = 4894
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`Visit`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`Visit` (
  `id` INT(11) NOT NULL AUTO_INCREMENT ,
  `Session_id` INT(11) NOT NULL ,
  `Client_id` INT(11) NOT NULL ,
  `attend_n` TINYINT(1)  NOT NULL ,
  `charge` INT(11) NOT NULL ,
  `client_paid` DECIMAL(6,2) NULL DEFAULT NULL ,
  `note` TEXT CHARACTER SET 'utf8' COLLATE 'utf8_bin' NULL DEFAULT NULL ,
  `insurance_paid` DECIMAL(6,2) NULL DEFAULT NULL ,
  `due` DECIMAL(6,2) NOT NULL ,
  `bill_date` DATE NULL DEFAULT NULL ,
  `check_date` DATE NULL DEFAULT NULL ,
  `id_zoho` VARCHAR(45) NULL ,
  `id_dabble` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  INDEX `fk_Visit_Client1` (`Client_id` ASC) ,
  INDEX `fk_Visit_Session1` (`Session_id` ASC) ,
  CONSTRAINT `fk_Visit_Client1`
    FOREIGN KEY (`Client_id` )
    REFERENCES `hh_office`.`Client` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Visit_Session1`
    FOREIGN KEY (`Session_id` )
    REFERENCES `hh_office`.`Session` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = MyISAM
AUTO_INCREMENT = 11383
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`dataface__failed_logins`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`dataface__failed_logins` (
  `attempt_id` INT(11) NOT NULL AUTO_INCREMENT ,
  `ip_address` VARCHAR(32) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `username` VARCHAR(32) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `time_of_attempt` INT(11) NOT NULL ,
  PRIMARY KEY (`attempt_id`) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`dataface__preferences`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`dataface__preferences` (
  `pref_id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT ,
  `username` VARCHAR(64) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `table` VARCHAR(128) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `record_id` VARCHAR(255) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `key` VARCHAR(128) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  `value` VARCHAR(255) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  PRIMARY KEY (`pref_id`) ,
  INDEX `username` (`username` ASC) ,
  INDEX `table` (`table` ASC) ,
  INDEX `record_id` (`record_id` ASC) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`dataface__version`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`dataface__version` (
  `version` INT(5) NOT NULL DEFAULT '0' )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `hh_office`.`users`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `hh_office`.`users` (
  `username` VARCHAR(80) CHARACTER SET 'utf8' COLLATE 'utf8_bin' NOT NULL ,
  PRIMARY KEY (`username`) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Placeholder table for view `hh_office`.`Client_Balances`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hh_office`.`Client_Balances` (`id` INT, `earliest` INT, `latest` INT, `client_name` INT, `charges` INT, `client_paid` INT, `insurance_paid` INT, `due` INT);

-- -----------------------------------------------------
-- View `hh_office`.`Client_Balances`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `hh_office`.`Client_Balances`;
USE `hh_office`;
CREATE  OR REPLACE VIEW `hh_office`.`Client_Balances` as
select c.id
     , min(s.session_date) as earliest
     , max(s.session_date) as latest
     , c.name as client_name
     , sum(v.charge) as charges
     , sum(v.client_paid) as client_paid
     , sum(v.insurance_paid) as insurance_paid
     , sum(v.due) as due
from Client as c
join Visit as v on v.Client_id = c.id
join `Session` as s on v.Session_id = s.id
group by c.id;
;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
