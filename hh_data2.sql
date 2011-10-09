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

CREATE TABLE `Group` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	rate DECIMAL(8, 2) NOT NULL, 
	evaluation BOOL NOT NULL, 
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id), 
	CHECK (evaluation IN (0, 1))
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

CREATE TABLE `Therapist` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	weight INTEGER, 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id)
)ENGINE=InnoDB

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

CREATE TABLE `Client` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(120) NOT NULL, 
	insurance VARCHAR(120), 
	approval TEXT, 
	`DX` VARCHAR(120), 
	note TEXT, 
	address VARCHAR(120), 
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
	id_zoho VARCHAR(40), 
	id_dabble VARCHAR(40), 
	added_time TIMESTAMP NULL, 
	added_user VARCHAR(40), 
	modified_time TIMESTAMP NULL, 
	modified_user VARCHAR(40), 
	PRIMARY KEY (id), 
	FOREIGN KEY(`Officer_id`) REFERENCES `Officer` (id) ON DELETE SET NULL
)ENGINE=InnoDB

 ;

CREATE TABLE `Visit` (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	attend_n BOOL NOT NULL, 
	charge DECIMAL(8, 2) NOT NULL, 
	client_paid DECIMAL(8, 2) NOT NULL, 
	insurance_paid DECIMAL(8, 2) DEFAULT 0.00 NOT NULL, 
	note TEXT, 
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
	FOREIGN KEY(`Client_id`) REFERENCES `Client` (id) ON DELETE CASCADE, 
	FOREIGN KEY(`Session_id`) REFERENCES `Session` (id) ON DELETE CASCADE
)ENGINE=InnoDB

 ;
