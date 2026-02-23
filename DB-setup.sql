CREATE TABLE Colleges (
  AbbreviatedName VARCHAR(200) NOT NULL UNIQUE,
  FullName VARCHAR(200) NOT NULL,
  PRIMARY KEY (AbbreviatedName)
);

CREATE TABLE Departments (
  DepartmentName    VARCHAR(200) NOT NULL,
  College VARCHAR(200) NOT NULL,
  PRIMARY KEY (DepartmentName, College),
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
  FileName       VARCHAR(500) NOT NULL,
  FilePath       VARCHAR(1000) NOT NULL,
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
  SquareFeet      FLOAT,
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
    ON DELETE SET NULL
);


CREATE TABLE RoomImage (
  FileName VARCHAR(500) NOT NULL,
  BuildingNumber INT NOT NULL,
  RoomNumber INT NOT NULL,

  PRIMARY KEY(FileName),

  CONSTRAINT fk_roomimage_room
    FOREIGN KEY (BuildingNumber, RoomNumber) 
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE RoomCoordinates (
  BuildingNum INT NOT NULL,
  RoomNumber VARCHAR(50) NOT NULL,
  TopLeftX INT NOT NULL,
  TopLeftY INT NOT NULL,
  BottomRightX INT NOT NULL,
  BottomRightY INT NOT NULL,
  PRIMARY KEY (BuildingNum, RoomNumber),
  CONSTRAINT fk_roomcoordinates_room
    FOREIGN KEY (BuildingNum, RoomNumber) 
    REFERENCES Rooms(BuildingNumber, RoomNumber)
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

-- Equipment (M:N)

CREATE TABLE Equipment (
  EType        VARCHAR(100) NOT NULL,
  EDescription VARCHAR(1000) NULL,
  Sensitive   VARCHAR(50) NOT NULL DEFAULT 'No',
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
  EmpID        INT NOT NULL AUTO_INCREMENT,
  Email          VARCHAR(320) NOT NULL,
  FullName       VARCHAR(200) NOT NULL,
  DepartmentName VARCHAR(200) NOT NULL,
  College        VARCHAR(200) NOT NULL,
  PRIMARY KEY (EmpID),

  CONSTRAINT fk_emp_dept
    FOREIGN KEY (DepartmentName, College) REFERENCES Departments(DepartmentName, College)
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



-- Relationship Set Tables (M:M or 1:M without participation constraints)
CREATE TABLE EmployeesAssignedToRooms (
  EmpID INT NOT NULL,
  RoomNum VARCHAR(50) NOT NULL,
  BuildingNum INT NOT NULL,
  PRIMARY KEY (EmpID, RoomNum, BuildingNum),
  CONSTRAINT fk_eatr_emp
    FOREIGN KEY (EmpID) REFERENCES Employees(EmpID)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_eatr_room
    FOREIGN KEY (BuildingNum, RoomNum) REFERENCES Rooms(BuildingNumber, RoomNumber)
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
    FOREIGN KEY (DepartmentName, College) REFERENCES Departments(DepartmentName, College)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);