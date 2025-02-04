DROP DATABASE BacterialGrowthDiagram;
CREATE DATABASE BacterialGrowthDiagram;
USE BacterialGrowthDiagram;

CREATE TABLE IF NOT EXISTS Project (
    projectId VARCHAR(100) UNIQUE,
    projectPrivateId VARCHAR(100),
    projectName VARCHAR(100), 
    projectDescription TEXT,
    PRIMARY KEY (projectId)
);

CREATE TABLE IF NOT EXISTS Study (
    projectId VARCHAR(100),
	studyId VARCHAR(100),
    studyPrivateId VARCHAR(100),
    studyName VARCHAR(100), 
    studyDescription TEXT,
    studyURL VARCHAR(100),
    PRIMARY KEY (studyId),
    FOREIGN KEY (projectId) REFERENCES Project(projectId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Experiments (
    studyId VARCHAR(100),
	experimentId INT AUTO_INCREMENT,
    experimentName VARCHAR(20), 
    experimentDescription TEXT,
    cultivationMode  VARCHAR(50),
    controlDescription TEXT,
    PRIMARY KEY (experimentId),
    FOREIGN KEY (studyId) REFERENCES Study(studyId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS BiologicalReplicates (
    experimentId INT,
    bioreplicateId INT AUTO_INCREMENT PRIMARY KEY,
    bioreplicateName VARCHAR(50),
    controls BOOLEAN DEFAULT FALSE,
    OD BOOLEAN DEFAULT FALSE,
    OD_std BOOLEAN DEFAULT FALSE,
    Plate_counts BOOLEAN DEFAULT FALSE,
    Plate_counts_std BOOLEAN DEFAULT FALSE,
    FCCounts BOOLEAN DEFAULT FALSE,
    FCCounts_std BOOLEAN DEFAULT FALSE,
    16RNASeq BOOLEAN DEFAULT FALSE,
    16RNASeq_std BOOLEAN DEFAULT FALSE,
    pH BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (experimentId) REFERENCES Experiments(experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Compartments (
    experimentId INT,
    compartmentId INT AUTO_INCREMENT PRIMARY KEY,
    compartmentName VARCHAR(50) NOT NULL,
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
    FOREIGN KEY (experimentId) REFERENCES Experiments(experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Taxa (
    NCBId INT, 
    taxaNames VARCHAR(255),
    PRIMARY KEY (NCBId)
);


CREATE TABLE IF NOT EXISTS CommunityMembers (
    strainId INT AUTO_INCREMENT,
    strainName TEXT,
    defined BOOLEAN DEFAULT FALSE,
    NCBId INT,
    descriptionStain TEXT,
    PRIMARY KEY (strainId),
    FOREIGN KEY (NCBId) REFERENCES Taxa(NCBId) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Community (
    experimentId INT,
    comunityId INT AUTO_INCREMENT PRIMARY KEY,
    comunityName VARCHAR(50) NOT NULL,
    strainId INT,
    UNIQUE(comunityId),
    FOREIGN KEY (experimentId) REFERENCES Experiments(experimentId)  ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (strainId) REFERENCES CommunityMembers(strainId) ON UPDATE CASCADE ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS Metabolites (
    chebiId VARCHAR(255), 
    metaboliteName VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (chebiId)
);



CREATE TABLE IF NOT EXISTS BiologicalReplicatesMetadata (
    bioreplicateId INT,
    bioreplicateName VARCHAR(50),
    biosampleLink TEXT,
    bioreplicateDescrition TEXT,
    FOREIGN KEY (bioreplicateId) REFERENCES BiologicalReplicates(bioreplicateId)  ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Perturbation (
    experimentId INT,
    perturbationId INT AUTO_INCREMENT,
    OLDCompartmentId VARCHAR(20),
    OLDComunityId VARCHAR(20),
    NEWCompartmentId VARCHAR(20),
    NEWComunityId VARCHAR(20),
    perturbationDescription TEXT,
    perturbationMinimumValue DECIMAL(10, 2),
    perturbationMaximumValue DECIMAL(10, 2),
    perturbationStartTime TIME,
    perturbationEndTime TIME,
    PRIMARY KEY (perturbationId),
    FOREIGN KEY (experimentId) REFERENCES Experiments(experimentId) ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS MetabolitePerBiologicalReplicate (
    bioreplicateId INT,
    metaboliteName VARCHAR(255) DEFAULT NULL,
    chebiId VARCHAR(255),
    FOREIGN KEY (chebiId) REFERENCES Metabolites(chebiId) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (bioreplicateId) REFERENCES BiologicalReplicates (bioreplicateId) ON UPDATE CASCADE ON DELETE CASCADE
);
