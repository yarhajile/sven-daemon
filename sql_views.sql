DROP VIEW IF EXISTS device_output_actions;

DROP VIEW IF EXISTS devices_all;
DROP VIEW IF EXISTS devices_bus;

DROP VIEW IF EXISTS devices_GPIO;
DROP VIEW IF EXISTS devices_SPI;
DROP VIEW IF EXISTS devices_ADC;
DROP VIEW IF EXISTS devices_I2C;
DROP VIEW IF EXISTS devices_PWM;
DROP VIEW IF EXISTS devices_UART;
DROP VIEW IF EXISTS devices_RCSwitch;
DROP VIEW IF EXISTS devices_WebSocketServer;
DROP VIEW IF EXISTS devices_SvenSocketServer;
DROP VIEW IF EXISTS devices_MP3Player;
DROP VIEW IF EXISTS devices_DHT22;
DROP VIEW IF EXISTS devices_Nest;
DROP VIEW IF EXISTS devices_NestProtect;
DROP VIEW IF EXISTS devices_NestThermostat;
DROP VIEW IF EXISTS devices_Notification;
DROP VIEW IF EXISTS devices_Dummy;
DROP VIEW IF EXISTS devices_JunkDrawer;
DROP VIEW IF EXISTS devices_Espeak;


CREATE VIEW device_output_actions AS
SELECT
    d.id,
    d.name,
    a.action,
    a.parameters,
    a.output_device_id,
    ld.id AS location_id,
    lg.id AS location_group_id
FROM
    monitor_input_device_callback_action AS a
    JOIN monitor_device AS d ON d.id = a.input_device_id
    JOIN monitor_location_device AS ld ON d.id = ld.device_id
    JOIN monitor_location AS l ON ld.location_id = l.id
    JOIN monitor_location_group AS lg ON l.location_group_id = lg.id
;


CREATE VIEW devices_all AS
SELECT
    lg.id               AS location_group_id,
	lg.name 			AS location_group_name,
	lg.active           AS location_group_active,
	lg.description 		AS location_group_description,

    l.id                AS location_id,
	l.name 				AS location_name,
	l.active            as location_active,
	l.description 		AS location_description,

    d.id                AS device_id,
	d.name 				AS device_name,
	d.active            AS device_active,
	d.description 		AS device_description,
	d.current_value 	AS device_current_value,

	dp.parameter        AS device_key,
	dp.value            AS device_value
FROM
	monitor_location_group AS lg

	JOIN monitor_location AS l
		ON ( l.location_group_id = lg.id )

	JOIN monitor_location_device AS ld
		ON ( ld.location_id = l.id )

	JOIN monitor_device AS d
		ON ( d.id = ld.device_id )

	JOIN monitor_device_parameter AS dp
		ON ( dp.device_id = d.id )
;

--
-- BUS
--
CREATE VIEW devices_bus AS
SELECT
    *
FROM
    devices_all
WHERE
    device_key = 'bus'
;

--
-- GPIO
--
CREATE VIEW devices_GPIO AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'GPIO'
;


--
-- PWM
--
CREATE VIEW devices_PWM AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'PWM'
;


--
-- I2C
--
CREATE VIEW devices_I2C AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'I2C'
;

--
-- ADC
--
CREATE VIEW devices_ADC AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'ADC'
;

--
-- SPI
--
CREATE VIEW devices_SPI AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'SPI'
;

--
-- PWM
--
CREATE VIEW devices_UART AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'UART'
;


--
-- Socket
--
CREATE VIEW devices_SvenSocketServer AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'Socket'
;


--
-- Web Socket
--
CREATE VIEW devices_WebSocketServer AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'WebSocketServer'
;


--
-- System Sound
--
CREATE VIEW devices_MP3Player AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'MP3Player'
;


--
-- DHT22
--
CREATE VIEW devices_DHT22 AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'DHT22'
;


--
-- MODIFY THIS TO ONLY ALLOW DEVICES TO CHOOSE FROM WHEN THERE IS AT LEAST ONE Nest device
-- Nest Thermostat
--
CREATE VIEW devices_NestThermostat AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'NestThermostat'
;


--
-- MODIFY THIS TO ONLY ALLOW DEVICES TO CHOOSE FROM WHEN THERE IS AT LEAST ONE Nest device
-- Nest Protect
--
CREATE VIEW devices_NestProtect AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'NestProtect'
;


--
-- Nest
--
CREATE VIEW devices_Nest AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'Nest'
;


--
-- RCSWITCH
--
CREATE VIEW devices_RCSwitch AS
SELECT
    *,
    ( SELECT device_value FROM devices_all WHERE device_id = da.device_id AND device_key = 'address' ) AS address,
    ( SELECT device_value FROM devices_all WHERE device_id = da.device_id AND device_key = 'unitcode' ) AS unitcode
FROM
    devices_all AS da
WHERE
    da.device_value = 'RCSwitch'
;


--
-- Dummy
--
CREATE VIEW devices_Dummy AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'Dummy'
;


--
-- Notification
--
CREATE VIEW devices_Notification AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'Notification'
;


--
-- Junk Drawer ( Common stuffs )
--
CREATE VIEW devices_JunkDrawer AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'JunkDrawer'
;


--
-- Espeak ( Common stuffs )
--
CREATE VIEW devices_Espeak AS
SELECT
    *
FROM
    devices_bus
WHERE
    device_value = 'Espeak'
;
