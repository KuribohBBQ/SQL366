-- insert data into college table
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('BCSM', 'Bailey College of Science and Mathematics');
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('CENG', 'College of Engineering');
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('OCOB', 'Orfalea College of Business');
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('CAFES', 'College of Agriculture, Food and Environmental Sciences');
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('CAED', 'College of Architecture and Environmental Design');
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('CLA', 'College of Liberal Arts');
INSERT INTO Colleges (AbbreviatedName, FullName)
VALUES ('UNKN', 'Unknown College');
-- insert data into department table
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (109400, 'Liberal Studies', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (115100, 'Biological Sciences', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (115200, 'Chemistry & Biochemistry', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (115300, 'Statistics', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (115400, 'Mathematics', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (115500, 'Physics', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (115600, 'Kinesiology & Public Hlth', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117500, 'College General Use', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117501, 'Advising Center', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117502, 'Deans Office', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117503, 'Computing Support Services', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117504, 'Advancement', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117506, 'Cntr for Cstal Marine Sci', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117507, 'Health Professions', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117508, 'Ctr Sci-Math Teacher Educ', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117509, 'Math Science Teacher Int', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117511, 'LSAMP', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117512, 'STAR', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117513, 'Design & Fabrication Fácil', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (117600, 'School of Education', 'BCSM');
INSERT INTO Departments_Subdivisions (DeptID, DepartmentName, College) VALUES (999999, 'Unknown Department', 'UNKN');
