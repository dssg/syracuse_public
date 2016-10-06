
create schema if not exists water_system;
DROP TABLE IF EXISTS water_system.new_mains;
CREATE TABLE water_system.new_mains (
	comments VARCHAR(50),
	date_laid DATE,
	depth FLOAT,
	diameters FLOAT,
	enabled INTEGER,
	globalid VARCHAR(50),
	install_year INTEGER,
	lat_system VARCHAR(50),
	material VARCHAR(50),
	objectid INTEGER,
	owner VARCHAR(50),
	shape_length FLOAT,
	year_abandoned INTEGER
);

\copy water_system.new_mains from './temp.csv' delimiter ',' csv header;
