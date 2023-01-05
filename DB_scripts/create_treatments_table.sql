# TREATMENTS - relation of N:M with experiment. We need an intermediate table to relate both of them.
# 1 experiment may have several treatments that can be shared among many experiments
CREATE TABLE treatments (
	treatment_id INT primary key auto_increment
);

CREATE TABLE experiment_treatments (
	et_id INT PRIMARY KEY auto_increment,
	experiment_id INT NOT NULL,
    treatment_id INT NOT NULL,
    FOREIGN KEY (experiment_id) 
		REFERENCES experiment(experiment_id)
        ON DELETE cascade,
    FOREIGN KEY (treatment_id) 
		REFERENCES treatments(treatment_id)
        ON DELETE cascade
);

