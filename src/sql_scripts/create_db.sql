DROP DATABASE BacterialGrowth;
CREATE DATABASE BacterialGrowth;
USE BacterialGrowth;

CREATE TABLE IF NOT EXISTS Project (
	projectId VARCHAR(100),
    projectName VARCHAR(100) DEFAULT NULL, 
    projectDescription TEXT DEFAULT NULL,
    projectUniqueID VARCHAR(100),
    PRIMARY KEY (projectId),
    UNIQUE (projectName)
);

CREATE TABLE IF NOT EXISTS Study (
	studyId VARCHAR(100),
    projectUniqueID VARCHAR(100),
    studyName VARCHAR(100) DEFAULT NULL, 
    studyDescription TEXT DEFAULT NULL,
    studyURL VARCHAR(100) DEFAULT NULL,
    studyUniqueID VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (studyId),
    UNIQUE (studyDescription(255))
);

CREATE TABLE IF NOT EXISTS Experiments (
    studyId VARCHAR(100),
	experimentUniqueId INT AUTO_INCREMENT,
    experimentId VARCHAR(20), 
    experimentDescription TEXT,
    cultivationMode  VARCHAR(50),
    controlDescription TEXT,
    PRIMARY KEY (experimentUniqueId),
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Compartments (
    compartmentUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    studyId VARCHAR(100),
    compartmentId VARCHAR(50) NOT NULL,
    volume FLOAT(7,2) DEFAULT 0,
    pressure FLOAT(7,2) DEFAULT 0,
    stirring_speed FLOAT(7,2) DEFAULT 0,
    stirring_mode VARCHAR(50) DEFAULT '',
    O2 FLOAT(7,2) DEFAULT 0,
    CO2 FLOAT(7,2) DEFAULT 0,
    H2  FLOAT(7,2) DEFAULT 0,
    N2 FLOAT(7,2) DEFAULT 0,
    inoculumConcentration FLOAT(10,2) DEFAULT 0,
	inoculumVolume FLOAT(7,2) DEFAULT 0,
    initialPh FLOAT(7,2) DEFAULT 0,
    initialTemperature FLOAT(7,2) DEFAULT 0,
    carbonSource BOOLEAN DEFAULT FALSE,
    mediaNames VARCHAR(100) NOT NULL,
    mediaLink VARCHAR(100) NOT NULL,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Strains (
    studyId VARCHAR(100),
    memberId VARCHAR(50),
    defined BOOLEAN DEFAULT FALSE,
    memberName TEXT,
    strainId INT AUTO_INCREMENT PRIMARY KEY,
    NCBId INT,
    descriptionMember TEXT,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community (
    studyId VARCHAR(100),
    comunityUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    comunityId VARCHAR(50) NOT NULL,
    strainId INT,
    UNIQUE(comunityId,strainId),
    FOREIGN KEY (strainId) REFERENCES Strains (strainId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE

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


CREATE TABLE CompartmentsPerExperiment (
    studyId VARCHAR(100),
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    compartmentUniqueId INT,
    compartmentId VARCHAR(100) NOT NULL,
    comunityUniqueId INT,
    comunityId VARCHAR(100) NOT NULL,
    PRIMARY KEY (experimentUniqueId, compartmentUniqueId,comunityUniqueId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (compartmentUniqueId) REFERENCES Compartments(compartmentUniqueId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (comunityUniqueId) REFERENCES Community(comunityUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE TechniquesPerExperiment (
    studyId VARCHAR(100),
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    technique VARCHAR(100),
    techniqueUnit VARCHAR(100),
    PRIMARY KEY (experimentUniqueId, technique, techniqueUnit),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE BioReplicatesPerExperiment (
    studyId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    bioreplicateId VARCHAR(100),
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    controls BOOLEAN DEFAULT FALSE,
    OD BOOLEAN DEFAULT FALSE,
    OD_std BOOLEAN DEFAULT FALSE,
    Plate_counts BOOLEAN DEFAULT FALSE,
    Plate_counts_std BOOLEAN DEFAULT FALSE,
    pH BOOLEAN DEFAULT FALSE,
    UNIQUE (studyId, bioreplicateId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId)  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE BioReplicatesMetadata (
    studyId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(100),
    biosampleLink TEXT,
    bioreplicateDescrition TEXT,
    PRIMARY KEY (bioreplicateId),
    UNIQUE (studyId, bioreplicateUniqueId),
    FOREIGN KEY (bioreplicateUniqueId) REFERENCES BioReplicatesPerExperiment (bioreplicateUniqueId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId)  ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Perturbation (
    studyId VARCHAR(100),
    perturbationUniqueid INT AUTO_INCREMENT,
    perturbationId VARCHAR(100) NOT NULL,
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    OLDCompartmentId VARCHAR(100),
    OLDComunityId VARCHAR(100),
    NEWCompartmentId VARCHAR(100),
    NEWComunityId VARCHAR(100),
    perturbationDescription TEXT,
    perturbationMinimumValue DECIMAL(10, 2),
    perturbationMaximumValue DECIMAL(10, 2),
    perturbationStartTime TIME,
    perturbationEndTime TIME,
    PRIMARY KEY (perturbationUniqueid),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS MetabolitePerExperiment (
    studyId VARCHAR(100),
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(100),
    metabo_name VARCHAR(255) DEFAULT NULL,
    cheb_id VARCHAR(255),
    PRIMARY KEY  (experimentId,bioreplicateId, cheb_id),
    FOREIGN KEY (cheb_id) REFERENCES Metabolites(cheb_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Abundances (
    studyId VARCHAR(100),
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(100),
    strainId INT,
    memberId VARCHAR(255),
    PRIMARY KEY  (experimentId,bioreplicateId, memberId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FC_Counts (
    studyId VARCHAR(100),
    experimentUniqueId INT,
    experimentId VARCHAR(100) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(100),
    strainId INT,
    memberId VARCHAR(255),
    PRIMARY KEY  (experimentId,bioreplicateId, memberId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);




