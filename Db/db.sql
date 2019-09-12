CREATE TABLE UserFarm(
    pub_id varchar(100) not null primary key,
    pri_id varchar(200) not null unique,
    time_sam timestamp not null default CURRENT_TIMESTAMP,
	time_con timestamp not null default CURRENT_TIMESTAMP,
	lux int not null default 0,
	timeled_open_h int not null default 0,
	timeled_open_m int not null default 0,
	timeled_close_h int not null default 0,
	timeled_close_m int not null default 0,
	timedoor_open_h int not null default 0,
	timedoor_open_m int not null default 0,
	timedoor_close_h int not null default 0,
	timedoor_close_m int not null default 0,
	timenest_open_h int not null default 0,
	timenest_open_m int not null default 0,
	timenest_close_h int not null default 0,
	timenest_close_m int not null default 0,
	timeksr_open_h int not null default 0,
	timeksr_open_m int not null default 0,
	timeksr_close_h int not null default 0,
	timeksr_close_m int not null default 0,
	timeonfly_open_h int not null default 0,
	timeonfly_open_m int not null default 0,
	timeonfly_close_h int not null default 0,
	timeonfly_close_m int not null default 0,
	a_lux int not null default 0,
	a_hysteresis int not null default 0,
	b_lux int not null default 0,
	b_hysteresis int not null default 0
);

CREATE TABLE UserDevice(
    user_id int not null primary key,
    username  varchar(100) not null unique,
    password varchar(100) not null unique
);

CREATE TABLE Motor(
    motor_id int not null,
    farm_id varchar(100) not null,
    addresses varchar(20) null,
	numbers varchar(20) null,
	time_ready int not null default 0,
	active boolean not null default FALSE,
	CHECK (motor_id BETWEEN 1 AND 7),
	FOREIGN KEY (farm_id) REFERENCES UserFarm(pub_id),
	PRIMARY KEY (motor_id, farm_id)
);

CREATE TABLE Led(
    led_id int not null,
    farm_id varchar(100) not null,
    addresses varchar(20) null,
	numbers varchar(20) null,
	max_value int not null default 0,
	dim_up_delay int not null default 0,
	dim_down_delay int not null default 0,
	dim_time int not null default 0,
	active boolean not null default FALSE,
	CHECK (led_id BETWEEN 1 AND 6),
	CHECK (max_value BETWEEN 0 AND 255),
	FOREIGN KEY (farm_id) REFERENCES UserFarm(pub_id),
	PRIMARY KEY (led_id, farm_id)
);

CREATE TABLE Change(
    change_id int not null primary key,
    farm_id varchar(100) not null,
    code varchar(20) not null,
	val varchar(20) not null,
	time_req time not null,
	flag boolean not null default FALSE,
	FOREIGN KEY (farm_id) REFERENCES UserFarm(pub_id)
);

CREATE TABLE Session(
    session_id varchar(100) null unique,
    pub_id varchar(100) not null,
    key varchar(400) not null,
	sid varchar(100) null,
	otp varchar(100) not null primary key,
	flag boolean not null,
	time_start timestamp not null,
	time_end timestamp null,
	FOREIGN KEY (pub_id) REFERENCES UserFarm(pub_id)
);

INSERT INTO UserFarm ( pub_id, pri_id)
VALUES ( 'a', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.aWRwcml2YXRv.7fygGrObBYuD6P9CK0mu1SyQ0_SJwQXaLaQQkU_Ufw0'),
( 'b', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.cGFyb2xh.qAR8yz13LEZhQ3YpAfDP2UByVT4mQZKXM0nIdXGyLlE');

INSERT INTO UserDevice ( user_id, username, password)
VALUES ( 1, 'username', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.Y2xpZW50UHN3.kdUiGdXjeA3xVoIVggTj8lycNFBcZIbXXMrr20Y9QiU');

INSERT INTO Motor ( motor_id, farm_id)
VALUES ( 1, 'a'),( 2, 'a'),( 3, 'a'),( 4, 'a'),( 5, 'a'),( 6, 'a'),( 7, 'a'),( 1, 'b'),( 2, 'b'),( 3, 'b'),( 4, 'b'),( 5, 'b'),( 6, 'b'),( 7, 'b');

INSERT INTO Led ( led_id, farm_id)
VALUES ( 1, 'a'),( 2, 'a'),( 3, 'a'),( 4, 'a'),( 5, 'a'),( 6, 'a'),( 1, 'b'),( 2, 'b'),( 3, 'b'),( 4, 'b'),( 5, 'b'),( 6, 'b');

INSERT INTO Change ( change_id, farm_id, code, val, time_req, flag)
VALUES ( 1, 'a', 'first', '160', NOW(), False),
( 2, 'a', 'second', 'ok', NOW(), False),
( 3, 'b', 'third', '160', NOW(), False),
( 4, 'a', 'fourth', 'ok', NOW(), False),
( 5, 'b', 'fiveth', '160', NOW(), False),
( 6, 'a', 'sixth', 'ok', NOW(), False);

SELECT * FROM Session;
DELETE FROM Session;

