#REACTOR - relation N:1 with the experiment (N experiments can use 1 reactor)
CREATE TABLE reactor(
	reactor_id INT PRIMARY KEY auto_increment,
    volume float, 
    stirring_speed float
);
    