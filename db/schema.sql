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
-- Table structure for table `Bioreplicates`
--

DROP TABLE IF EXISTS Bioreplicates;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Bioreplicates (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  experimentId int NOT NULL,
  biosampleUrl text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  position varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  isControl tinyint(1) NOT NULL DEFAULT '0',
  isBlank tinyint(1) NOT NULL DEFAULT '0',
  calculationType varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY studyId (studyId,`name`),
  KEY fk_1 (experimentId),
  CONSTRAINT BioReplicatesPerExperiment_fk_1 FOREIGN KEY (experimentId) REFERENCES Experiments (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT BioReplicatesPerExperiment_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Communities`
--

DROP TABLE IF EXISTS Communities;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Communities (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  strainIds json NOT NULL DEFAULT (json_array()),
  PRIMARY KEY (id),
  KEY fk_2 (studyId),
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
  id int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  volume decimal(7,2) DEFAULT NULL,
  pressure decimal(7,2) DEFAULT NULL,
  stirringSpeed float(7,2) DEFAULT NULL,
  stirringMode varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  O2 decimal(7,2) DEFAULT NULL,
  CO2 decimal(7,2) DEFAULT NULL,
  H2 decimal(7,2) DEFAULT NULL,
  N2 decimal(7,2) DEFAULT NULL,
  inoculumConcentration decimal(20,3) DEFAULT NULL,
  inoculumVolume decimal(7,2) DEFAULT NULL,
  initialPh decimal(7,2) DEFAULT NULL,
  initialTemperature decimal(7,2) DEFAULT NULL,
  carbonSource tinyint(1) DEFAULT '0',
  mediumName varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  mediumUrl varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
  KEY fk_1 (studyId),
  CONSTRAINT Compartments_fk_1 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
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
-- Table structure for table `ExperimentCompartments`
--

DROP TABLE IF EXISTS ExperimentCompartments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ExperimentCompartments (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  experimentId int NOT NULL,
  compartmentId int NOT NULL,
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id),
  KEY fk_2 (compartmentId),
  KEY fk_4 (studyId),
  KEY CompartmentsPerExperiment_fk_1 (experimentId),
  CONSTRAINT CompartmentsPerExperiment_fk_1 FOREIGN KEY (experimentId) REFERENCES Experiments (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CompartmentsPerExperiment_fk_2 FOREIGN KEY (compartmentId) REFERENCES Compartments (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT CompartmentsPerExperiment_fk_4 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Experiments`
--

DROP TABLE IF EXISTS Experiments;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Experiments (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  id int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  cultivationMode varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  communityId int DEFAULT NULL,
  PRIMARY KEY (id),
  KEY fk_1 (studyId),
  KEY Experiment_fk_1 (communityId),
  CONSTRAINT Experiment_fk_1 FOREIGN KEY (communityId) REFERENCES Communities (id) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT Experiments_fk_1 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MeasurementContexts`
--

DROP TABLE IF EXISTS MeasurementContexts;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE MeasurementContexts (
  id int NOT NULL AUTO_INCREMENT,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  bioreplicateId int NOT NULL,
  compartmentId int NOT NULL,
  techniqueId int DEFAULT NULL,
  subjectId varchar(100) NOT NULL,
  subjectType varchar(100) NOT NULL,
  calculationType varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
  KEY MeasurementContexts_fk_1 (bioreplicateId),
  KEY MeasurementContexts_fk_2 (compartmentId),
  KEY MeasurementContexts_fk_3 (techniqueId),
  KEY MeasurementContexts_fk_4 (studyId),
  CONSTRAINT MeasurementContexts_fk_1 FOREIGN KEY (bioreplicateId) REFERENCES Bioreplicates (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementContexts_fk_2 FOREIGN KEY (compartmentId) REFERENCES Compartments (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementContexts_fk_3 FOREIGN KEY (techniqueId) REFERENCES MeasurementTechniques (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MeasurementContexts_fk_4 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  timeInSeconds int NOT NULL,
  `value` decimal(20,3) DEFAULT NULL,
  std decimal(20,3) DEFAULT NULL,
  contextId int NOT NULL,
  PRIMARY KEY (id),
  KEY studyId (studyId),
  KEY Measurements_fk_1 (contextId),
  CONSTRAINT Measurements_fk_1 FOREIGN KEY (contextId) REFERENCES MeasurementContexts (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Metabolites`
--

DROP TABLE IF EXISTS Metabolites;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Metabolites (
  chebiId varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(512) COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  averageMass decimal(10,5) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY Metabolites_chebiId (chebiId)
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
-- Table structure for table `ModelingRequests`
--

DROP TABLE IF EXISTS ModelingRequests;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ModelingRequests (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  jobUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `error` text,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (id),
  KEY ModelingRequests_studyId (studyId),
  CONSTRAINT ModelingRequests_studyId FOREIGN KEY (studyId) REFERENCES Study (studyId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ModelingResults`
--

DROP TABLE IF EXISTS ModelingResults;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE ModelingResults (
  id int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  requestId int NOT NULL,
  coefficients json DEFAULT (json_object()),
  state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `error` text,
  createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  calculatedAt datetime DEFAULT NULL,
  fit json DEFAULT (json_object()),
  measurementContextId int NOT NULL,
  PRIMARY KEY (id),
  KEY Calculations_calculationTechniqueId (requestId),
  CONSTRAINT Calculations_calculationTechniqueId FOREIGN KEY (requestId) REFERENCES ModelingRequests (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Perturbations`
--

DROP TABLE IF EXISTS Perturbations;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE Perturbations (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  id int NOT NULL AUTO_INCREMENT,
  experimentId int NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  removedCompartmentId int DEFAULT NULL,
  addedCompartmentId int DEFAULT NULL,
  oldCommunityId int DEFAULT NULL,
  newCommunityId int DEFAULT NULL,
  startTimepoint int NOT NULL,
  PRIMARY KEY (id),
  KEY fk_1 (experimentId),
  KEY fk_2 (studyId),
  CONSTRAINT Perturbation_fk_1 FOREIGN KEY (experimentId) REFERENCES Experiments (id) ON DELETE CASCADE ON UPDATE CASCADE,
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
  projectId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  projectName varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  projectDescription text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  projectUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
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
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  defined tinyint(1) DEFAULT '0',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  NCBId int DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  assemblyGenBankId varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  userUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  PRIMARY KEY (id),
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
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  projectUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyName varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyDescription text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  studyURL varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  studyUniqueID varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
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
-- Table structure for table `StudyMetabolites`
--

DROP TABLE IF EXISTS StudyMetabolites;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE StudyMetabolites (
  studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  chebi_id varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  id bigint unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id),
  KEY fk_1 (chebi_id),
  KEY fk_3 (studyId),
  CONSTRAINT MetabolitePerExperiment_fk_1 FOREIGN KEY (chebi_id) REFERENCES Metabolites (chebiId) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT MetabolitePerExperiment_fk_3 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
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
  ncbiId varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `name` varchar(512) COLLATE utf8mb4_bin NOT NULL,
  id int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (id),
  UNIQUE KEY Taxa_ncbiId (ncbiId)
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
(1,'2024_11_11_160324_initial_schema','2025-04-30 12:54:12'),
(2,'2024_11_11_164726_remove_unique_study_description_index','2025-04-30 12:54:12'),
(3,'2024_11_21_115349_allow_null_medialink','2025-04-30 12:54:12'),
(4,'2024_11_21_120444_fix_unique_primary_keys','2025-04-30 12:54:13'),
(5,'2025_01_30_152951_fix_bioreplicates_metadata_unique_id','2025-04-30 12:54:13'),
(6,'2025_02_04_134239_rename-chebi-id','2025-04-30 12:54:13'),
(7,'2025_02_05_134203_make-project-and-study-uuids-unique','2025-04-30 12:54:13'),
(8,'2025_02_12_170210_add-assembly-id-to-strains','2025-04-30 12:54:13'),
(9,'2025_02_13_114748_increase_experiment_id_size','2025-04-30 12:54:13'),
(10,'2025_02_13_120609_rename_comunity_to_community','2025-04-30 12:54:13'),
(11,'2025_02_13_121409_rename_comunity_to_community_2','2025-04-30 12:54:14'),
(12,'2025_02_13_163206_create_measurements','2025-04-30 12:54:14'),
(13,'2025_02_17_161750_remove_duplicated_columns_from_metabolite_per_experiment','2025-04-30 12:54:14'),
(14,'2025_03_11_113040_create_submissions_and_excel_files','2025-04-30 12:54:14'),
(15,'2025_03_21_112110_create_project_and_study_user_join_tables','2025-04-30 12:54:14'),
(16,'2025_03_25_133231_add_user_id_to_new_strains','2025-04-30 12:54:14'),
(17,'2025_03_28_181930_create_measurement_techniques','2025-04-30 12:54:14'),
(18,'2025_03_30_160720_add_technique_id_to_measurements','2025-04-30 12:54:14'),
(19,'2025_04_03_121425_add_time_units_to_study','2025-04-30 12:54:14'),
(20,'2025_04_03_125243_add_timestamps_to_study_and_project','2025-04-30 12:54:14'),
(21,'2025_04_15_112546_add_publishing_related_states_to_studies','2025-04-30 12:54:15'),
(22,'2025_04_24_095808_create_calculation_techniques','2025-04-30 12:54:15'),
(23,'2025_04_25_103658_create_calculations','2025-04-30 12:54:15'),
(24,'2025_04_30_135012_fix_compartments_per_experiment_keys_and_columns','2025-04-30 12:54:15'),
(30,'2025_04_30_142205_fix_compartment_columns','2025-04-30 13:08:43'),
(33,'2025_05_01_172225_fix_community_columns','2025-05-01 15:32:33'),
(36,'2025_05_02_171609_fix_strain_columns','2025-05-02 15:23:03'),
(41,'2025_05_05_104555_fix_experiment_columns','2025-05-05 09:24:08'),
(46,'2025_05_05_130725_fix_experiment_compartments','2025-05-05 11:21:15'),
(53,'2025_05_05_201613_fix_bioreplicate_columns','2025-05-05 18:36:14'),
(56,'2025_05_05_204021_remove_bioreplicate_metadata','2025-05-05 18:44:24'),
(67,'2025_05_09_143613_fix_perturbation_columns','2025-05-09 16:16:48'),
(69,'2025_05_09_185956_remove_position_from_measurements','2025-05-09 17:00:56'),
(74,'2025_05_09_194730_fix_study_metabolite_columns','2025-05-09 17:59:54'),
(76,'2025_05_10_112933_add_compartment_id_to_measurements','2025-05-10 09:32:30'),
(78,'2025_05_11_154801_add_fields_to_bioreplicates','2025-05-11 13:52:06'),
(82,'2025_05_13_172421_drop_unused_tables','2025-05-13 16:10:28'),
(102,'2025_05_16_141435_fix_taxon_columns','2025-05-16 12:29:44'),
(103,'2025_05_15_202520_create_measurement_contexts','2025-05-16 12:44:48'),
(104,'2025_05_15_202707_move_measurement_fields_to_contexts','2025-05-16 12:44:48'),
(120,'2025_05_17_165050_fix_metabolite_columns','2025-05-18 09:49:50'),
(121,'2025_05_18_105334_rename_calculations_to_models','2025-05-18 09:49:50'),
(128,'2025_05_19_170414_add_calculation_types','2025-05-19 17:10:23'),
(130,'2025_05_20_220923_fix_modeling_requests_error_column','2025-05-20 20:11:12');

