use BacterialGrowth;

describe Experiment;
INSERT IGNORE INTO Experiment (experimentDescription, experimentDate, reactorId) 
VALUES ('This experiment was carried out in the KU Leuven by researcher XXX', '2008-11-11', 1);
SELECT * FROM Experiment;

describe CultivationConditions;
INSERT IGNORE INTO CultivationConditions (cultivationId, experimentId, inoculumConcentration, inoculumVolumen)
VALUES 
	(1001, 1, 10, 10),
    (1002, 1, 10, 20);
SELECT * FROM CultivationConditions;

describe TechnicalReplicates;
INSERT IGNORE INTO TechnicalReplicates (replicateId, cultivationId, bacterialAbundanceFile, metabolitesFile)
VALUES 
	('1001_1', 1001, 10, 10),
    ('1001_1', 1001, 10, 20);
SELECT * FROM CultivationConditions;

