use bacterial_growth;

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

create table if not exists Conditions (
	conditionId int not null auto_increment,
    carbonSource boolean default false,
    primary key (conditionId)
);

create table if not exists Reactor (
	reactorId int not null auto_increment,
    volume float,
    atmosphere float,
    stirring_speed float,
    reactorMode varchar(50), #chemostat, batch, fed-batch
    primary key (reactorId)
);

create table if not exists Cultivation (
	cultivationId int not null auto_increment,
    mediaName varchar(50),
	mediaFile varchar(100),
    initial_ph float,
    initial_temperature float, 
    primary key (cultivationId)
);

create table if not exists Treatment (
	treatmentId int not null auto_increment,
    antibiotic varchar(100),
    primary key (treatmentId)
);

create table if not exists Experiment (
	experimentId int not null auto_increment,
    monoculture boolean default false,
    precultivationId int,
	inoculumConcentration int,
	inoculumVolumen int,
    conditionId int,
	reactorId int,
    cultivationId int,
    treatmentId int, 
    PRIMARY KEY (experimentId),
    FOREIGN KEY (precultivationId) REFERENCES Precultivation (precultivationId) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (conditionId) REFERENCES Conditions (conditionId) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (reactorId) REFERENCES Reactor (reactorId) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (cultivationId) REFERENCES Cultivation (cultivationId) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (treatmentId) REFERENCES Treatment (treatmentId) ON UPDATE CASCADE ON DELETE SET NULL
);

create table if not exists Bacteria_Community (
	comunnityId int not null auto_increment, 
    bacteriaId int,
    experimentId int,
    primary key (comunnityId),
    FOREIGN KEY (bacteriaId) REFERENCES Bacteria (bacteriaId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);

create table if not exists Experiment_Comments (
	commentId int not null auto_increment,
    experimentId int,
    commentText text,
    primary key (commentId),
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);

create table if not exists Technical_Replicates (
	replicateId int not null auto_increment,
    experimentId int,
    bacterialAbundanceMetadataFile varchar(100),
    bacterialAbundanceFile varchar(100),
    metabolitesMetadataFile varchar(100),
    metabolitesFile varchar(100),
    primary key (replicateId),
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);
