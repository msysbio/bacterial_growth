DROP DATABASE Metabolites;
CREATE DATABASE Metabolites;
USE Metabolites;

CREATE TABLE IF NOT EXISTS MetaboliteName (
    cheb_id VARCHAR(255), 
    metabo_name VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (cheb_id)
);

CREATE TABLE IF NOT EXISTS MetaboliteSynonym (
    syn_id INT AUTO_INCREMENT PRIMARY KEY, 
    synonym_value VARCHAR(255) DEFAULT NULL,
    cheb_id VARCHAR(255),
    FOREIGN KEY (cheb_id) REFERENCES MetaboliteName(cheb_id)
);

