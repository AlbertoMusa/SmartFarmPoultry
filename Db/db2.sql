CREATE TABLE UserDevice(
    user_id int not null primary key,
    username  varchar(100) not null unique,
    password varchar(100) not null unique
);

CREATE TABLE UserFarm(
    pub_id varchar(100) not null primary key,
    pri_id varchar(200) not null unique
);

CREATE TABLE Farm(
    pub_id varchar(100) not null,
    time_sam timestamp not null,
	time_con timestamp not null,
	lux int null,
	timeled_open_h int null,
	timeled_open_m int null,
	timeled_close_h int null,
	timeled_close_m int null,
	timedoor_open_h int null,
	timedoor_open_m int null,
	timedoor_close_h int null,
	timedoor_close_m int null,
	timenest_open_h int null,
	timenest_open_m int null,
	timenest_close_h int null,
	timenest_close_m int null,
	timeksr_open_h int null,
	timeksr_open_m int null,
	timeksr_close_h int null,
	timeksr_close_m int null,
	timeonfly_open_h int null,
	timeonfly_open_m int null,
	timeonfly_close_h int null,
	timeonfly_close_m int null,
	a_lux int null,
	a_hysteresis int null,
	b_lux int null,
	b_hysteresis int null,
	FOREIGN KEY (pub_id) REFERENCES UserFarm(pub_id),
	UNIQUE(pub_id, time_sam, time_con),
	PRIMARY KEY (pub_id, time_sam, time_con)
);

CREATE TABLE Motor(
    motor_id int not null,
    farm_id varchar(100) not null,
    time_sam timestamp not null,
	time_con timestamp not null,
    addresses varchar(20) null,
	numbers varchar(20) null,
	time_ready int null,
	active boolean null,
	CHECK (motor_id BETWEEN 1 AND 7),
	FOREIGN KEY (farm_id, time_sam, time_con) REFERENCES Farm(pub_id, time_sam, time_con),
	UNIQUE(motor_id, farm_id, time_sam, time_con),
	PRIMARY KEY (motor_id, farm_id, time_sam, time_con)
);

CREATE TABLE Led(
    led_id int not null,
    farm_id varchar(100) not null,
    time_sam timestamp not null,
	time_con timestamp not null,
    addresses varchar(20) null,
	numbers varchar(20) null,
	max_value int null,
	dim_up_delay int null,
	dim_down_delay int null,
	dim_time int null,
	active boolean null,
	CHECK (led_id BETWEEN 1 AND 6),
	CHECK (max_value BETWEEN 0 AND 255),
	FOREIGN KEY (farm_id, time_sam, time_con) REFERENCES Farm(pub_id, time_sam, time_con),
	UNIQUE(led_id, farm_id, time_sam, time_con),
	PRIMARY KEY (led_id, farm_id, time_sam, time_con)
);

CREATE TABLE Change(
    user_id int not null,
    pub_id varchar(100) not null,
    dev int not null,
    code int not null,
	val varchar(20) not null,
	time_req timestamp not null,
	flag boolean not null default FALSE,
	FOREIGN KEY (user_id) REFERENCES UserDevice(user_id),
	FOREIGN KEY (pub_id) REFERENCES UserFarm(pub_id),
	PRIMARY KEY (user_id, pub_id, time_req)
);

dev = db.Column('dev', db.Integer(20))
    code = db.Column('code', db.Integer(20))
    val = db.Column('val', db.String(20))
    time_req = db.Column('time_req', db.DateTime, primary_key=True)
    flag = db.Column('flag', db.Boolean, default=False)

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

INSERT INTO Change ( user_id, pub_id, dev, code, val, time_req, flag)
VALUES ( 1, 'a', 0, 1, '160', NOW(), False),
( 1, 'a', 1, 1, 'ok', NOW(), False),
( 1, 'b', 2, 2, '160', NOW(), False),
( 1, 'a', 3, 3, 'ok', NOW(), False),
( 1, 'b', 7, 5, '160', NOW(), False),
( 1, 'a', 13, 3, 'ok', NOW(), False);

SELECT * FROM Session;
DELETE FROM Session;

