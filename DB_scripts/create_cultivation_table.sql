#CULTIVATION - relation N:1 with the experiment (N experiments can have 1 (the same) cultivation data)
#If the experiment is deleted, do not delete the cultivation as it could be used in 
CREATE TABLE cultivation(
	cultivation_id INT PRIMARY KEY auto_increment,
    cultivation_technique varchar(10),
    # medium_type varchar(20), #read about complex/chemically defined mediums
    culture_medium_file varchar(200) NOT NULL,
    feeding_medium_file varchar(200)
);