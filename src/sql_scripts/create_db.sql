DROP DATABASE BacterialGrowth;
CREATE DATABASE BacterialGrowth;
USE BacterialGrowth;

CREATE TABLE IF NOT EXISTS Study (
	studyId INT AUTO_INCREMENT,
    studyName VARCHAR(20) DEFAULT NULL, 
    studyDescription TEXT DEFAULT NULL,
    PRIMARY KEY (studyId),
    UNIQUE (studyName)
);

CREATE TABLE IF NOT EXISTS Precultivation (
	precultivationId INT AUTO_INCREMENT,
    precultivationDescription TEXT,
    PRIMARY KEY (precultivationId)
);

CREATE TABLE IF NOT EXISTS Reactor (
	reactorId INT AUTO_INCREMENT,
    reactorName VARCHAR(50) NOT NULL,
    volume FLOAT(7,2) DEFAULT 0,
    atmosphere FLOAT(7,2) DEFAULT 0,
    stirring_speed FLOAT(7,2) DEFAULT 0,
    stirring_mode VARCHAR(50) DEFAULT '', #linear motion, orbital, etc
    reactorMode VARCHAR(50) DEFAULT '', #chemostat, batch, fed-batch,
    reactorDescription TEXT,
    PRIMARY KEY (reactorId),
    UNIQUE (reactorName, volume, atmosphere, stirring_speed, reactorMode)
);

CREATE TABLE IF NOT EXISTS Bacteria (
	bacteriaId INT AUTO_INCREMENT,
    bacteriaGenus VARCHAR(100) DEFAULT NULL,
	bacteriaSpecies VARCHAR(100),
	bacteriaStrain VARCHAR(100),
    PRIMARY KEY (bacteriaId),
    UNIQUE (bacteriaSpecies, bacteriaStrain)
);

CREATE TABLE IF NOT EXISTS Taxon (
	taxonId INT AUTO_INCREMENT,
    phylum VARCHAR(100) DEFAULT NULL,
    class VARCHAR(100) DEFAULT NULL,
    order_txn VARCHAR(100) DEFAULT NULL,
    family VARCHAR(100) DEFAULT NULL,
    genus VARCHAR(100) DEFAULT NULL,
	species VARCHAR(100),
	strain VARCHAR(100),
    PRIMARY KEY (taxonId),
    UNIQUE (species, strain)
);

CREATE TABLE IF NOT EXISTS Media (
    mediaId INT AUTO_INCREMENT,
    mediaName VARCHAR(20),
    mediaFile VARCHAR(100),
    PRIMARY KEY (mediaId),
    UNIQUE (mediaName)
);

CREATE TABLE IF NOT EXISTS Metabolites (
    cheb_id VARCHAR(255), 
    metabo_name VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (cheb_id)
);

CREATE TABLE IF NOT EXISTS MetaboliteSynonym (
    syn_id INT AUTO_INCREMENT PRIMARY KEY, 
    synonym_value VARCHAR(255) DEFAULT NULL,
    cheb_id VARCHAR(255),
    FOREIGN KEY (cheb_id) REFERENCES Metabolites(cheb_id)
);

CREATE TABLE IF NOT EXISTS BiologicalReplicate (
	biologicalReplicateId INT AUTO_INCREMENT,
    biologicalReplicateName VARCHAR(20),
    cheb_id VARCHAR(255), 
    studyId INT NOT NULL,
    precultivationId INT,
    reactorId INT NOT NULL,
    plateId INT DEFAULT NULL,
    platePosition VARCHAR(4) DEFAULT NULL,
    mediaId INT NOT NULL,
    blank BOOLEAN DEFAULT FALSE,
    inoculumConcentration FLOAT(7,2) DEFAULT 0,
	inoculumVolume FLOAT(7,2) DEFAULT 0,
    initialPh FLOAT(7,2) DEFAULT NULL,
    initialTemperature FLOAT(7,2) DEFAULT NULL,
    carbonSource VARCHAR(100) DEFAULT NULL,
    antibiotic VARCHAR(100) DEFAULT NULL,
    biologicalReplicateDescription TEXT,
    PRIMARY KEY (biologicalReplicateId),
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (precultivationId) REFERENCES Precultivation (precultivationId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (reactorId) REFERENCES Reactor (reactorId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (mediaId) REFERENCES Media (mediaId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (cheb_id) REFERENCES Metabolites (cheb_id) ON UPDATE CASCADE ON DELETE CASCADE
    ##UNIQUE (biologicalReplicateName, studyId, reactorId, plateId, plateColumn, plateRow, mediaId, blank, inoculumConcentration, inoculumVolume, initialPh, initialTemperature, carbonSource, antibiotic)
);

CREATE TABLE IF NOT EXISTS Perturbation (
	perturbationId VARCHAR(15),
    biologicalReplicateId INT NOT NULL,
    plateId INT DEFAULT NULL,
    platePosition VARCHAR(4) DEFAULT NULL,
    property VARCHAR(20),
    newValue VARCHAR(20),
    startTime INT,
    endTime INT DEFAULT NULL,
    perturbationDescription TEXT,
    PRIMARY KEY (perturbationId),
    FOREIGN KEY (biologicalReplicateId) REFERENCES BiologicalReplicate (biologicalReplicateId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS TechnicalReplicate (
	technicalReplicateId VARCHAR(15),
    biologicalReplicateId INT,
    perturbationId VARCHAR(15) DEFAULT NULL,
    abundanceFile VARCHAR(100) DEFAULT NULL,
    metabolitesFile VARCHAR(100) DEFAULT NULL,
    phFile VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (technicalReplicateId),
    FOREIGN KEY (biologicalReplicateId) REFERENCES BiologicalReplicate (biologicalReplicateId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (perturbationId) REFERENCES Perturbation (perturbationId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS BacteriaCommunity (
    bacteriaId INT,
    biologicalReplicateId INT,
    PRIMARY KEY (bacteriaId, biologicalReplicateId),
    FOREIGN KEY (bacteriaId) REFERENCES Bacteria (bacteriaId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (biologicalReplicateId) REFERENCES BiologicalReplicate (biologicalReplicateId) ON UPDATE CASCADE ON DELETE CASCADE
);



