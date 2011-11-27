use hh_office;

CREATE TABLE users (
	username VARCHAR(120) NOT NULL, 
	role ENUM('READ ONLY','EDIT','DELETE','OWNER','REVIEWER','USER','ADMIN','MANAGER'), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (username)
)ENGINE=InnoDB

 ;

CREATE TABLE `Diagnosis` (
	icd9 VARCHAR(8) NOT NULL, 
	name VARCHAR(120), 
	PRIMARY KEY (icd9)
)ENGINE=InnoDB

 ;

CREATE TABLE `Batch` (
	name VARCHAR(120) NOT NULL, 
	cutoff DATE, 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (name)
)

 ;

CREATE TABLE `Office` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	address VARCHAR(120), 
	fax VARCHAR(120), 
	notes TEXT, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id)
)ENGINE=InnoDB

 ;

CREATE TABLE `Carrier` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	address VARCHAR(50) NOT NULL, 
	city_st_zip VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id)
)ENGINE=InnoDB

 ;

CREATE TABLE `Therapist` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	weight INTEGER, 
	npi VARCHAR(10), 
	tax_id VARCHAR(15), 
	acode INTEGER, 
	phone INTEGER, 
	address VARCHAR(29), 
	city_st_zip VARCHAR(29), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id)
)ENGINE=InnoDB

 ;

CREATE TABLE `Procedure` (
	cpt VARCHAR(6) NOT NULL, 
	name VARCHAR(120), 
	PRIMARY KEY (cpt)
)ENGINE=InnoDB

 ;

CREATE TABLE `Officer` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(120), 
	`Office_id` INTEGER, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id), 
	FOREIGN KEY(`Office_id`) REFERENCES `Office` (id) ON DELETE SET NULL
)ENGINE=InnoDB

 ;

CREATE TABLE `Group` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP, 
	modified_user VARCHAR(40), 
	name VARCHAR(120) NOT NULL, 
	rate DECIMAL(8, 2) NOT NULL, 
	evaluation BOOL DEFAULT 0, 
	cpt VARCHAR(6), 
	PRIMARY KEY (id), 
	CHECK (evaluation IN (0, 1)), 
	FOREIGN KEY(cpt) REFERENCES `Procedure` (cpt)
)ENGINE=InnoDB

 ;

CREATE TABLE `Client` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP, 
	modified_user VARCHAR(40), 
	name VARCHAR(120) NOT NULL, 
	insurance VARCHAR(120), 
	approval TEXT, 
	`DX` VARCHAR(120), 
	address VARCHAR(120), 
	note TEXT, 
	phone VARCHAR(120), 
	`DOB` DATE, 
	`Officer_id` INTEGER, 
	file VARCHAR(40), 
	file_site ENUM('op','kck'), 
	file_opened DATE, 
	billing_cutoff DATE, 
	recent DATE, 
	charges DECIMAL(8, 2), 
	client_paid DECIMAL(8, 2), 
	insurance_paid DECIMAL(8, 2), 
	balance DECIMAL(8, 2), 
	balance_cached TIMESTAMP NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(`Officer_id`) REFERENCES `Officer` (id) ON DELETE SET NULL
)ENGINE=InnoDB

 ;

CREATE TABLE `Session` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	session_date DATE NOT NULL, 
	time VARCHAR(40), 
	`Group_id` INTEGER NOT NULL, 
	`Therapist_id` INTEGER, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id), 
	FOREIGN KEY(`Group_id`) REFERENCES `Group` (id) ON DELETE CASCADE, 
	FOREIGN KEY(`Therapist_id`) REFERENCES `Therapist` (id) ON DELETE SET NULL
)ENGINE=InnoDB

 ;

CREATE TABLE `Visit` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	attend_n BOOL DEFAULT 0, 
	charge DECIMAL(8, 2) NOT NULL, 
	client_paid DECIMAL(8, 2) NOT NULL, 
	insurance_paid DECIMAL(8, 2) DEFAULT 0.00 NOT NULL, 
	note TEXT, 
	cpt VARCHAR(6), 
	claim_uid VARCHAR(40), 
	bill_date DATE, 
	check_date DATE, 
	`Client_id` INTEGER NOT NULL, 
	`Session_id` INTEGER NOT NULL, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id), 
	CHECK (attend_n IN (0, 1)), 
	FOREIGN KEY(cpt) REFERENCES `Procedure` (cpt), 
	FOREIGN KEY(`Client_id`) REFERENCES `Client` (id) ON DELETE CASCADE, 
	FOREIGN KEY(`Session_id`) REFERENCES `Session` (id) ON DELETE CASCADE
)ENGINE=InnoDB

 ;

CREATE TABLE `Insurance` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	added_time TIMESTAMP, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP, 
	modified_user VARCHAR(40), 
	`Carrier_id` INTEGER NOT NULL, 
	payer_type ENUM('Medicare','Medicaid','Group Health Plan','Other') NOT NULL, 
	id_number VARCHAR(30) NOT NULL, 
	`Client_id` INTEGER NOT NULL, 
	patient_sex ENUM('M','F') NOT NULL, 
	insured_name VARCHAR(30) NOT NULL, 
	patient_address VARCHAR(30) NOT NULL, 
	patient_city VARCHAR(24) NOT NULL, 
	patient_state VARCHAR(3) NOT NULL, 
	patient_zip VARCHAR(12) NOT NULL, 
	patient_acode VARCHAR(3), 
	patient_phone VARCHAR(10), 
	patient_rel ENUM('Self','Spouse','Child','Other') NOT NULL, 
	insured_address VARCHAR(30) NOT NULL, 
	insured_city VARCHAR(24) NOT NULL, 
	insured_state VARCHAR(3) NOT NULL, 
	insured_zip VARCHAR(12) NOT NULL, 
	insured_acode VARCHAR(3), 
	insured_phone VARCHAR(10), 
	patient_status ENUM('Single','Married','Other'), 
	patient_status2 ENUM('Employed','Full Time Student','Part Time Student'), 
	insured_policy VARCHAR(30), 
	insured_dob DATE, 
	insured_sex ENUM('M','F'), 
	dx1 VARCHAR(8), 
	dx2 VARCHAR(8), 
	approval TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(`Carrier_id`) REFERENCES `Carrier` (id) ON DELETE CASCADE, 
	FOREIGN KEY(`Client_id`) REFERENCES `Client` (id) ON DELETE CASCADE, 
	FOREIGN KEY(dx1) REFERENCES `Diagnosis` (icd9), 
	FOREIGN KEY(dx2) REFERENCES `Diagnosis` (icd9)
)ENGINE=InnoDB

 ;
