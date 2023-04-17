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

SELECT * FROM TechnicalReplicate where experimentId = 105;




SELECT * FROM Experiment WHERE (studyId= '1');
SELECT * FROM Perturbation WHERE (experimentId= '101');
SELECT * FROM TechnicalReplicate WHERE (experimentId= '101');
SELECT perturbationId FROM Perturbation WHERE (experimentId= '101'); 
