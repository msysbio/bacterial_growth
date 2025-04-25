-- MySQL dump 10.13  Distrib 8.4.0, for Linux (x86_64)
--
-- Host: localhost    Database: BacterialGrowth
-- ------------------------------------------------------
-- Server version	8.4.4

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Abundances`
--

DROP TABLE IF EXISTS Abundances;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Abundances (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int NOT NULL,
  experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  bioreplicateUniqueId int NOT NULL,
  bioreplicateId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  strainId int DEFAULT NULL,
  memberId varchar(255) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (experimentUniqueId,bioreplicateUniqueId,memberId),
  KEY fk_1 (experimentUniqueId),
  KEY fk_2 (strainId),
  KEY fk_3 (studyId),
  CONSTRAINT Abundances_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Abundances_fk_2 FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Abundances_fk_3 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BioReplicatesMetadata`
--

DROP TABLE IF EXISTS BioReplicatesMetadata;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE BioReplicatesMetadata (
  studyId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  bioreplicateUniqueId int NOT NULL,
  bioreplicateId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  biosampleLink text COLLATE utf8mb4_bin,
  bioreplicateDescrition text COLLATE utf8mb4_bin,
  PRIMARY KEY (studyId,bioreplicateUniqueId),
  UNIQUE KEY studyId (studyId,bioreplicateUniqueId),
  KEY fk_1 (bioreplicateUniqueId),
  CONSTRAINT BioReplicatesMetadata_fk_1 FOREIGN KEY (bioreplicateUniqueId) REFERENCES BioReplicatesPerExperiment (bioreplicateUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT BioReplicatesMetadata_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `BioReplicatesPerExperiment`
--

DROP TABLE IF EXISTS BioReplicatesPerExperiment;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE BioReplicatesPerExperiment (
  studyId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  bioreplicateUniqueId int NOT NULL AUTO_INCREMENT,
  bioreplicateId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int DEFAULT NULL,
  experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  controls tinyint(1) DEFAULT '0',
  OD tinyint(1) DEFAULT '0',
  OD_std tinyint(1) DEFAULT '0',
  Plate_counts tinyint(1) DEFAULT '0',
  Plate_counts_std tinyint(1) DEFAULT '0',
  pH tinyint(1) DEFAULT '0',
  PRIMARY KEY (bioreplicateUniqueId),
  UNIQUE KEY studyId (studyId,bioreplicateId),
  KEY fk_1 (experimentUniqueId),
  CONSTRAINT BioReplicatesPerExperiment_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT BioReplicatesPerExperiment_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CalculationTechniques`
--

DROP TABLE IF EXISTS CalculationTechniques;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE CalculationTechniques (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  studyUniqueId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  jobUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `error` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY CalculationTechniques_studyUniqueId (studyUniqueId),
  CONSTRAINT CalculationTechniques_studyUniqueId FOREIGN KEY (studyUniqueId) REFERENCES Study (studyUniqueID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Calculations`
--

DROP TABLE IF EXISTS Calculations;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Calculations (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  subjectId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  subjectType varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  calculationTechniqueId int NOT NULL,
  measurementTechniqueId int NOT NULL,
  coefficients json DEFAULT (json_object()),
  state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `error` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  calculatedAt datetime DEFAULT NULL,
  PRIMARY KEY (id),
  KEY Calculations_measurementTechniqueId (measurementTechniqueId),
  KEY Calculations_calculationTechniqueId (calculationTechniqueId),
  CONSTRAINT Calculations_calculationTechniqueId FOREIGN KEY (calculationTechniqueId) REFERENCES CalculationTechniques (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Calculations_measurementTechniqueId FOREIGN KEY (measurementTechniqueId) REFERENCES MeasurementTechniques (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Community`
--

DROP TABLE IF EXISTS Community;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Community (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  communityUniqueId int NOT NULL AUTO_INCREMENT,
  communityId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  strainId int DEFAULT NULL,
  PRIMARY KEY (communityUniqueId),
  UNIQUE KEY communityId (communityId,strainId),
  KEY fk_1 (strainId),
  KEY fk_2 (studyId),
  CONSTRAINT Community_fk_1 FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Community_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Compartments`
--

DROP TABLE IF EXISTS Compartments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Compartments (
  compartmentUniqueId int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  compartmentId varchar(50) COLLATE utf8mb4_bin NOT NULL,
  volume float(7,2) DEFAULT '0.00',
  pressure float(7,2) DEFAULT '0.00',
  stirring_speed float(7,2) DEFAULT '0.00',
  stirring_mode varchar(50) COLLATE utf8mb4_bin DEFAULT '',
  O2 float(7,2) DEFAULT '0.00',
  CO2 float(7,2) DEFAULT '0.00',
  H2 float(7,2) DEFAULT '0.00',
  N2 float(7,2) DEFAULT '0.00',
  inoculumConcentration float(10,2) DEFAULT '0.00',
  inoculumVolume float(7,2) DEFAULT '0.00',
  initialPh float(7,2) DEFAULT '0.00',
  initialTemperature float(7,2) DEFAULT '0.00',
  carbonSource tinyint(1) DEFAULT '0',
  mediaNames varchar(100) COLLATE utf8mb4_bin NOT NULL,
  mediaLink varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (compartmentUniqueId),
  KEY fk_1 (studyId),
  CONSTRAINT Compartments_fk_1 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CompartmentsPerExperiment`
--

DROP TABLE IF EXISTS CompartmentsPerExperiment;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE CompartmentsPerExperiment (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int NOT NULL,
  experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  compartmentUniqueId int NOT NULL,
  compartmentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  communityUniqueId int NOT NULL,
  communityId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (experimentUniqueId,compartmentUniqueId,communityUniqueId),
  KEY fk_2 (compartmentUniqueId),
  KEY fk_3 (communityUniqueId),
  KEY fk_4 (studyId),
  CONSTRAINT CompartmentsPerExperiment_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CompartmentsPerExperiment_fk_2 FOREIGN KEY (compartmentUniqueId) REFERENCES Compartments (compartmentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CompartmentsPerExperiment_fk_3 FOREIGN KEY (communityUniqueId) REFERENCES Community (communityUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CompartmentsPerExperiment_fk_4 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ExcelFiles`
--

DROP TABLE IF EXISTS ExcelFiles;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ExcelFiles (
  id int NOT NULL AUTO_INCREMENT,
  filename varchar(255) DEFAULT NULL,
  size int NOT NULL,
  content longblob NOT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Experiments`
--

DROP TABLE IF EXISTS Experiments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Experiments (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int NOT NULL AUTO_INCREMENT,
  experimentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentDescription text COLLATE utf8mb4_bin,
  cultivationMode varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  controlDescription text COLLATE utf8mb4_bin,
  PRIMARY KEY (experimentUniqueId),
  KEY fk_1 (studyId),
  CONSTRAINT Experiments_fk_1 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `FC_Counts`
--

DROP TABLE IF EXISTS FC_Counts;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE FC_Counts (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int DEFAULT NULL,
  experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  bioreplicateUniqueId int DEFAULT NULL,
  bioreplicateId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  strainId int DEFAULT NULL,
  memberId varchar(255) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (experimentId,bioreplicateId,memberId),
  KEY fk_1 (experimentUniqueId),
  KEY fk_2 (strainId),
  KEY fk_3 (studyId),
  CONSTRAINT FC_Counts_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT FC_Counts_fk_2 FOREIGN KEY (strainId) REFERENCES Strains (strainId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT FC_Counts_fk_3 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MeasurementTechniques`
--

DROP TABLE IF EXISTS MeasurementTechniques;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MeasurementTechniques (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  subjectType varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  units varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `description` text,
  includeStd tinyint(1) NOT NULL DEFAULT '0',
  studyUniqueId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  metaboliteIds json DEFAULT (json_array()),
  strainIds json DEFAULT (json_array()),
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY MeasurementTechniques_studyUniqueId (studyUniqueId),
  CONSTRAINT MeasurementTechniques_studyUniqueId FOREIGN KEY (studyUniqueId) REFERENCES Study (studyUniqueID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Measurements`
--

DROP TABLE IF EXISTS Measurements;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Measurements (
  id int NOT NULL AUTO_INCREMENT,
  bioreplicateUniqueId int NOT NULL,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  position varchar(100) NOT NULL,
  timeInSeconds int NOT NULL,
  pH varchar(100) DEFAULT NULL,
  unit varchar(100) DEFAULT NULL,
  technique varchar(100) DEFAULT NULL,
  `value` decimal(20,3) DEFAULT NULL,
  std decimal(20,3) DEFAULT NULL,
  subjectType varchar(100) NOT NULL,
  subjectId varchar(100) NOT NULL,
  techniqueId int DEFAULT NULL,
  PRIMARY KEY (id),
  KEY bioreplicateUniqueId (bioreplicateUniqueId),
  KEY studyId (studyId),
  CONSTRAINT bioreplicateUniqueId FOREIGN KEY (bioreplicateUniqueId) REFERENCES BioReplicatesPerExperiment (bioreplicateUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT studyId FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MetabolitePerExperiment`
--

DROP TABLE IF EXISTS MetabolitePerExperiment;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MetabolitePerExperiment (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int NOT NULL,
  bioreplicateUniqueId int NOT NULL,
  chebi_id varchar(255) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (experimentUniqueId,bioreplicateUniqueId,chebi_id),
  KEY fk_1 (chebi_id),
  KEY fk_2 (experimentUniqueId),
  KEY fk_3 (studyId),
  CONSTRAINT MetabolitePerExperiment_fk_1 FOREIGN KEY (chebi_id) REFERENCES Metabolites (chebi_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MetabolitePerExperiment_fk_2 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MetabolitePerExperiment_fk_3 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Metabolites`
--

DROP TABLE IF EXISTS Metabolites;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Metabolites (
  chebi_id varchar(512) COLLATE utf8mb4_bin NOT NULL,
  metabo_name varchar(512) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (chebi_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MigrationVersions`
--

DROP TABLE IF EXISTS MigrationVersions;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MigrationVersions (
  id bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  migratedAt datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Perturbation`
--

DROP TABLE IF EXISTS Perturbation;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Perturbation (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  perturbationUniqueid int NOT NULL AUTO_INCREMENT,
  perturbationId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  experimentUniqueId int DEFAULT NULL,
  experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  OLDCompartmentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  OLDComunityId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  NEWCompartmentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  NEWComunityId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  perturbationDescription text COLLATE utf8mb4_bin,
  perturbationMinimumValue decimal(10,2) DEFAULT NULL,
  perturbationMaximumValue decimal(10,2) DEFAULT NULL,
  perturbationStartTime time DEFAULT NULL,
  perturbationEndTime time DEFAULT NULL,
  PRIMARY KEY (perturbationUniqueid),
  KEY fk_1 (experimentUniqueId),
  KEY fk_2 (studyId),
  CONSTRAINT Perturbation_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT Perturbation_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Project`
--

DROP TABLE IF EXISTS Project;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Project (
  projectId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  projectName varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  projectDescription text COLLATE utf8mb4_bin,
  projectUniqueID varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (projectId),
  UNIQUE KEY projectName (projectName),
  UNIQUE KEY projectUniqueID (projectUniqueID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ProjectUsers`
--

DROP TABLE IF EXISTS ProjectUsers;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ProjectUsers (
  id int NOT NULL AUTO_INCREMENT,
  projectUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY projectUniqueID (projectUniqueID),
  CONSTRAINT projectUniqueID FOREIGN KEY (projectUniqueID) REFERENCES Project (projectUniqueID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Strains`
--

DROP TABLE IF EXISTS Strains;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Strains (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  memberId varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  defined tinyint(1) DEFAULT '0',
  memberName text COLLATE utf8mb4_bin,
  strainId int NOT NULL AUTO_INCREMENT,
  NCBId int DEFAULT NULL,
  descriptionMember text COLLATE utf8mb4_bin,
  assemblyGenBankId varchar(50) COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (strainId),
  KEY fk_1 (studyId),
  CONSTRAINT Strains_fk_1 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Study`
--

DROP TABLE IF EXISTS Study;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Study (
  studyId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  projectUniqueID varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  studyName varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  studyDescription text COLLATE utf8mb4_bin,
  studyURL varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  studyUniqueID varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  timeUnits varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  publishableAt datetime DEFAULT NULL,
  publishedAt datetime DEFAULT NULL,
  embargoExpiresAt datetime DEFAULT NULL,
  PRIMARY KEY (studyId),
  UNIQUE KEY studyUniqueID (studyUniqueID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `StudyUsers`
--

DROP TABLE IF EXISTS StudyUsers;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE StudyUsers (
  id int NOT NULL AUTO_INCREMENT,
  studyUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY studyUniqueID (studyUniqueID),
  CONSTRAINT studyUniqueID FOREIGN KEY (studyUniqueID) REFERENCES Study (studyUniqueID) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Submissions`
--

DROP TABLE IF EXISTS Submissions;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Submissions (
  id int NOT NULL AUTO_INCREMENT,
  projectUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyDesign json DEFAULT (json_object()),
  studyFileId int DEFAULT NULL,
  dataFileId int DEFAULT NULL,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Taxa`
--

DROP TABLE IF EXISTS Taxa;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Taxa (
  tax_id varchar(512) COLLATE utf8mb4_bin NOT NULL,
  tax_names varchar(512) COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (tax_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TechniquesPerExperiment`
--

DROP TABLE IF EXISTS TechniquesPerExperiment;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE TechniquesPerExperiment (
  studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
  experimentUniqueId int NOT NULL,
  experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
  technique varchar(100) COLLATE utf8mb4_bin NOT NULL,
  techniqueUnit varchar(100) COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (experimentUniqueId,technique,techniqueUnit),
  KEY fk_2 (studyId),
  CONSTRAINT TechniquesPerExperiment_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (experimentUniqueId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT TechniquesPerExperiment_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

INSERT INTO MigrationVersions VALUES
(1,'2024_11_11_160324_initial_schema','2025-04-25 09:06:52'),
(2,'2024_11_11_164726_remove_unique_study_description_index','2025-04-25 09:06:52'),
(3,'2024_11_21_115349_allow_null_medialink','2025-04-25 09:06:52'),
(4,'2024_11_21_120444_fix_unique_primary_keys','2025-04-25 09:06:53'),
(5,'2025_01_30_152951_fix_bioreplicates_metadata_unique_id','2025-04-25 09:06:53'),
(6,'2025_02_04_134239_rename-chebi-id','2025-04-25 09:06:53'),
(7,'2025_02_05_134203_make-project-and-study-uuids-unique','2025-04-25 09:06:53'),
(8,'2025_02_12_170210_add-assembly-id-to-strains','2025-04-25 09:06:53'),
(9,'2025_02_13_114748_increase_experiment_id_size','2025-04-25 09:06:53'),
(10,'2025_02_13_120609_rename_comunity_to_community','2025-04-25 09:06:53'),
(11,'2025_02_13_121409_rename_comunity_to_community_2','2025-04-25 09:06:53'),
(12,'2025_02_13_163206_create_measurements','2025-04-25 09:06:53'),
(13,'2025_02_17_161750_remove_duplicated_columns_from_metabolite_per_experiment','2025-04-25 09:06:53'),
(14,'2025_03_11_113040_create_submissions_and_excel_files','2025-04-25 09:06:54'),
(15,'2025_03_21_112110_create_project_and_study_user_join_tables','2025-04-25 09:06:54'),
(16,'2025_03_25_133231_add_user_id_to_new_strains','2025-04-25 09:06:54'),
(17,'2025_03_28_181930_create_measurement_techniques','2025-04-25 09:06:54'),
(18,'2025_03_30_160720_add_technique_id_to_measurements','2025-04-25 09:06:54'),
(19,'2025_04_03_121425_add_time_units_to_study','2025-04-25 09:06:54'),
(20,'2025_04_03_125243_add_timestamps_to_study_and_project','2025-04-25 09:06:54'),
(21,'2025_04_15_112546_add_publishing_related_states_to_studies','2025-04-25 09:06:54'),
(24,'2025_04_24_095808_create_calculation_techniques','2025-04-25 10:19:28'),
(25,'2025_04_25_103658_create_calculations','2025-04-25 10:19:28');

