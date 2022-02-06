
DROP TABLE IF EXISTS blob;
CREATE TABLE blob (
  name varchar(20) NOT NULL,
  name_container varchar(45) NOT NULL,
  crypto varchar(50) DEFAULT NULL,
  compression varchar(50) DEFAULT NULL,
  PRIMARY KEY (name),
  UNIQUE KEY name_UNIQUE (name),
  UNIQUE KEY name_container_UNIQUE (name_container),
  CONSTRAINT name_container FOREIGN KEY (name_container) REFERENCES container (name) ON UPDATE CASCADE
) 

DROP TABLE IF EXISTS container;
CREATE TABLE container (
  name varchar(30) NOT NULL,
  nome_storage varchar(50) NOT NULL,
  PRIMARY KEY (name),
  UNIQUE KEY name_UNIQUE (name),
  UNIQUE KEY nome_storage_UNIQUE (nome_storage),
  KEY nome_storage_idx (nome_storage),
  CONSTRAINT nome_storage FOREIGN KEY (nome_storage) REFERENCES storage (name) ON UPDATE CASCADE
) 


DROP TABLE IF EXISTS storage;
CREATE TABLE storage (
  name varchar(50) NOT NULL,
  key varchar(200) NOT NULL,
  iduser varchar(100) NOT NULL,
  password varchar(30) NOT NULL,
  PRIMARY KEY (name),
  KEY iduser_idx (iduser),
  CONSTRAINT iduser FOREIGN KEY (iduser) REFERENCES user (idUser) ON UPDATE CASCADE
) 

DROP TABLE IF EXISTS user;
CREATE TABLE user (
  idUser varchar(100) NOT NULL,
  nomeRG varchar(50) NOT NULL,
  PRIMARY KEY (idUser),
  UNIQUE KEY idUser_UNIQUE (idUser),
  UNIQUE KEY nomeRG_UNIQUE (nomeRG)
) 