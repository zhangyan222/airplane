create table flight (
	depart_id char(3),
	arrive_id char(3),
	company_id char(2),
	flight_id char(10) PRIMARY KEY,
	dtime char(5),
	atime char(5),
	sch1 boolean,
	sch2 boolean,
	sch3 boolean,
	sch4 boolean,
	sch5 boolean,
	sch6 boolean,
	sch7 boolean
);

create table airport_city (
	airport_id char(3) primary key,
	airport_name char(50),
	city char(50)
);

create table company_name (
	company_id char(3) primary key,
	company_name char(50)
);

create table prize (
	flight_id char(10),
	prize real,
	begin_time date,
	end_time date,
	operate_time datetime default CURRENT_TIMESTAMP NOT NULL primary key
);

create table purchase (
	tid integer primary key,
	flight char(10),
	flight_date date,
	pay_method char(10),
	prize real,
	purchased boolean default false
);
