
INSERT INTO Buildings (BuildingNumber, Name, NumOfFloors)
VALUES ('033-0', 'Clyde P. Fisher Science Hall', 4),
        ('002-0', 'Cotchett Education Building', 2),
        ('025-0', 'Faculty Offices East', 3),
        ('116-0', 'Jespersen Hall', 2),
        ('043-A', 'Kinesiology', 4),
        ('038-0', 'Mathematics and Science', 2),
        ('052-0', 'Science', 1),
        ('053-0', 'Science North', 3),
        ('180-0', 'Warren J. Baker Center for Science and Mathematics', 6),
        ('181-0', 'William and Linda Frost Center for Research and Innovation', 4),
        ('052-B', 'Science Observatory', 1),
        ('043-0', 'Recreation Center', 2),
        ('072-0', 'Plant Conservatory', 1),
        ('228-H', 'Pier Storage Container 2', 1),
        ('228-G', 'Pier Storage Container 1', 1),
        ('228-E', 'Pier Paint Locker', 1),
        ('228-A', 'Pier Main Building', 2),
        ('228-F', 'Pier Boat Locker', 1),
        ('026-M', 'Graphic Arts Modular (M063)', 1),
        ('228-B', 'Flowing Seawater Facility', 1),
        ('228-D', 'Diving Support Locker', 1),
        ('042-A', 'Anderson Aquatic Center', 1)
ON DUPLICATE KEY UPDATE Name=VALUES(Name), NumOfFloors=VALUES(NumOfFloors);


INSERT INTO Floors (BuildingNumber, FloorNumber)
VALUES
-- 033-0 (4 floors)
('033-0',1),('033-0',2),('033-0',3),('033-0',4),

-- 002-0 (2 floors)
('002-0',1),('002-0',2),

-- 025-0 (3 floors)
('025-0',1),('025-0',2),('025-0',3),

-- 116-0 (2 floors)
('116-0',1),('116-0',2),

-- 043-A (4 floors)
('043-A',1),('043-A',2),('043-A',3),('043-A',4),

-- 038-0 (2 floors)
('038-0',1),('038-0',2),

-- 052-0 (1 floor)
('052-0',1),

-- 053-0 (3 floors)
('053-0',1),('053-0',2),('053-0',3),

-- 180-0 (6 floors)
('180-0',1),('180-0',2),('180-0',3),
('180-0',4),('180-0',5),('180-0',6),

-- 181-0 (4 floors)
('181-0',1),('181-0',2),('181-0',3),('181-0',4),

-- 052-B (1 floor)
('052-B',1),

-- 043-0 (2 floors)
('043-0',1),('043-0',2),

-- 072-0 (1 floor)
('072-0',1),

-- 228-H (1 floor)
('228-H',1),

-- 228-G (1 floor)
('228-G',1),

-- 228-E (1 floor)
('228-E',1),

-- 228-A (2 floors)
('228-A',1),('228-A',2),

-- 228-F (1 floor)
('228-F',1),

-- 026-M (1 floor)
('026-M',1),

-- 228-B (1 floor)
('228-B',1),

-- 228-D (1 floor)
('228-D',1),

-- 042-A (1 floor)
('042-A',1)

ON DUPLICATE KEY UPDATE FloorNumber = VALUES(FloorNumber);

