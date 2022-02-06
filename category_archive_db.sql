use schema Categoryarchivedb

create table user (
  idUser varchar(100) not null constraint user_pk primary key nonclustered,
  nomeRG varchar(50) not null unique,
)
go
create table storage (
  name varchar(50) not null constraint storage_pk primary key nonclustered,
  key varchar(200) not null,
  iduser varchar(100) not null unique,
  password varchar(30) not null,
  CONSTRAINT FK_iduser_iduser FOREIGN KEY (iduser) REFERENCES user (idUser) ON UPDATE CASCADE ON DELETE CASCADE
) 
go
create table container (
  name varchar(30) not null constraint container_pk primary key nonclustered,
  nome_storage varchar(50) not null unique,
  KEY nome_storage_idx (nome_storage),
  CONSTRAINT FK_nome_storage_storage FOREIGN KEY (nome_storage) REFERENCES storage (name) ON UPDATE CASCADE ON DELETE CASCADE
) 
go
create table blob (
  name varchar(20) not null constraint blob_pk primary key nonclustered,
  name_container varchar(45) not null unique,
  crypto varchar(50) DEFAULT null,
  compression varchar(50) DEFAULT null,
  CONSTRAINT FK_name_container_name FOREIGN KEY (name_container) REFERENCES container (name) ON UPDATE CASCADE ON DELETE CASCADE
) 


