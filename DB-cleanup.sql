
SET FOREIGN_KEY_CHECKS = 0;

-- Relationship / child tables first
DROP TABLE IF EXISTS RoomEquipmentActions;
DROP TABLE IF EXISTS RoomsAreAssignedToDepts_Subdiv;
DROP TABLE IF EXISTS RoomsAreEquippedWithEquipment;
DROP TABLE IF EXISTS EmployeesAssignedToRooms;

-- Other dependent tables
DROP TABLE IF EXISTS Logs;
DROP TABLE IF EXISTS RoomCoordinates;
DROP TABLE IF EXISTS RoomImage;
DROP TABLE IF EXISTS FloorPlans;

-- Core entity tables
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Employees;

-- Lookup / parent tables
DROP TABLE IF EXISTS People;
DROP TABLE IF EXISTS Actions;
DROP TABLE IF EXISTS Equipment;
DROP TABLE IF EXISTS Roles;

DROP TABLE IF EXISTS Departments_Subdivisions;
DROP TABLE IF EXISTS Colleges;

DROP TABLE IF EXISTS RoomType;
DROP TABLE IF EXISTS SpaceType;
DROP TABLE IF EXISTS FurnitureType;

DROP TABLE IF EXISTS Floors;
DROP TABLE IF EXISTS Buildings;

SET FOREIGN_KEY_CHECKS = 1;