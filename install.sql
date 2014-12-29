-- Create default location group
INSERT INTO
  monitor_location_group
VALUES
  ( 1, now(), now(), 'Home', 'Home Sweet Home', true )
;


-- Create default location
INSERT INTO
  monitor_location
VALUES
  ( 1, now(), now(), 'System', 'System Services', true, 1 )
;


-- Create default web socket
INSERT INTO
  monitor_device
VALUES
  ( 1, now(), now(), 'System Web Socket Server', 'System web socket server listening address', true, '', false, 1 ),
  ( 2, now(), now(), 'Common System Components', 'Common System Components', true, '', false, 1 ),
;


-- Create default
INSERT INTO
  monitor_device_parameter
VALUES
  ( 1, now(), now(), 1, 'address', '0.0.0.0' ),
  ( 2, now(), now(), 1, 'port', '7654' ),
  ( 3, now(), now(), 1, 'interface', 'System' ),
  ( 4, now(), now(), 1, 'bus', 'WebSocketServer' )
;


-- Preload arm statuses
INSERT INTO
  monitor_arm_status
VALUES
  ( 1, 'away' ),
  ( 2, 'home' ),
  ( 3, 'night' )
;


-- Preset the main location groups arm status to 'home'
INSERT INTO
  monitor_arm_status_location_group
VALUES
  ( 1, 1, 2 )
;