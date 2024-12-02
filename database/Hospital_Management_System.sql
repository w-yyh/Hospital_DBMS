
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `departments`
-- ----------------------------
DROP TABLE IF EXISTS `departments`;
CREATE TABLE `departments` (
  `department_id` int NOT NULL,
  `department_name` varchar(100) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of departments
-- ----------------------------
INSERT INTO `departments` VALUES ('1', 'C12', null);
INSERT INTO `departments` VALUES ('2', 'C11', null);
INSERT INTO `departments` VALUES ('3', 'C10', null);
INSERT INTO `departments` VALUES ('4', 'C9', null);

-- ----------------------------
-- Table structure for `doctors`
-- ----------------------------
DROP TABLE IF EXISTS `doctors`;
CREATE TABLE `doctors` (
  `doctor_id` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `contact_number` varchar(15) DEFAULT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `department_id` int DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`doctor_id`),
  KEY `department_id` (`department_id`),
  CONSTRAINT `doctors_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of doctors
-- ----------------------------
INSERT INTO `doctors` VALUES ('1', 'Ronaldo', '1985-02-05', '13012345678', 'Surgery', '2', 'Ronaldo@qq.com');
INSERT INTO `doctors` VALUES ('2', 'James', '1998-02-26', '13312345678', 'Ophthalmology', '1', 'James@qq.com');
INSERT INTO `doctors` VALUES ('3', 'Terry', '1990-01-26', '13212345678', 'Surgery', '2', 'Terry123@qq.com');
INSERT INTO `doctors` VALUES ('4', 'Brown', '1999-01-15', '15382114568', 'Respiratory medicine', '4', 'Brown@qq.com');

-- ----------------------------
-- Table structure for `nurses`
-- ----------------------------
DROP TABLE IF EXISTS `nurses`;
CREATE TABLE `nurses` (
  `nurse_id` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `contact_number` varchar(15) DEFAULT NULL,
  `assigned_room` int DEFAULT NULL,
  PRIMARY KEY (`nurse_id`),
  KEY `assigned_room` (`assigned_room`),
  CONSTRAINT `nurses_ibfk_1` FOREIGN KEY (`assigned_room`) REFERENCES `rooms` (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of nurses
-- ----------------------------
INSERT INTO `nurses` VALUES ('1', 'Amy', '15312345678', '1');
INSERT INTO `nurses` VALUES ('2', 'Jennie', '13312345678', '2');
INSERT INTO `nurses` VALUES ('3', 'Iris', '15512345678', '3');
INSERT INTO `nurses` VALUES ('4', 'May', '17812345678', '4');
INSERT INTO `nurses` VALUES ('5', 'Rose', '17012345678', '2');

-- ----------------------------
-- Table structure for `patients`
-- ----------------------------
DROP TABLE IF EXISTS `patients`;
CREATE TABLE `patients` (
  `patient_id` int NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `contact_number` varchar(15) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `gender` char(1) DEFAULT NULL,
  `admission_date` date DEFAULT NULL,
  `discharge_date` date DEFAULT NULL,
  `treatment_record` text,
  PRIMARY KEY (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of patients
-- ----------------------------
INSERT INTO `patients` VALUES ('1', 'Cris', '2004-10-01', '13312345678', '华工', '男', '2024-11-23', '2024-11-30', '已做骨折手术');
INSERT INTO `patients` VALUES ('2', 'Andy', '2004-05-03', '15412345678', '中大', '男', '2024-11-14', '2024-11-21', '发烧药物治疗');
INSERT INTO `patients` VALUES ('3', 'Andony', '1996-09-19', '18925413321', '小谷围街道', '男', '2024-11-28', null, '药物治疗');

-- ----------------------------
-- Table structure for `patient_doctor`
-- ----------------------------
DROP TABLE IF EXISTS `patient_doctor`;
CREATE TABLE `patient_doctor` (
  `patient_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `visit_date` date DEFAULT NULL,
  `diagnosis` text,
  PRIMARY KEY (`patient_id`,`doctor_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `patient_doctor_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `patient_doctor_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of patient_doctor
-- ----------------------------
INSERT INTO `patient_doctor` VALUES ('1', '2', '2024-11-24', '手指骨折');
INSERT INTO `patient_doctor` VALUES ('2', '4', '2024-11-27', '发烧');
INSERT INTO `patient_doctor` VALUES ('3', '4', '2024-11-28', '发烧');

-- ----------------------------
-- Table structure for `patient_room`
-- ----------------------------
DROP TABLE IF EXISTS `patient_room`;
CREATE TABLE `patient_room` (
  `patient_id` int NOT NULL,
  `room_id` int NOT NULL,
  `admission_date` date DEFAULT NULL,
  `discharge_date` date DEFAULT NULL,
  PRIMARY KEY (`patient_id`,`room_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `patient_room_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `patient_room_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of patient_room
-- ----------------------------
INSERT INTO `patient_room` VALUES ('1', '2', '2024-11-23', '2024-11-30');
INSERT INTO `patient_room` VALUES ('2', '2', '2024-11-14', '2024-11-21');
INSERT INTO `patient_room` VALUES ('3', '2', '2024-11-28', null);

-- ----------------------------
-- Table structure for `rooms`
-- ----------------------------
DROP TABLE IF EXISTS `rooms`;
CREATE TABLE `rooms` (
  `room_id` int NOT NULL,
  `room_type` varchar(50) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `room_number` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of rooms
-- ----------------------------
INSERT INTO `rooms` VALUES ('1', 'ICU', '2', '301');
INSERT INTO `rooms` VALUES ('2', 'General_Ward', '8', '201');
INSERT INTO `rooms` VALUES ('3', 'isolation ward\r\nisolation ward\r\nIsolation_ward', '1', '501');
INSERT INTO `rooms` VALUES ('4', 'BCTU', '4', '401');
DROP TRIGGER IF EXISTS `SyncAdmissionDate`;
DELIMITER ;;
CREATE TRIGGER `SyncAdmissionDate` AFTER UPDATE ON `patients` FOR EACH ROW BEGIN
    IF OLD.admission_date != NEW.admission_date THEN
        UPDATE Patient_Room
        SET admission_date = NEW.admission_date
        WHERE patient_id = NEW.patient_id;
    END IF;
END
;;
DELIMITER ;
DROP TRIGGER IF EXISTS `SyncDischargeDate`;
DELIMITER ;;
CREATE TRIGGER `SyncDischargeDate` AFTER UPDATE ON `patients` FOR EACH ROW BEGIN
    IF OLD.discharge_date != NEW.discharge_date THEN
        UPDATE Patient_Room
        SET discharge_date = NEW.discharge_date
        WHERE patient_id = NEW.patient_id;
    END IF;
END
;;
DELIMITER ;
