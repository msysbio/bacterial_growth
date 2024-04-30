DROP DATABASE BacterialGrowth;
CREATE DATABASE BacterialGrowth;
USE BacterialGrowth;

CREATE TABLE IF NOT EXISTS Project (
	projectId INT AUTO_INCREMENT,
    projectName VARCHAR(100) DEFAULT NULL, 
    projectDescription TEXT DEFAULT NULL,
    projectUniqueID VARCHAR(100),
    PRIMARY KEY (projectId),
    UNIQUE (projectName)
);

CREATE TABLE IF NOT EXISTS Study (
	studyId INT AUTO_INCREMENT,
    projectUniqueID VARCHAR(100),
    studyName VARCHAR(100) DEFAULT NULL, 
    studyDescription TEXT DEFAULT NULL,
    studyURL VARCHAR(100) DEFAULT NULL,
    studyUniqueID VARCHAR(100) DEFAULT NULL,
    PRIMARY KEY (studyId),
    UNIQUE (studyName)
);

CREATE TABLE IF NOT EXISTS Experiments (
	experimentUniqueId INT AUTO_INCREMENT,
    experimentId VARCHAR(20), 
    studyId INT,
    experimentDescription TEXT,
    cultivationMode  VARCHAR(50),
    controlDescription TEXT,
    PRIMARY KEY (experimentUniqueId),
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Compartments (
    studyId INT,
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
    mediaLink VARCHAR(100) NOT NULL,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Strains (
    studyId INT,
    memberId VARCHAR(50),
    defined BOOLEAN DEFAULT FALSE,
    memberName VARCHAR(50),
    strainId INT AUTO_INCREMENT PRIMARY KEY,
    NCBId INT,
    descriptionMember TEXT,
    FOREIGN KEY (studyId) REFERENCES Study (studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community (
    studyId INT,
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
    experimentUniqueId INT,
    experimentId VARCHAR(20) NOT NULL,
    compartmentUniqueId INT,
    compartmentId VARCHAR(50) NOT NULL,
    comunityUniqueId INT,
    comunityId VARCHAR(50) NOT NULL,
    PRIMARY KEY (experimentUniqueId, compartmentUniqueId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (compartmentUniqueId) REFERENCES Compartments(compartmentUniqueId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (comunityUniqueId) REFERENCES Community(comunityUniqueId) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE TechniquesPerExperiment (
    experimentUniqueId INT,
    experimentId VARCHAR(20) NOT NULL,
    technique VARCHAR(20),
    techniqueUnit VARCHAR(20),
    PRIMARY KEY (experimentUniqueId, technique, techniqueUnit),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE BioReplicatesPerExperiment (
    studyId INT NOT NULL,
    bioreplicateUniqueId INT AUTO_INCREMENT PRIMARY KEY,
    bioreplicateId VARCHAR(50),
    experimentUniqueId INT,
    experimentId VARCHAR(20) NOT NULL,
    controls BOOLEAN DEFAULT FALSE,
    OD BOOLEAN DEFAULT FALSE,
    OD_std BOOLEAN DEFAULT FALSE,
    FC BOOLEAN DEFAULT FALSE,
    FC_std BOOLEAN DEFAULT FALSE,
    Plate_counts BOOLEAN DEFAULT FALSE,
    Plate_counts_std BOOLEAN DEFAULT FALSE,
    pH BOOLEAN DEFAULT FALSE,
    UNIQUE (studyId, bioreplicateId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (studyId) REFERENCES Study (studyId)  ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Perturbation (
    studyId INT,
    perturbationUniqueid INT AUTO_INCREMENT,
    perturbationId VARCHAR(20) NOT NULL,
    experimentUniqueId INT,
    experimentId VARCHAR(20) NOT NULL,
    OLDCompartmentId VARCHAR(20),
    OLDComunityId VARCHAR(20),
    NEWCompartmentId VARCHAR(20),
    NEWComunityId VARCHAR(20),
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
    experimentUniqueId INT,
    experimentId VARCHAR(20) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(20),
    metabo_name VARCHAR(255) DEFAULT NULL,
    cheb_id VARCHAR(255),
    PRIMARY KEY  (experimentId,bioreplicateId, cheb_id),
    FOREIGN KEY (cheb_id) REFERENCES Metabolites(cheb_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Abundances (
    experimentUniqueId INT,
    experimentId VARCHAR(20) NOT NULL,
    bioreplicateUniqueId INT,
    bioreplicateId VARCHAR(20),
    strainId INT,
    memberId VARCHAR(255),
    PRIMARY KEY  (bioreplicateId, memberId),
    FOREIGN KEY (experimentUniqueId) REFERENCES Experiments(experimentUniqueId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON UPDATE CASCADE ON DELETE CASCADE
);



