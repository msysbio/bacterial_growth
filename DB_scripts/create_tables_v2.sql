create database bacterial_growth_v2;
use bacterial_growth_v2;

create table if not exists Bacteria (
	bacteriaId int not null auto_increment,
    bacterialGenus varchar(100),
	bacterialSpecies varchar(100),
	bacterialStrain varchar(100),
    primary key (bacteriaId)
);

create table if not exists Precultivation (
	precultivationId int not null auto_increment,
    mediaName varchar(50),
	mediaFile varchar(100),
	pH float,
    primary key (precultivationId)
);

create table if not exists Reactor (
	reactorId int not null auto_increment,
    volume float,
    atmosphere float,
    stirring_speed float,
    reactorMode varchar(50), #chemostat, batch, fed-batch
    primary key (reactorId)
);

create table if not exists Experiment (
	experimentId int not null auto_increment,
    monoculture boolean default false,
    precultivationId int,
	inoculumConcentration int,
	inoculumVolumen int,
    reactorId int,
    PRIMARY KEY (experimentId),
    FOREIGN KEY (precultivationId) REFERENCES Precultivation (precultivationId) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (reactorId) REFERENCES Reactor (reactorId) ON UPDATE CASCADE ON DELETE SET NULL
);

create table if not exists BacteriaCommunity (
    bacteriaId int,
    experimentId int,
    primary key (bacteriaId, experimentId),
    FOREIGN KEY (bacteriaId) REFERENCES Bacteria (bacteriaId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);

create table if not exists CultivationConditions(
	cultivationId int auto_increment,
    experimentId int,
    mediaName varchar(50),
	mediaFile varchar(100),
    initial_ph float,
    initial_temperature float,
    carbonSource boolean default false,
    antibiotic varchar(100) default null,
    primary key (cultivationId),
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);

# Some ideas for the TechnicalReplicates:
#	- add here the date
#	- sampling time
#	- dilution
#	- serial dilutions??

create table if not exists TechnicalReplicates (
	replicateId int auto_increment,
    cultivationId int,
    bacterialAbundanceMetadataFile varchar(100),
    bacterialAbundanceFile varchar(100),
    metabolitesMetadataFile varchar(100),
    metabolitesFile varchar(100),
    primary key (replicateId),
    FOREIGN KEY (cultivationId) REFERENCES CultivationConditions (cultivationId) ON UPDATE CASCADE ON DELETE CASCADE
);

create table if not exists ExperimentComments (
	commentId int not null auto_increment,
    experimentId int,
    commentText text,
    primary key (commentId),
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);
