create database BacterialGrowth;
use BacterialGrowth;

create table if not exists Bacteria (
	bacteriaId int not null unique,
    bacteriaGenus varchar(100) default '',
	bacteriaSpecies varchar(100),
	bacteriaStrain varchar(100),
    primary key (bacteriaSpecies, bacteriaStrain)
);

create table if not exists Precultivation (
	precultivationId int not null auto_increment,
    precultivationDescription text,
    primary key (precultivationId)
);

create table if not exists Reactor (
	reactorId int not null auto_increment,
    reactorName TINYTEXT,
    volume float default 0,
    atmosphere float default 0,
    stirring_speed float default 0,
    reactorMode varchar(50) default '', #chemostat, batch, fed-batch
    primary key (reactorId)
);

create table if not exists Experiment (
	experimentId int not null auto_increment,
    experimentDescription text,
    experimentDate date default null,
    reactorId int,
    PRIMARY KEY (experimentId),
    FOREIGN KEY (reactorId) REFERENCES Reactor (reactorId) ON UPDATE CASCADE ON DELETE SET NULL
);

create table if not exists CultivationConditions(
	cultivationId int,
    cultivationDescription text,
    experimentId int,
    precultivationId int,
    inoculumConcentration int,
	inoculumVolumen int,
    monoculture boolean default false,
    mediaName varchar(50) default '',
	mediaFile varchar(100),
    initial_ph float default 0,
    initial_temperature float default 0,
    carbonSource boolean default false,
    antibiotic varchar(100) default null,
    primary key (cultivationId),
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (precultivationId) REFERENCES Precultivation (precultivationId) ON UPDATE CASCADE ON DELETE SET NULL
);

create table if not exists BacteriaCommunity (
    bacteriaId int,
    cultivationId int,
    primary key (bacteriaId, cultivationId),
    FOREIGN KEY (bacteriaId) REFERENCES Bacteria (bacteriaId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (cultivationId) REFERENCES CultivationConditions (cultivationId) ON UPDATE CASCADE ON DELETE CASCADE
);

create table if not exists TechnicalReplicates (
	replicateId int,
    replicateDescription text,
    cultivationId int,
    bacterialAbundanceMetadataFile varchar(100) default null,
    bacterialAbundanceFile varchar(100),
    metabolitesMetadataFile varchar(100) default null,
    metabolitesFile varchar(100),
    primary key (replicateId),
    FOREIGN KEY (cultivationId) REFERENCES CultivationConditions (cultivationId) ON UPDATE CASCADE ON DELETE CASCADE
);