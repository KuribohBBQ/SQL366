CREATE TABLE Colleges (
  AbbreviatedName VARCHAR(200) NOT NULL UNIQUE,
  FullName VARCHAR(200) NOT NULL,
  PRIMARY KEY (AbbreviatedName)
);

CREATE TABLE Departments_Subdivisions_Subdivisions (
  DepartmentName    VARCHAR(200) NOT NULL,
  College VARCHAR(200) NOT NULL,
  PRIMARY KEY (DepartmentName, College),
  CONSTRAINT fk_Departments_Subdivisions_college
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
  FileName       VARCHAR(500) NOT NULL,
  BuildingNumber INT NOT NULL,
  FloorNumber    INT NOT NULL,
  PRIMARY KEY (FileName),
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
  RoomNumber      VARCHAR(50) NOT NULL,
  FloorNumber     INT NOT NULL,      
  RoomUseCode     INT NOT NULL,
  SquareFeet      DECIMAL(10,2) NULL,
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

  CONSTRAINT fk_rooms_type
    FOREIGN KEY (RoomUseCode) REFERENCES RoomType(RoomUseCode)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


CREATE TABLE RoomImage (
  ImageURL VARCHAR(500) NOT NULL,
  BuildingNumber INT NOT NULL,
  RoomNumber VARCHAR(50) NOT NULL,

  PRIMARY KEY(ImageURL),

  CONSTRAINT fk_roomimage_room
    FOREIGN KEY (BuildingNumber, RoomNumber) 
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE RoomCoordinates (
  BuildingNumber INT NOT NULL,
  RoomNumber VARCHAR(50) NOT NULL,
  TopLeftX INT NOT NULL,
  TopLeftY INT NOT NULL,
  BottomRightX INT NOT NULL,
  BottomRightY INT NOT NULL,
  PRIMARY KEY (BuildingNumber, RoomNumber),
  CONSTRAINT fk_roomcoordinates_room
    FOREIGN KEY (BuildingNumber, RoomNumber) 
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Equipment (M:N)

CREATE TABLE Equipment (
  EType        VARCHAR(100) NOT NULL,
  EDescription VARCHAR(1000) NULL,
  IsSensitive    TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (EType)
);


CREATE TABLE Employees (
  EmpID        INT NOT NULL AUTO_INCREMENT,
  Email          VARCHAR(320) NOT NULL UNIQUE,
  FullName       VARCHAR(200) NOT NULL,
  DepartmentName VARCHAR(200) NOT NULL,
  College        VARCHAR(200) NOT NULL,
  PRIMARY KEY (EmpID),

  CONSTRAINT fk_emp_dept
    FOREIGN KEY (DepartmentName, College) REFERENCES Departments_Subdivisions_Subdivisions(DepartmentName, College)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- Roles, Permissions, RolePermissions (Roles given Permissions)

CREATE TABLE Roles (
  Role_ID   VARCHAR(50) NOT NULL,
  RoleName  VARCHAR(200) NOT NULL,
  PRIMARY KEY (Role_ID)
);



-- Users assigned to Roles (M:1)

CREATE TABLE Users (
  UserID   INT NOT NULL AUTO_INCREMENT,
  Email     VARCHAR(320) NOT NULL,
  Name      VARCHAR(200) NOT NULL,
  Password  VARCHAR(255) NOT NULL,  -- store hash
  Role_ID   VARCHAR(50) NOT NULL,
  PRIMARY KEY (UserID),
  CONSTRAINT fk_users_role
    FOREIGN KEY (Role_ID) REFERENCES Roles(Role_ID)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);


-- Logs (User 1:M Logs, Logs M:1 Rooms)
CREATE TABLE Logs(
  ID INT NOT NULL AUTO_INCREMENT,
  Date DATE NOT NULL DEFAULT (CURRENT_DATE),
  LogIn TIME NOT NULL DEFAULT (CURRENT_TIME),
  LogOut TIME,
  UserID INT NOT NULL,
  AssignOrDelete VARCHAR(10), -- 'Assign' or 'Delete'
  BuildingNumber INT,
  RoomNumber VARCHAR(50),
  EmpID INT,
  DepartmentName VARCHAR(200),
  College VARCHAR(200),
  EType VARCHAR(100),
  Quantity INT,
  PRIMARY KEY (ID),
  CONSTRAINT fk_logs_user
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT fk_logs_room
    FOREIGN KEY (BuildingNumber, RoomNumber) REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT fk_logs_emp
    FOREIGN KEY (EmpID) REFERENCES Employees(EmpID)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT fk_logs_dept
    FOREIGN KEY (DepartmentName, College) REFERENCES Departments_Subdivisions_Subdivisions(DepartmentName, College)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT fk_logs_equipment
    FOREIGN KEY (EType) REFERENCES Equipment(EType)
    ON UPDATE CASCADE
    ON DELETE SET NULL


);


-- Relationship Set Tables (M:M or 1:M without participation constraints)
CREATE TABLE EmployeesAssignedToRooms (
  EmpID INT NOT NULL,
  RoomNumber VARCHAR(50) NOT NULL,
  BuildingNumber INT NOT NULL,
  PRIMARY KEY (EmpID, RoomNumber, BuildingNumber),
  CONSTRAINT fk_eatr_emp
    FOREIGN KEY (EmpID) REFERENCES Employees(EmpID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_eatr_room
    FOREIGN KEY (BuildingNumber, RoomNumber) REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE RoomsAreEquippedWithEquipment (
  BuildingNumber INT NOT NULL,
  RoomNumber     VARCHAR(50) NOT NULL,
  EType           VARCHAR(100) NOT NULL,
  Quantity        INT NOT NULL DEFAULT 1,
  PRIMARY KEY (BuildingNumber, RoomNumber, EType),
  CONSTRAINT fk_raew_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_raew_equipment
    FOREIGN KEY (EType) REFERENCES Equipment(EType)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

CREATE TABLE RoomsAreAssignedToDepts_Subdiv (
  BuildingNumber INT NOT NULL,
  RoomNumber     VARCHAR(50) NOT NULL,
  DepartmentName VARCHAR(200) NOT NULL,
  College        VARCHAR(200) NOT NULL,
  PRIMARY KEY (BuildingNumber, RoomNumber, DepartmentName, College),
  CONSTRAINT fk_raadt_room
    FOREIGN KEY (BuildingNumber, RoomNumber)
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_raadt_dept
    FOREIGN KEY (DepartmentName, College) REFERENCES Departments_Subdivisions_Subdivisions(DepartmentName, College)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);