CREATE DATABASE BacterialGrowth;
USE BacterialGrowth;

CREATE TABLE IF NOT EXISTS Bacteria (
	bacteriaId INT NOT NULL UNIQUE,
    bacteriaGenus VARCHAR(100) DEFAULT '',
	bacteriaSpecies VARCHAR(100),
	bacteriaStrain VARCHAR(100),
    PRIMARY KEY (bacteriaSpecies, bacteriaStrain)
);

CREATE TABLE IF NOT EXISTS Precultivation (
	precultivationId INT AUTO_INCREMENT,
    precultivationDescription TEXT,
    PRIMARY KEY (precultivationId)
);

CREATE TABLE IF NOT EXISTS Reactor (
	reactorId INT AUTO_INCREMENT,
    reactorName TINYTEXT NOT NULL,
    volume FLOAT DEFAULT 0,
    atmosphere FLOAT DEFAULT 0,
    stirring_speed FLOAT DEFAULT 0,
    reactorMode VARCHAR(50) DEFAULT '', #chemostat, batch, fed-batch,
    reactorDescription TEXT,
    PRIMARY KEY (reactorId)
);

CREATE TABLE IF NOT EXISTS Experiment (
	experimentId INT AUTO_INCREMENT,
    experimentName TINYTEXT,
    experimentDate DATE DEFAULT NULL,
    reactorId INT,
    experimentDescription TEXT,
    PRIMARY KEY (experimentId),
    FOREIGN KEY (reactorId) REFERENCES Reactor (reactorId) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS CultivationConditions(
	cultivationId INT,
    experimentId INT,
    precultivationId INT,
    inoculumConcentration INT,
	inoculumVolume INT,
    monoculture BOOLEAN DEFAULT FALSE,
    mediaName VARCHAR(50) DEFAULT '',
	mediaFile VARCHAR(100),
    initialPh FLOAT DEFAULT 0,
    initialTemperature FLOAT DEFAULT 0,
    carbonSource BOOLEAN DEFAULT FALSE,
    antibiotic VARCHAR(100) DEFAULT NULL,
    cultivationDescription TEXT,
    PRIMARY KEY (cultivationId),
    FOREIGN KEY (experimentId) REFERENCES Experiment (experimentId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (precultivationId) REFERENCES Precultivation (precultivationId) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS BacteriaCommunity (
    bacteriaId INT,
    cultivationId INT,
    PRIMARY KEY (bacteriaId, cultivationId),
    FOREIGN KEY (bacteriaId) REFERENCES Bacteria (bacteriaId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (cultivationId) REFERENCES CultivationConditions (cultivationId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TechnicalReplicates (
	replicateId VARCHAR(10),
    cultivationId INT,
    #bacterialAbundanceMetadataFile VARCHAR(100) DEFAULT NULL,
    bacterialAbundanceFile VARCHAR(100),
    #metabolitesMetadataFile VARCHAR(100) DEFAULT NULL,
    metabolitesFile VARCHAR(100),
    phFile VARCHAR(100),
    replicateDescription TEXT,
    PRIMARY KEY (replicateId),
    FOREIGN KEY (cultivationId) REFERENCES CultivationConditions (cultivationId) ON UPDATE CASCADE ON DELETE CASCADE
);