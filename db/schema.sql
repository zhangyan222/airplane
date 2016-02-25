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
	operate_time datetime default CURRENT_TIMESTAMP NOT NULL
);

create table purchase (
	tid integer primary key,
	passenger_id integer,
	flight_id char(10),
	flight_date date,
	pay_method char(10),
	prize real,
	purchased boolean default false
);

create table passenger (
	passenger_id integer primary key,
	name char(50),
	gender char(4),
	work varchar,
	card char(18),
	mail varchar,
	phone char(20)
);

create view e_ticket as 
select tid, purchase.flight_id as flight, flight_date, dtime,
	name, gender, card, company_name.company_name as company_name,
	dcity.airport_name as dairport, acity.airport_name as aairport
	from purchase
left join passenger on purchase.passenger_id = passenger.passenger_id 
left join flight on purchase.flight_id = flight.flight_id 
left join airport_city dcity on flight.depart_id = dcity.airport_id 
left join airport_city acity on flight.arrive_id = acity.airport_id 
left join company_name on flight.company_id = company_name.company_id;

create view plane_table as
select d.airport_name as dairport, a.airport_name as aairport,
	printf("%s(%s)", d.airport_name, d.city) as depart,
	printf("%s(%s)", a.airport_name, a.city) as arrive,
	company_name, flight.flight_id as flight_id, 
	dtime, atime, prize.prize as prize,
	d.city as dcity, a.city as acity,
	prize.begin_time as begin_time, prize.end_time as end_time
from flight left join airport_city d on depart_id = d.airport_id
left join airport_city a on arrive_id = a.airport_id
left join company_name c on flight.company_id = c.company_id
left join prize on flight.flight_id = prize.flight_id;
