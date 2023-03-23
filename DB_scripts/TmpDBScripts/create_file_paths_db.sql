create database if not exists FilePaths;
use FilePaths;

drop table FilePath;

create table if not exists FilePath(
	filePath varchar(200),
    primary key (filePath)
);