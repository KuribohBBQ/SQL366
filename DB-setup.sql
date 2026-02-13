CREATE TABLE Colleges (
  AbbreviatedName VARCHAR(200) NOT NULL,
  FullName VARCHAR(200) NOT NULL,
  PRIMARY KEY (AbbreviatedName)
);

CREATE TABLE Departments (
  DepartmentName    VARCHAR(200) NOT NULL,
  College VARCHAR(200) NOT NULL,
  PRIMARY KEY (DepartmentName)
  CONSTRAINT fk_departments_college
    FOREIGN KEY (College) REFERENCES Colleges(AbbreviatedName)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


-- Buildings

CREATE TABLE Buildings (
  BuildingNumber INT NOT NULL,
  Name           VARCHAR(200) NOT NULL,
  NumOfFloors     INT NOT NULL,
  PRIMARY KEY (BuildingNumber),
  CONSTRAINT chk_buildings_numfloors
    CHECK (NumOfFloors > 0)
);

-- Floors (weak under Building)

CREATE TABLE Floors (
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  PRIMARY KEY (BuildingNumber, FloorNumber),
  CONSTRAINT fk_floors_building
    FOREIGN KEY (BuildingNumber) REFERENCES Buildings(BuildingNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);


-- FloorPlans (1:1 with Floors)

CREATE TABLE FloorPlans (
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  FileName       VARCHAR(500) NOT NULL,
  FilePath       VARCHAR(1000) NOT NULL,

  PRIMARY KEY (BuildingNumber, FloorNumber),

  CONSTRAINT fk_floorplans_floor
    FOREIGN KEY (BuildingNumber, FloorNumber)
    REFERENCES Floors(BuildingNumber, FloorNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);



-- RoomType
CREATE TABLE RoomType (
  RoomUseCode INT NOT NULL,
  Name VARCHAR(200) NOT NULL,
  PRIMARY KEY (RoomUseCode)
);

-- Rooms (weak under Buildings)
CREATE TABLE Rooms (
  BuildingNumber  INT NOT NULL,
  RoomNumber      INT NOT NULL,
  FloorNumber     INT NOT NULL,      

  DepartmentName  VARCHAR(200) NULL,
  RoomUseCode     INT NULL,

  SquareFeet      INT NULL,
  Notes           VARCHAR(2000) NULL,
  Occupancy       INT NULL,

  PRIMARY KEY (BuildingNumber, RoomNumber),

  CONSTRAINT fk_rooms_building
    FOREIGN KEY (BuildingNumber)
    REFERENCES Buildings(BuildingNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_rooms_floor
    FOREIGN KEY (BuildingNumber, FloorNumber)
    REFERENCES Floors(BuildingNumber, FloorNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_rooms_department
    FOREIGN KEY (DepartmentName) REFERENCES Departments(DepartmentName)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  CONSTRAINT fk_rooms_type
    FOREIGN KEY (RoomUseCode) REFERENCES RoomType(RoomUseCode)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);


CREATE TABLE RoomImage (
  BuildingNumber INT NOT NULL,
  RoomNumber INT NOT NULL,
  
  ImageURL VARCHAR(500) NOT NULL,

  PRIMARY KEY(BuildingNumber, RoomNumber, ImageURL),

  CONSTRAINT fk_roomimage_room
    FOREIGN KEY (BuildingNumber, RoomNumber) 
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Equipment (M:N)

CREATE TABLE Equipment (
  EType        VARCHAR(100) NOT NULL,
  EDescription VARCHAR(1000) NULL,
  Sensitive   BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (EType)
);

CREATE TABLE RoomsHaveEquipment (
  BuildingNumber INT NOT NULL,
  RoomNumber     INT NOT NULL,
  EType           VARCHAR(100) NOT NULL,
  PRIMARY KEY (BuildingNumber, RoomNumber, EType),
  CONSTRAINT fk_rhe_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_rhe_equipment
    FOREIGN KEY (EType) REFERENCES Equipment(EType)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE Employees (
  Email          VARCHAR(320) NOT NULL,
  FullName       VARCHAR(200) NOT NULL,
  DepartmentName VARCHAR(200) NOT NULL,
  College        VARCHAR(200) NOT NULL,
  PRIMARY KEY (Email),

  CONSTRAINT fk_emp_dept
    FOREIGN KEY (DepartmentName) REFERENCES Departments(DepartmentName)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_emp_college
    FOREIGN KEY (College) REFERENCES Colleges(AbbreviatedName)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- Roles, Permissions, RolePermissions (Roles given Permissions)

CREATE TABLE Roles (
  Role_ID   VARCHAR(50) NOT NULL,
  RoleName  VARCHAR(200) NOT NULL,
  PRIMARY KEY (Role_ID)
);

CREATE TABLE Permissions (
  ID          INT NOT NULL,
  Name        VARCHAR(200) NOT NULL,
  Description VARCHAR(2000) NULL,
  PRIMARY KEY (ID)
);

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
);


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
);


-- Logs (User 1:M Logs, Logs M:1 Rooms)

CREATE TABLE Logs (
  LogID            INT NOT NULL AUTO_INCREMENT,
  LogDate          DATE NOT NULL,
  UserEmail        VARCHAR(320) NOT NULL,
  PRIMARY KEY (LogID),

  CONSTRAINT fk_logs_user
    FOREIGN KEY (UserEmail) REFERENCES Users(Email)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE LogIn (
  LogID     INT NOT NULL,
  LoginTime TIME NOT NULL,
  PRIMARY KEY (LogID),
  CONSTRAINT fk_login_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE LogOut (
  LogID      INT NOT NULL,
  LogoutTime TIME NOT NULL,
  PRIMARY KEY (LogID),
  CONSTRAINT fk_logout_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE Colleges (
  AbbreviatedName VARCHAR(200) NOT NULL,
  FullName VARCHAR(200) NOT NULL,
  PRIMARY KEY (AbbreviatedName)
);

CREATE TABLE Departments (
  DepartmentName    VARCHAR(200) NOT NULL,
  College VARCHAR(200) NOT NULL,
  PRIMARY KEY (DepartmentName),
  CONSTRAINT fk_departments_college
    FOREIGN KEY (College) REFERENCES Colleges(AbbreviatedName)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


-- Buildings

CREATE TABLE Buildings (
  BuildingNumber INT NOT NULL,
  Name           VARCHAR(200) NOT NULL,
  NumOfFloors     INT NOT NULL,
  PRIMARY KEY (BuildingNumber),
  CONSTRAINT chk_buildings_numfloors
    CHECK (NumOfFloors > 0)
);

-- Floors (weak under Building)

CREATE TABLE Floors (
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  PRIMARY KEY (BuildingNumber, FloorNumber),
  CONSTRAINT fk_floors_building
    FOREIGN KEY (BuildingNumber) REFERENCES Buildings(BuildingNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);


-- FloorPlans (1:1 with Floors)

CREATE TABLE FloorPlans (
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  FileName       VARCHAR(500) NOT NULL,
  FilePath       VARCHAR(1000) NOT NULL,

  PRIMARY KEY (BuildingNumber, FloorNumber),

  CONSTRAINT fk_floorplans_floor
    FOREIGN KEY (BuildingNumber, FloorNumber)
    REFERENCES Floors(BuildingNumber, FloorNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);



-- RoomType
CREATE TABLE RoomType (
  RoomUseCode INT NOT NULL,
  Name VARCHAR(200) NOT NULL,
  PRIMARY KEY (RoomUseCode)
);

-- Rooms (weak under Buildings)
CREATE TABLE Rooms (
  BuildingNumber  INT NOT NULL,
  RoomNumber      INT NOT NULL,
  FloorNumber     INT NOT NULL,      

  DepartmentName  VARCHAR(200) NULL,
  RoomUseCode     INT NULL,

  SquareFeet      INT NULL,
  Notes           VARCHAR(2000) NULL,
  Occupancy       INT NULL,

  PRIMARY KEY (BuildingNumber, RoomNumber),

  CONSTRAINT fk_rooms_building
    FOREIGN KEY (BuildingNumber)
    REFERENCES Buildings(BuildingNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_rooms_floor
    FOREIGN KEY (BuildingNumber, FloorNumber)
    REFERENCES Floors(BuildingNumber, FloorNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_rooms_department
    FOREIGN KEY (DepartmentName) REFERENCES Departments(DepartmentName)
    ON UPDATE CASCADE
    ON DELETE SET NULL,

  CONSTRAINT fk_rooms_type
    FOREIGN KEY (RoomUseCode) REFERENCES RoomType(RoomUseCode)
    ON UPDATE CASCADE
    ON DELETE SET NULL
);


CREATE TABLE RoomImage (
  BuildingNumber INT NOT NULL,
  RoomNumber INT NOT NULL,
  
  ImageURL VARCHAR(500) NOT NULL,

  PRIMARY KEY(BuildingNumber, RoomNumber, ImageURL),

  CONSTRAINT fk_roomimage_room
    FOREIGN KEY (BuildingNumber, RoomNumber) 
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Equipment (M:N)

CREATE TABLE Equipment (
  EType        VARCHAR(100) NOT NULL,
  EDescription VARCHAR(1000) NULL,
  Sensitive   BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (EType)
);

CREATE TABLE RoomsHaveEquipment (
  BuildingNumber INT NOT NULL,
  RoomNumber     INT NOT NULL,
  EType           VARCHAR(100) NOT NULL,
  PRIMARY KEY (BuildingNumber, RoomNumber, EType),
  CONSTRAINT fk_rhe_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_rhe_equipment
    FOREIGN KEY (EType) REFERENCES Equipment(EType)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE Employees (
  Email          VARCHAR(320) NOT NULL,
  FullName       VARCHAR(200) NOT NULL,
  DepartmentName VARCHAR(200) NOT NULL,
  College        VARCHAR(200) NOT NULL,
  PRIMARY KEY (Email),

  CONSTRAINT fk_emp_dept
    FOREIGN KEY (DepartmentName) REFERENCES Departments(DepartmentName)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_emp_college
    FOREIGN KEY (College) REFERENCES Colleges(AbbreviatedName)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- Roles, Permissions, RolePermissions (Roles given Permissions)

CREATE TABLE Roles (
  Role_ID   VARCHAR(50) NOT NULL,
  RoleName  VARCHAR(200) NOT NULL,
  PRIMARY KEY (Role_ID)
);

CREATE TABLE Permissions (
  ID          INT NOT NULL,
  Name        VARCHAR(200) NOT NULL,
  Description VARCHAR(2000) NULL,
  PRIMARY KEY (ID)
);

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
);


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
);


-- Logs (User 1:M Logs, Logs M:1 Rooms)

CREATE TABLE Logs (
  LogId            INT NOT NULL AUTO_INCREMENT,
  LogDate          DATE NOT NULL,
  UserEmail        VARCHAR(320) NOT NULL,
  PRIMARY KEY (LogId),

  CONSTRAINT fk_logs_user
    FOREIGN KEY (UserEmail) REFERENCES Users(Email)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE LogIn (
  LogID     INT NOT NULL,
  LoginTime TIME NOT NULL,
  PRIMARY KEY (LogID),
  CONSTRAINT fk_login_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE LogOut (
  LogID      INT NOT NULL,
  LogoutTime TIME NOT NULL,
  PRIMARY KEY (LogID),
  CONSTRAINT fk_logout_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE LogEmplToRoom (
  LogID             INT NOT NULL,
  EmployeeEmail     VARCHAR(320) NOT NULL,

  OldBuildingNumber INT NOT NULL,
  OldRoomNumber     INT NOT NULL,

  NewBuildingNumber INT NOT NULL,
  NewRoomNumber     INT NOT NULL,

  PRIMARY KEY (LogID),

  CONSTRAINT fk_ler_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,

  CONSTRAINT fk_ler_employee
    FOREIGN KEY (EmployeeEmail) REFERENCES Employees(Email)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  -- Old room must exist
  CONSTRAINT fk_ler_old_room
    FOREIGN KEY (OldBuildingNumber, OldRoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  -- New room must exist
  CONSTRAINT fk_ler_new_room
    FOREIGN KEY (NewBuildingNumber, NewRoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE LogDeptToRoom (
  LogID          INT NOT NULL,
  OldDepartment  VARCHAR(200) NOT NULL,
  NewDepartment  VARCHAR(200) NOT NULL,
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  RoomNumber     INT NOT NULL,
  PRIMARY KEY (LogID),
  CONSTRAINT fk_ldr_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_ldr_room
    FOREIGN KEY (BuildingNumber, FloorNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, FloorNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE LogEqpmtToRoom (
  LogID          INT NOT NULL,
  EquipmentType  VARCHAR(100) NOT NULL,
  OldQuantity    INT NOT NULL,
  NewQuantity    INT NOT NULL,
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  RoomNumber     INT NOT NULL,
  PRIMARY KEY (LogID),
  CONSTRAINT fk_leq_log
    FOREIGN KEY (LogID) REFERENCES Logs(LogID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_leq_room
    FOREIGN KEY (BuildingNumber, FloorNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, FloorNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);