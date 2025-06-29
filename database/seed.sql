-- Seed Clients
INSERT INTO clients (organization_name, faiss_label_path, image_folder_path)
VALUES
('Acme Corp', '/data/faiss/acme_labels.pkl', '/data/images/acme/'),
('University XYZ', '/data/faiss/uni_xyz_labels.pkl', '/data/images/uni_xyz/'),
('SmartHome Inc', '/data/faiss/smarthome_labels.pkl', '/data/images/smarthome/');

-- Seed Identities (people linked to clients)
INSERT INTO identities (client_id, full_name, image_path)
VALUES
(1, 'John Doe', '/data/images/acme/john_doe.jpg'),
(1, 'Jane Smith', '/data/images/acme/jane_smith.jpg'),
(2, 'Alice Johnson', '/data/images/uni_xyz/alice_johnson.jpg'),
(3, 'Bob Brown', '/data/images/smarthome/bob_brown.jpg');

-- Seed Cameras (assigned to clients, gates and roles)
INSERT INTO cameras (roll, client_id, gate, camera_location)
VALUES
('entry', 1, 'Main Gate', 'Lobby Entrance'),
('exit', 1, 'Main Gate', 'Lobby Exit'),
('entry', 2, 'North Gate', 'University Entrance'),
('exit', 2, 'North Gate', 'University Exit'),
('entry', 3, 'Front Door', 'Main Entrance'),
('exit', 3, 'Front Door', 'Back Exit');

-- Seed Access Logs (identity movement logs)
INSERT INTO access_logs (identity_id, camera_id, access_time, access_type, detection_confidence, processing_time_ms)
VALUES
(1, 1, NOW() - INTERVAL '2 hours', 'entry', 0.92, 150),
(1, 2, NOW() - INTERVAL '1 hour 45 minutes', 'exit', 0.95, 140),
(2, 1, NOW() - INTERVAL '30 minutes', 'entry', 0.90, 160),
(3, 3, NOW() - INTERVAL '3 hours', 'entry', 0.88, 170),
(4, 5, NOW() - INTERVAL '10 minutes', 'entry', 0.93, 155);
-- Seed Identities (people linked to clients)
INSERT INTO identities (client_id, full_name, image_path)
VALUES
(1, 'John Doe', '/data/images/acme/john_doe.jpg'),
(1, 'Jane Smith', '/data/images/acme/jane_smith.jpg'),
(2, 'Alice Johnson', '/data/images/uni_xyz/alice_johnson.jpg'),
(3, 'Bob Brown', '/data/images/smarthome/bob_brown.jpg');-- Seed Cameras (assigned to clients, gates and roles)
INSERT INTO cameras (roll, client_id, gate, camera_location)
VALUES
('entry', 1, 'Main Gate', 'Lobby Entrance'),
('exit', 1, 'Main Gate', 'Lobby Exit'),
('entry', 2, 'North Gate', 'University Entrance'),
('exit', 2, 'North Gate', 'University Exit'),
('entry', 3, 'Front Door', 'Main Entrance'),
('exit', 3, 'Front Door', 'Back Exit');-- Seed Access Logs (identity movement logs)
INSERT INTO access_logs (identity_id, camera_id, access_time, access_type, detection_confidence, processing_time_ms)
VALUES
(1, 1, NOW() - INTERVAL '2 hours', 'entry', 0.92, 150),
(1, 2, NOW() - INTERVAL '1 hour 45 minutes', 'exit', 0.95, 140),
(2, 1, NOW() - INTERVAL '30 minutes', 'entry', 0.90, 160),
(3, 3, NOW() - INTERVAL '3 hours', 'entry', 0.88, 170),
(4, 5, NOW() - INTERVAL '10 minutes', 'entry', 0.93, 155);