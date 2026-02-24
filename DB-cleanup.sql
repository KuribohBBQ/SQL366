SET FOREIGN_KEY_CHECKS = 0;

-- Relationship (junction) tables
DROP TABLE IF EXISTS RoomsAreAssignedToDepts_Subdiv;
DROP TABLE IF EXISTS RoomsAreEquippedWithEquipment;
DROP TABLE IF EXISTS EmployeesAssignedToRooms;

DROP TABLE IF EXISTS Logs;

-- Dependent child tables
DROP TABLE IF EXISTS RoomCoordinates;
DROP TABLE IF EXISTS RoomImage;

-- Core room/floor/building tables
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS RoomType;

DROP TABLE IF EXISTS FloorPlans;
DROP TABLE IF EXISTS Floors;

DROP TABLE IF EXISTS Buildings;

-- Users / roles
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Roles;

-- Employees / equipment
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Equipment;

-- Departments_Subdivisions / colleges
DROP TABLE IF EXISTS Departments_Subdivisions_Subdivisions;
DROP TABLE IF EXISTS Colleges;

SET FOREIGN_KEY_CHECKS = 1;