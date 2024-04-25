DROP DATABASE BacterialGrowth;
CREATE DATABASE BacterialGrowth;
USE BacterialGrowth;

CREATE TABLE IF NOT EXISTS Study (
	studyId INT AUTO_INCREMENT,
    studyName VARCHAR(100) DEFAULT NULL, 
    studyDescription TEXT DEFAULT NULL,
    studyURL VARCHAR(100) DEFAULT NULL,
    studyUniqueID VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (studyId),
    UNIQUE (studyName)
);

CREATE TABLE IF NOT EXISTS Events (
	EventUniqueId INT AUTO_INCREMENT,
    EventId VARCHAR(20), 
    studyId INT NOT NULL,
    blank BOOLEAN DEFAULT FALSE,
    EventDescription TEXT,
    PRIMARY KEY (EventUniqueId),
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Compartments (
    compartmentUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    compartmentId VARCHAR(50) NOT NULL,
    volume FLOAT(7,2) DEFAULT 0,
    pressure FLOAT(7,2) DEFAULT 0,
    stirring_speed FLOAT(7,2) DEFAULT 0,
    stirring_mode VARCHAR(50) DEFAULT '',
    O2 FLOAT(7,2) DEFAULT 0,
    CO2 FLOAT(7,2) DEFAULT 0,
    H2  FLOAT(7,2) DEFAULT 0,
    N2 FLOAT(7,2) DEFAULT 0,
    inoculumConcentration FLOAT(7,2) DEFAULT 0,
	inoculumVolume FLOAT(7,2) DEFAULT 0,
    initialPh FLOAT(7,2) DEFAULT NULL,
    initialTemperature FLOAT(7,2) DEFAULT NULL,
    carbonSource BOOLEAN DEFAULT FALSE,
    mediaName VARCHAR(20) NOT NULL,
    mediaLink VARCHAR(100) NOT NULL
);

CREATE TABLE Strains (
    strainId INT AUTO_INCREMENT PRIMARY KEY,
    genus VARCHAR(50),
    species VARCHAR(50),
    NCBISpeciesId INT,
    strain VARCHAR(50),
    NCBIStrainId INT,
    UNIQUE(genus,species,NCBISpeciesId,strain,NCBIStrainId)
);

CREATE TABLE IF NOT EXISTS Comunity (
    comunityUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    comunityId VARCHAR(50) NOT NULL,
    strainId INT,
    UNIQUE(comunityId,strainId),
    FOREIGN KEY (strainId) REFERENCES Strains (strainId)

);

CREATE TABLE IF NOT EXISTS Metabolites (
    cheb_id VARCHAR(255), 
    metabo_name VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (cheb_id)
);

CREATE TABLE IF NOT EXISTS Taxa (
    tax_id VARCHAR(255), 
    tax_names VARCHAR(255),
    PRIMARY KEY (tax_id)
);

/*
CREATE TABLE IF NOT EXISTS MetaboliteSynonym (
    syn_id INT AUTO_INCREMENT PRIMARY KEY, 
    synonym_value VARCHAR(255) DEFAULT NULL,
    cheb_id VARCHAR(255),
    FOREIGN KEY (cheb_id) REFERENCES Metabolites(cheb_id)
);

*/


CREATE TABLE CompartmentsPerEvent (
    EventUniqueId INT,
    EventId VARCHAR(20) NOT NULL,
    compartmentUniqueId INT,
    compartmentId VARCHAR(50) NOT NULL,
    comunityUniqueId INT,
    comunityId VARCHAR(50) NOT NULL,
    PRIMARY KEY (EventUniqueId, compartmentUniqueId),
    FOREIGN KEY (EventUniqueId) REFERENCES Events(EventUniqueId),
    FOREIGN KEY (compartmentUniqueId) REFERENCES Compartments(compartmentUniqueId),
    FOREIGN KEY (comunityUniqueId) REFERENCES Comunity(comunityUniqueId)
);


CREATE TABLE TechniquesPerEvent (
    EventUniqueId INT,
    EventId VARCHAR(20) NOT NULL,
    technique VARCHAR(20),
    techniqueUnit VARCHAR(20),
    PRIMARY KEY (EventUniqueId, technique, techniqueUnit),
    FOREIGN KEY (EventUniqueId) REFERENCES Events(EventUniqueId)
);

CREATE TABLE BioReplicatesPerEvent (
    bioreplicateUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    bioreplicateId VARCHAR(20),
    EventUniqueId INT,
    EventId VARCHAR(20) NOT NULL,
    plateNumber INT DEFAULT NULL,
    platePosition VARCHAR(4) DEFAULT NULL,
    OD BOOLEAN DEFAULT FALSE,
    OD_std BOOLEAN DEFAULT FALSE,
    FC BOOLEAN DEFAULT FALSE,
    FC_std BOOLEAN DEFAULT FALSE,
    Plate_counts BOOLEAN DEFAULT FALSE,
    Plate_counts_std BOOLEAN DEFAULT FALSE,
    pH BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (EventUniqueId) REFERENCES Events(EventUniqueId)
);


CREATE TABLE IF NOT EXISTS Perturbation (
    perturbationUniqueid INT AUTO_INCREMENT,
    perturbationId VARCHAR(15),
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(20) NOT NULL,
    OLDCompartmentId VARCHAR(20),
    OLDComunityId VARCHAR(20),
    NEWCompartmentId VARCHAR(20),
    NEWComunityId VARCHAR(20),
    perturbationDescription VARCHAR(255),
    perturbationMinimumValue DECIMAL(10, 2),
    perturbationMaximumValue DECIMAL(10, 2),
    perturbationStartTime TIME,
    perturbationEndTime TIME,
    perturbationFilesDirectory VARCHAR(255),
    PRIMARY KEY (perturbationUniqueid),
    FOREIGN KEY (bioreplicateUniqueId) REFERENCES BioReplicatesPerEvent(bioreplicateUniqueId)
);


CREATE TABLE IF NOT EXISTS MetabolitePerEvent (
    EventUniqueId INT,
    EventId VARCHAR(20) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(20),
    metabo_name VARCHAR(255) DEFAULT NULL,
    cheb_id VARCHAR(255),
    PRIMARY KEY  (bioreplicateId, cheb_id),
    FOREIGN KEY (cheb_id) REFERENCES Metabolites(cheb_id),
    FOREIGN KEY (EventUniqueId) REFERENCES Events(EventUniqueId)
);

CREATE TABLE IF NOT EXISTS Abundances (
    EventUniqueId INT,
    EventId VARCHAR(20) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(20),
    strainId INT,
    memberId VARCHAR(255),
    PRIMARY KEY  (bioreplicateId, memberId),
    FOREIGN KEY (EventUniqueId) REFERENCES Events(EventUniqueId),
    FOREIGN KEY (strainId) REFERENCES Strains (strainId)
);




