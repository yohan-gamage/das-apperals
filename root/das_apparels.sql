-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 02, 2026 at 03:06 AM
-- Server version: 8.0.45
-- PHP Version: 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `das_apparels`
--

-- --------------------------------------------------------

--
-- Table structure for table `asset`
--

DROP TABLE IF EXISTS `asset`;
CREATE TABLE IF NOT EXISTS `asset` (
  `assetID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `category` varchar(16) NOT NULL,
  `locationID` int NOT NULL,
  PRIMARY KEY (`assetID`),
  KEY `assetlocation` (`locationID`)
) ENGINE=InnoDB AUTO_INCREMENT=116 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `asset`
--

INSERT INTO `asset` (`assetID`, `name`, `category`, `locationID`) VALUES
(101, 'Laser Cutter 5000', 'Cutting', 1),
(102, 'Brother S-7100A', 'Sewing', 2),
(103, 'Steam Station Alpha', 'Finishing', 3),
(104, 'Juki DDL-8700', 'Sewing', 2),
(105, 'Auto Spreader', 'Cutting', 1),
(106, 'Overlock 4-Thread', 'Sewing', 2),
(107, 'Air Compressor 20HP', 'Utility', 5),
(108, 'Heat Press Pro', 'Printing', 1),
(109, 'Vacuum Sealer', 'Packaging', 4),
(110, 'QC Light Box', 'Quality', 1),
(111, 'Button Holer', 'Sewing', 2),
(112, 'Boiler System', 'Utility', 5),
(113, 'Forklift #1', 'Logistics', 4),
(114, 'Fabric Drill', 'Cutting', 1),
(115, 'Snap Fastener', 'Sewing', 2);

-- --------------------------------------------------------

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
CREATE TABLE IF NOT EXISTS `employee` (
  `employeeID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `speciality` varchar(16) NOT NULL,
  `username` varchar(16) NOT NULL,
  `passwordHash` varchar(16) NOT NULL,
  `salt` varchar(16) NOT NULL,
  PRIMARY KEY (`employeeID`)
) ENGINE=InnoDB AUTO_INCREMENT=345 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `employee`
--

INSERT INTO `employee` (`employeeID`, `name`, `speciality`, `username`, `passwordHash`, `salt`) VALUES
(1, 'System Administrator', 'Admin', 'superadmin', 'admin789', ''),
(2, 'Maintenance Supervisor', 'Maintenance', 'maintenance', '1234', ''),
(3, 'Manager', 'Management', 'management', '1234', ''),
(4, 'Employee', 'Electrical', 'employee', '1234', ''),
(5, 'John Smith', 'Electrical', 'jsmith', 'hash1', 's1'),
(6, 'Maria Garcia', 'Mechanical', 'mgarcia', 'hash2', 's2'),
(7, 'Alex Chen', 'Pneumatics', 'achen', 'hash3', 's3'),
(8, 'Sarah Bilal', 'Electronics', 'sbilal', 'hash4', 's4'),
(9, 'Kevin Voght', 'General', 'kvoght', 'hash5', 's5'),
(10, 'Linda Wu', 'Sewing Tech', 'lwu', 'hash6', 's6'),
(11, 'Raj Patel', 'Electrical', 'rpatel', 'hash7', 's7'),
(12, 'Elena Rossi', 'Hydraulics', 'erossi', 'hash8', 's8'),
(13, 'Tom Baker', 'Mechanical', 'tbaker', 'hash9', 's9'),
(14, 'Sam Rivera', 'HVAC', 'srivera', 'hash10', 's10'),
(112, 'Yohan Gamage', 'Maintenance', 'yohangamage', 'yohan1234', ''),
(114, 'Yohan', 'HVAC', 'yohan', '1234', ''),
(344, 'Yohan', 'Plumbing', 'abcd', '1234', '');

-- --------------------------------------------------------

--
-- Table structure for table `jobassignment`
--

DROP TABLE IF EXISTS `jobassignment`;
CREATE TABLE IF NOT EXISTS `jobassignment` (
  `jobID` int NOT NULL,
  `employeeID` int NOT NULL,
  `assignedDate` date DEFAULT NULL,
  PRIMARY KEY (`jobID`,`employeeID`),
  KEY `memployee_employee` (`employeeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `jobassignment`
--

INSERT INTO `jobassignment` (`jobID`, `employeeID`, `assignedDate`) VALUES
(901, 5, '2026-03-21'),
(902, 13, '2026-03-27'),
(904, 4, '2026-03-29'),
(905, 4, '2026-03-30'),
(906, 5, '2026-03-27'),
(907, 4, '2026-03-29'),
(908, 6, '2026-03-27');

-- --------------------------------------------------------

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
CREATE TABLE IF NOT EXISTS `location` (
  `locationID` int NOT NULL AUTO_INCREMENT,
  `locationName` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `description` varchar(64) NOT NULL,
  PRIMARY KEY (`locationID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `location`
--

INSERT INTO `location` (`locationID`, `locationName`, `description`) VALUES
(1, 'Cutting Room', 'Fabric layering and laser cutting area.'),
(2, 'Sewing Floor A', 'Main assembly line for tops and shirts.'),
(3, 'Finishing & Ironing', 'Steam pressing and final touch-ups.'),
(4, 'Warehouse', 'Raw material and finished goods storage.'),
(5, 'Utility Room', 'Housing for compressors and HVAC systems.');

-- --------------------------------------------------------

--
-- Table structure for table `maintenancejob`
--

DROP TABLE IF EXISTS `maintenancejob`;
CREATE TABLE IF NOT EXISTS `maintenancejob` (
  `jobID` int NOT NULL AUTO_INCREMENT,
  `description` varchar(64) NOT NULL,
  `report_date` date DEFAULT NULL,
  `status` varchar(16) NOT NULL,
  `assetID` int NOT NULL,
  PRIMARY KEY (`jobID`),
  KEY `MaintenanceAsset` (`assetID`)
) ENGINE=InnoDB AUTO_INCREMENT=915 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `maintenancejob`
--

INSERT INTO `maintenancejob` (`jobID`, `description`, `report_date`, `status`, `assetID`) VALUES
(901, 'Sensor replacement', '2026-03-20', 'Done', 101),
(902, 'Drive belt slip', '2026-03-21', 'Ongoing', 107),
(903, 'Needle strike', '2026-03-22', 'Pending', 104),
(904, 'Leaking steam valve', '2026-03-23', 'Done', 103),
(905, 'Hydraulic leak', '2026-03-24', 'Ongoing', 113),
(906, 'PCB repair', '2026-03-25', 'Ongoing', 108),
(907, 'Calibration', '2026-03-26', 'Done', 110),
(908, 'Filter cleaning', '2026-03-27', 'Pending', 112);

-- --------------------------------------------------------

--
-- Table structure for table `report`
--

DROP TABLE IF EXISTS `report`;
CREATE TABLE IF NOT EXISTS `report` (
  `reportID` int NOT NULL AUTO_INCREMENT,
  `AssetID` int NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `mobileNumber` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` varchar(32) NOT NULL,
  `reportDate` date NOT NULL,
  PRIMARY KEY (`reportID`),
  UNIQUE KEY `unique_asset_daily` (`AssetID`,`reportDate`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `report`
--

INSERT INTO `report` (`reportID`, `AssetID`, `description`, `mobileNumber`, `status`, `reportDate`) VALUES
(1, 102, '', '0704652088', 'Request Reviewed', '2026-03-28'),
(2, 104, '', '0704652088', 'Request Reviewed', '2026-03-28'),
(3, 110, '', '', 'Request Reviewed', '2026-03-29'),
(4, 109, '', '0704652088', 'Request Reviewed', '2026-03-29'),
(5, 102, 'abc', '0704652088', 'Pending', '2026-03-30');

-- --------------------------------------------------------

--
-- Table structure for table `tool`
--

DROP TABLE IF EXISTS `tool`;
CREATE TABLE IF NOT EXISTS `tool` (
  `toolID` int NOT NULL AUTO_INCREMENT,
  `tool_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `AvailableQuantity` int NOT NULL,
  PRIMARY KEY (`toolID`)
) ENGINE=InnoDB AUTO_INCREMENT=206 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `tool`
--

INSERT INTO `tool` (`toolID`, `tool_name`, `AvailableQuantity`) VALUES
(201, 'Digital Multimeter', 5),
(202, 'Impact Wrench', 0),
(203, 'Precision Driver Set', 9),
(204, 'Soldering Iron', 4),
(205, 'Pressure Gauge', 6);

-- --------------------------------------------------------

--
-- Table structure for table `toolusage`
--

DROP TABLE IF EXISTS `toolusage`;
CREATE TABLE IF NOT EXISTS `toolusage` (
  `usageID` int NOT NULL AUTO_INCREMENT,
  `jobID` int NOT NULL,
  `toolID` int NOT NULL,
  `borrowDate` date NOT NULL,
  `returnDate` date DEFAULT NULL,
  `quantity` int NOT NULL,
  `damage_comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`usageID`),
  KEY `toolusagejob` (`jobID`),
  KEY `toolusagetool` (`toolID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `toolusage`
--

INSERT INTO `toolusage` (`usageID`, `jobID`, `toolID`, `borrowDate`, `returnDate`, `quantity`, `damage_comment`) VALUES
(3, 901, 201, '2026-03-22', '2026-03-27', 1, ''),
(4, 901, 203, '2026-03-22', '2026-03-27', 1, ''),
(5, 901, 204, '2026-03-23', '2026-03-27', 1, 'Heating failure'),
(6, 908, 202, '2026-03-27', NULL, 3, NULL);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `asset`
--
ALTER TABLE `asset`
  ADD CONSTRAINT `assetlocation` FOREIGN KEY (`locationID`) REFERENCES `location` (`locationID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `jobassignment`
--
ALTER TABLE `jobassignment`
  ADD CONSTRAINT `memployee_employee` FOREIGN KEY (`employeeID`) REFERENCES `employee` (`employeeID`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `mtool_job` FOREIGN KEY (`jobID`) REFERENCES `maintenancejob` (`jobID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `maintenancejob`
--
ALTER TABLE `maintenancejob`
  ADD CONSTRAINT `MaintenanceAsset` FOREIGN KEY (`assetID`) REFERENCES `asset` (`assetID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `report`
--
ALTER TABLE `report`
  ADD CONSTRAINT `reportAsset` FOREIGN KEY (`AssetID`) REFERENCES `asset` (`assetID`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Constraints for table `toolusage`
--
ALTER TABLE `toolusage`
  ADD CONSTRAINT `toolusagejob` FOREIGN KEY (`jobID`) REFERENCES `maintenancejob` (`jobID`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  ADD CONSTRAINT `toolusagetool` FOREIGN KEY (`toolID`) REFERENCES `tool` (`toolID`) ON DELETE RESTRICT ON UPDATE RESTRICT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
