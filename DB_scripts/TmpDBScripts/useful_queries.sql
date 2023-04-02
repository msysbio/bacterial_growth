INSERT INTO Study (studyDescription) VALUES ('test');
INSERT INTO Study (studyDescription) VALUES ('the aim of this study is to ...');

INSERT INTO Reactor (reactorName) VALUES ('ambr15f');

INSERT INTO Media (mediaId, mediaName, mediaFile) VALUES (1, 'myMedia', 'path/here.txt');
INSERT INTO Precultivation (precultivationId) VALUES (1);
INSERT IGNORE INTO Precultivation (precultivationDescription)
VALUES ('Bacteria stored in XXX at temperate XXX...');

INSERT INTO Experiment (studyId, reactorId, mediaId) VALUES (1, 1, 1);
INSERT INTO Perturbation (perturbationId, experimentId) VALUES (7, 1);

INSERT IGNORE INTO Bacteria (bacteriaGenus, bacteriaSpecies, bacteriaStrain) VALUES ('B', 'BT', 1);

Use BacterialGrowth;
Describe Reactor;
Describe Media;
Describe Experiment;
DESCRIBE Perturbation;
Describe TechnicalReplicate;

Select * from Study;
SELECT * FROM Precultivation;
SELECT * FROM Reactor;
SELECT * FROM Media;
SELECT * FROM Bacteria;
SELECT * FROM Experiment;
SELECT * FROM Perturbation;
SELECT * FROM TechnicalReplicate;

INSERT IGNORE INTO Experiment (studyId,experimentId,reactorId,precultivationId,mediaId,plateId,plateColumn,plateRow,blank,inoculumConcentration,inoculumVolume,initialPh,initialTemperature,carbonSource,antibiotic,experimentDescription) VALUES ('1','101','1','1','1','1','1','A','0','1000000','10','5','20','0','0','Work?')