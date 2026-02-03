CREATE TABLE Colleges (
  Name VARCHAR(200) NOT NULL,
  PRIMARY KEY (Name)
) 

CREATE TABLE Departments (
  Name    VARCHAR(200) NOT NULL,
  College VARCHAR(200) NOT NULL,
  PRIMARY KEY (Name),
  CONSTRAINT fk_departments_college
    FOREIGN KEY (College) REFERENCES Colleges(Name)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) 


-- Buildings, Floors

CREATE TABLE Buildings (
  BuildingNumber INT NOT NULL,
  Name           VARCHAR(200) NOT NULL,
  NumOfFloors     INT NOT NULL,
  PRIMARY KEY (BuildingNumber),
  CONSTRAINT chk_buildings_numfloors
    CHECK (NumOfFloors > 0)
) 

CREATE TABLE Floors (
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  PRIMARY KEY (BuildingNumber, FloorNumber),
  CONSTRAINT fk_floors_building
    FOREIGN KEY (BuildingNumber) REFERENCES Buildings(BuildingNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) 


-- FloorPlans (1:1 with Floors)

CREATE TABLE FloorPlans (
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  FileName       VARCHAR(500) NOT NULL,
  PRIMARY KEY (BuildingNumber, FloorNumber),
  CONSTRAINT fk_floorplans_floor
    FOREIGN KEY (BuildingNumber, FloorNumber)
    REFERENCES Floors(BuildingNumber, FloorNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) 


-- Rooms
-- Rooms are in Buildings (M:1) and on Floors (M:1)
-- Rooms assigned to Departments (M:1)

CREATE TABLE Rooms (
  BuildingNumber  INT NOT NULL,
  RoomNumber      INT NOT NULL,

  SquareFeet      INT NULL,
  Type            INT NULL,
  Notes           VARCHAR(2000) NULL,
  ImageUrl        VARCHAR(1000) NULL,
  Occupancy       INT NULL,
  FurnitureType   INT NULL,
  Coordinates     VARCHAR(500) NULL,

  DepartmentName  VARCHAR(200) NULL,

  PRIMARY KEY (BuildingNumber, RoomNumber),

  CONSTRAINT fk_rooms_building
    FOREIGN KEY (BuildingNumber) REFERENCES Buildings(BuildingNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_rooms_floor
    FOREIGN KEY (BuildingNumber, FloorNumber)
    REFERENCES Floors(BuildingNumber, FloorNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_rooms_department
    FOREIGN KEY (DepartmentName) REFERENCES Departments(Name)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  CONSTRAINT chk_rooms_squarefeet
    CHECK (SquareFeet IS NULL OR SquareFeet >= 0),

  CONSTRAINT chk_rooms_occupancy
    CHECK (Occupancy IS NULL OR Occupancy >= 0)
) 


-- Faculty + junction (M:N)

CREATE TABLE Faculty (
  Email      VARCHAR(320) NOT NULL,
  Name       VARCHAR(200) NOT NULL,
  College    VARCHAR(200) NULL,
  Department VARCHAR(200) NULL,
  PRIMARY KEY (Email)
) 

CREATE TABLE FacultyAssignedToRooms (
  Email          VARCHAR(320) NOT NULL,
  BuildingNumber INT NOT NULL,
  RoomNumber     INT NOT NULL,
  PRIMARY KEY (Email, BuildingNumber, RoomNumber),
  CONSTRAINT fk_fatr_faculty
    FOREIGN KEY (Email) REFERENCES Faculty(Email)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_fatr_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) 


-- Equipment (M:N)

CREATE TABLE Equipment (
  Type        VARCHAR(100) NOT NULL,
  Description VARCHAR(1000) NULL,
  Sensitive   BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (Type)
) 

CREATE TABLE RoomsHaveEquipment (
  BuildingNumber INT NOT NULL,
  RoomNumber     INT NOT NULL,
  Type           VARCHAR(100) NOT NULL,
  PRIMARY KEY (BuildingNumber, RoomNumber, Type),
  CONSTRAINT fk_rhe_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_rhe_equipment
    FOREIGN KEY (Type) REFERENCES Equipment(Type)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) 


-- Roles, Permissions, RolePermissions (Roles given Permissions)

CREATE TABLE Roles (
  Role_ID   VARCHAR(50) NOT NULL,
  RoleName  VARCHAR(200) NOT NULL,
  PRIMARY KEY (Role_ID)
) 

CREATE TABLE Permissions (
  ID          INT NOT NULL,
  Name        VARCHAR(200) NOT NULL,
  Description VARCHAR(2000) NULL,
  PRIMARY KEY (ID)
) 

CREATE TABLE RolePermissions (
  Role_ID      VARCHAR(50) NOT NULL,
  PermissionID INT NOT NULL,
  PRIMARY KEY (Role_ID, PermissionID),
  CONSTRAINT fk_rp_role
    FOREIGN KEY (Role_ID) REFERENCES Roles(Role_ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_rp_permission
    FOREIGN KEY (PermissionID) REFERENCES Permissions(ID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
) 


-- Users assigned to Roles (M:1)

CREATE TABLE Users (
  Email     VARCHAR(320) NOT NULL,
  Name      VARCHAR(200) NOT NULL,
  Password  VARCHAR(255) NOT NULL,  -- store hash
  Role_ID   VARCHAR(50) NOT NULL,
  PRIMARY KEY (Email),
  CONSTRAINT fk_users_role
    FOREIGN KEY (Role_ID) REFERENCES Roles(Role_ID)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) 


-- Logs (User 1:M Logs, Logs M:1 Rooms)

CREATE TABLE Logs (
  LogId            INT NOT NULL AUTO_INCREMENT,
  
  LogDate          DATE NOT NULL,
  LoginTime        TIME NULL,
  LogOutTime       TIME NULL,

  ChangeDescription VARCHAR(4000) NULL,

  BuildingNumber   INT NOT NULL,
  RoomNumber       INT NOT NULL,

  PRIMARY KEY (LogId),

  CONSTRAINT fk_logs_user
    FOREIGN KEY (UserEmail) REFERENCES Users(Email)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_logs_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT

) 

