INSERT INTO RoomsAreEquippedWithEquipment (BuildingNumber, RoomNumber, EId, Quantity, BackupPower, PrimaryID, SecondaryID) 
SELECT '033-0', '0357-B0', e.EId, 1, 'No', p1.PersonID, p2.PersonID
FROM Equipment e
JOIN People p1 ON p1.FullName = 'John Merriam'
JOIN People p2 ON p2.FullName = 'Craig Jacobson'
WHERE e.EType = 'Refrigerator and/or Freezer'
ON DUPLICATE KEY UPDATE Quantity=VALUES(Quantity), BackupPower=VALUES(BackupPower), PrimaryID=VALUES(PrimaryID), SecondaryID=VALUES(SecondaryID);
