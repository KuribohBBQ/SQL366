
-- Buildings
INSERT INTO Buildings (BuildingNumber, Name, NumOfFloors)
VALUES (33, 'Clyde P. Fisher Science Hall', 4)
ON DUPLICATE KEY UPDATE Name = VALUES(Name), NumOfFloors = VALUES(NumOfFloors);

-- Floors
INSERT INTO Floors (BuildingNumber, FloorNumber)
VALUES (33, 3)
ON DUPLICATE KEY UPDATE FloorNumber = VALUES(FloorNumber);

-- RoomType
INSERT INTO RoomType (RoomUseCode, Name)
VALUES (210, 'Teaching Lab')
ON DUPLICATE KEY UPDATE Name = VALUES(Name);

INSERT INTO RoomType (RoomUseCode, Name)
VALUES (211, 'Special Instruction')
ON DUPLICATE KEY UPDATE Name = VALUES(Name);

INSERT INTO RoomType (RoomUseCode, Name)
VALUES (215, 'Teaching Lab Service')
ON DUPLICATE KEY UPDATE Name = VALUES(Name);

INSERT INTO RoomType (RoomUseCode, Name)
VALUES (250, 'Research Lab')
ON DUPLICATE KEY UPDATE Name = VALUES(Name);

INSERT INTO RoomType (RoomUseCode, Name)
VALUES (311, 'Staff Office')
ON DUPLICATE KEY UPDATE Name = VALUES(Name);

-- Rooms
INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 451, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 452, 3, 'Biological Sciences', 215, NULL, NULL, 0)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 453, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 454, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 455, 3, 'Biological Sciences', 215, NULL, NULL, 0)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 456, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 458, 3, 'Biological Sciences', 311, NULL, 'Wacker, Mark (CSM-BIO);Jacobson, Craig (CSM-BIO)', 2)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 459, 3, 'Biological Sciences', 250, NULL, 'Chan, Lauren (CSM-BIO);Francis, Clinton (CSM-BIO)', 10)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 460, 3, 'Biological Sciences', 250, NULL, 'Fidopiastis, Pat (CSM-BIO)', 2)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 461, 3, 'Biological Sciences', 250, NULL, 'Chan, Lauren (CSM-BIO);Liwanag, Heather (CSM-BIO)', 2)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 465, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 466, 3, 'Biological Sciences', 215, NULL, NULL, 0)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 467, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 468, 3, 'Biological Sciences', 210, NULL, NULL, 24)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 469, 3, 'Biological Sciences', 211, NULL, NULL, 0)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 470, 3, 'Biological Sciences', 250, NULL, 'Yeung, Marie (CSM-BIO)', 2)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 471, 3, 'Biological Sciences', 250, NULL, 'Yeung, Marie (CSM-BIO)', 2)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 472, 3, 'Biological Sciences', 250, NULL, 'Strand, Christy (CSM-BIO)', 6)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

INSERT INTO Rooms (BuildingNumber, RoomNumber, FloorNumber, DepartmentName, RoomUseCode, SquareFeet, Notes, Occupancy)
VALUES (33, 473, 3, 'Biological Sciences', 250, NULL, 'Liwanag, Heather (CSM-BIO)', 6)
ON DUPLICATE KEY UPDATE FloorNumber=VALUES(FloorNumber), DepartmentName=VALUES(DepartmentName), RoomUseCode=VALUES(RoomUseCode), SquareFeet=VALUES(SquareFeet), Notes=VALUES(Notes), Occupancy=VALUES(Occupancy);

-- RoomImage
INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 451, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200451-00.Room%20Photo1.180454.jpg&appVersion=1.000082&signature=59f51ab65ff29e020869c378759e328306902e7e78007c2650f5c15358433dba');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 451, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200451-00.Room%20Photo2.180454.jpg&appVersion=1.000082&signature=21b5bfa552bfc3f00c299f4d26408cecfd5f6a245f28455172bf662e7f5791c1');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 452, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200452-00.Room%20Photo1.172850.jpg&appVersion=1.000082&signature=7767ecd0a486206b0b6d87b83514d34ab8ee161b3f1a5a29209909d73c50906f');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 452, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200452-00.Room%20Photo2.172850.jpg&appVersion=1.000082&signature=d3ebff79f13d9b497f2f643e12873b9f2647e81f8692798adbfa4388a8fb4d71');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 453, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200453-00.Room%20Photo1.180337.jpg&appVersion=1.000082&signature=6b749f5805e45dffa7e9df9f444ba4cd569943994eb15b35b8f6289f89c28de6');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 454, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200454-00.Room%20Photo1.180243.jpg&appVersion=1.000082&signature=3a193498f0a4db72bc5c28bbbcd11a52bdabc4c563ecdd1ba22441eb9580730c');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 454, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200454-00.Room%20Photo2.180243.jpg&appVersion=1.000082&signature=7b94c9eac939d09d1d37330ddf8ea47e7db1c92e4440e78f622a4d8ebfb24533');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 455, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200455-00.Room%20Photo1.172727.jpg&appVersion=1.000082&signature=c49558147df6480a2300337989fcf6d8116d0a16df5f418398c9663ad9b27085');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 455, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200455-00.Room%20Photo2.172727.jpg&appVersion=1.000082&signature=cc26779161a573d27938bf5a3d0512929c3eabcfa0a030ec69e042f679bfce7d');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 456, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200456-00.Room%20Photo1.180103.jpg&appVersion=1.000082&signature=5cfc7208b97f22089ed89ceda515810bb28a45528398dd95c1bf1c3bd9594ae9');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 456, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200456-00.Room%20Photo2.180103.jpg&appVersion=1.000082&signature=8b9c41775ff197a3d362d32f83ca66682801f4814651f003586fe1c301ba4908');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 456, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200456-00.Room%20Photo3.180103.jpg&appVersion=1.000082&signature=6564d72f24c784606cf7001169ab76510dfa3453b06100e89e678deccb942681');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 458, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200458-00.Room%20Photo1.172419.jpg&appVersion=1.000082&signature=ef79fffc8e732e98b3d10bd2253d19c5a4940771cf991450f54e41cfad8b9894');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 458, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200458-00.Room%20Photo2.172419.jpg&appVersion=1.000082&signature=4d55d931c514d8173e74b9203253932534f9ede45ed65efe3acbb805fce6962d');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 459, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200459-00.Room%20Photo1.172114.jpg&appVersion=1.000082&signature=00f84a7391878e3ea16c623eb90a092053603fb1af3140f2aeeb96906a31ddc3');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 459, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200459-00.Room%20Photo2.172114.jpg&appVersion=1.000082&signature=30f89a638fb1c69b5cfa24d6ac491d92a4b4f0fe4ed0b1f1f720b2b281e6acda');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 459, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200459-00.Room%20Photo3.172114.jpg&appVersion=1.000082&signature=b4e9248f02b15dabf1b7279d0bcc0b34cbfb90633841448ecdf9db4b652e8224');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 460, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200460-00.Room%20Photo1.171757.jpg&appVersion=1.000082&signature=fba17b59c81ba8387b9ecfa5bad346b4a68c71957be9c6f6711db2950ca0b964');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 460, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200460-00.Room%20Photo2.171757.jpg&appVersion=1.000082&signature=2659433f3bcef6ac6df1b36cc6117974fe4669bf91cd9c13ad3ac77d7bf4e82b');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 461, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200461-00.Room%20Photo1.171616.jpg&appVersion=1.000082&signature=ba9f98438954f491f335ec9c54fd13cf3c475af452a8c8826d032cfba24b146b');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 461, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200461-00.Room%20Photo2.171616.jpg&appVersion=1.000082&signature=dfdc3dc4357fa44b31f6d524cea79ede57ef355166579c74a0a956f7da77253c');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 461, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200461-00.Room%20Photo3.171616.jpg&appVersion=1.000082&signature=f0b6180aa55d81fa26f2a808991bcd8d19fadf313bdf4d05af80a3fb312bac42');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 465, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200465-00.Room%20Photo1.180637.jpg&appVersion=1.000082&signature=ac36257bd58b1a4762a4c1a656438d124f6ac136161de4525302dfc5b94765b2');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 465, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200465-00.Room%20Photo2.180637.jpg&appVersion=1.000082&signature=89ae748b3bc15f102460e3e44d27f8e692e5bc8dce44b6bb1857556f33e09894');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 465, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200465-00.Room%20Photo3.180637.jpg&appVersion=1.000082&signature=4371c13cb44faf17f7d7c7bb0381278ca3ea0803f0875cc741d8f41c59fee16f');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-00.Room%20Photo1.174140.jpg&appVersion=1.000082&signature=7f4ed1d6d3d93121f9523a6411d28759bf29266399ba59b2160ed3d06b1b8d31');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-00.Room%20Photo2.174140.jpg&appVersion=1.000082&signature=8b3f20af30069b97371207b07accb24d2f3cf6f44eb5bd7125e070e098176a63');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-00.Room%20Photo3.174140.jpg&appVersion=1.000082&signature=6f582100017e3e8bc0036837fdc7f42397b29465b0e565f82621f0437f49cf7d');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-00.Room%20Photo4.174141.jpg&appVersion=1.000082&signature=42cc059aa234dc0e92fd286840dd3346d9199dd1f668615b271f5adc54a7faeb');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-A0.Room%20Photo1.174256.jpg&appVersion=1.000082&signature=f32da38cd126dd0cc0030a0b7a6d195dd87066eb32d90cb19c400dd495204f48');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-A0.Room%20Photo2.174256.jpg&appVersion=1.000082&signature=3dd7ac9e764511c43fa2877a302fcc3785aa84b026aae5d5e9795281ff2f9259');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-A0.Room%20Photo3.174256.jpg&appVersion=1.000082&signature=84d407bb62f87c85f9f8125b16c5d7114073976bf8ecea3792c801066261f854');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-B0.Room%20Photo1.174350.jpg&appVersion=1.000082&signature=91ef8d1808543cecff99f4a13fa0e723fe0f5074306657fa24861cb9c2c7a7a6');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 466, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200466-B0.Room%20Photo2.174350.jpg&appVersion=1.000082&signature=cece356ac171cedd5bb97adb31d57dd85803d797417f4334c92beaf062833444');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 467, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200467-00.Room%20Photo1.180930.jpg&appVersion=1.000082&signature=8554e86a36db4102ed79dff3491f3dfdba6aaae5df160f6ec258cb3a8b5a4205');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 467, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200467-00.Room%20Photo2.180930.jpg&appVersion=1.000082&signature=420ad7b5f5fe08d05a18b5c1d3df95b0eaac17342a6b6a911444538e3c2f6c89');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 468, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200468-00.Room%20Photo1.180726.jpg&appVersion=1.000082&signature=6551db51b3e6fe557e21f57a96ad28e87c0c2eabae236e08b3d7a5de6e83f60f');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 468, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200468-00.Room%20Photo2.180726.jpg&appVersion=1.000082&signature=75329c3f2a9ae3bad8ee1ce2bd4980fb5d8678bd023bb0d037103536cc494512');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 468, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200468-A0.Room%20Photo1.171329.jpg&appVersion=1.000082&signature=16b6a8a3da23ca678415ca0b3cb53eac32eb6e5231e4c80e1dc4e8a93fc56a93');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 468, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200468-A0.Room%20Photo2.171329.jpg&appVersion=1.000082&signature=e8ef6886f3a78d5482330b4c66173f2468f24c51795bc25dd83b410e8c119ff0');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 469, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200469-00.Room%20Photo1.171226.jpg&appVersion=1.000082&signature=564f8897c4ae310a474bd963f81a92fb90ed31de52e1d738777f57cabda2c757');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 469, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200469-00.Room%20Photo2.171226.jpg&appVersion=1.000082&signature=f181fb3922946336618b6b354518dfb70a217017a9ccfbbca322e914d7fbc505');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 469, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200469-00.Room%20Photo3.171226.jpg&appVersion=1.000082&signature=b8803798de717549d620642ee8f81f99cd00567e141ad33c69fddbda90097b92');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 470, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200470-00.Room%20Photo1.171044.jpg&appVersion=1.000082&signature=df1400679372542775556f541bd8a8ec0094919eac336855914fee7adaa9b6ee');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 470, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200470-00.Room%20Photo2.171044.jpg&appVersion=1.000082&signature=43952b181597be72c14349240984cd1d431ff55cc1bf441bd483cbeab21df3a1');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 470, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200470-00.Room%20Photo3.171044.jpg&appVersion=1.000082&signature=740fac069811c98642595e8ac6365af5a25e96ba1db38a83cb872cfb4e7d5867');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 471, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200471-00.Room%20Photo1.170920.jpg&appVersion=1.000082&signature=ebe111e605dcef57fcb6c3e41215f66994610e0254b588124e98b19ad74e12da');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 472, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200472-00.Room%20Photo1.170753.jpg&appVersion=1.000082&signature=97c5d73e194388d1f05cbbeca6fc02279c67c860f3d8f17e8a10b6c64ff0fcf6');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 472, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200472-00.Room%20Photo2.170753.jpg&appVersion=1.000082&signature=61da7ead2847495496a085075c68d88c8722ab5d4f6155619de3ba28710365ca');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 473, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200473-00.Room%20Photo1.170606.jpg&appVersion=1.000082&signature=4e560c2750ee61061b8b4fd899e94b90538e78ab97dfbfbf05427e43deed1567');

INSERT IGNORE INTO RoomImage (BuildingNumber, RoomNumber, ImageURL)
VALUES (33, 473, 'https://www.appsheet.com/image/getimageurl?appName=CalPolySpaceManagement2025-1009913&tableName=Facilities&fileName=Facilities_Images%2F033-0%2F033-0%200473-00.Room%20Photo2.170606.jpg&appVersion=1.000082&signature=7ced2afed890f446adbbd56ac52f4d054998942cb693eccfbac30f7992b8e48b');
