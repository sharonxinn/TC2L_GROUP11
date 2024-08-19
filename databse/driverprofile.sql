CREATE TABLE `driverprofile` (
  `fullName` varchar(50) NOT NULL,
  `gender` enum('male','female') NOT NULL,
  `dateandTime` datetime NOT NULL,
  `pickup` enum('HB1','HB2','HB3','HB4','FCI','STADIUM','DTC','Dpulze','TamarindSquare','MutiaraVille','TheArc') NOT NULL,
  `dropoff` enum('HB1','HB2','HB3','HB4','FCI','STADIUM','DTC','Dpulze','TamarindSquare','MutiaraVille','TheArc') NOT NULL,
  `carplate` varchar(50) NOT NULL,
  `carmodel` varchar(50) NOT NULL,
  `totalperson` int(10) NOT NULL,
  `fees` enum('Free','RM1') NOT NULL,
  `qrcode` longblob NOT NULL,
  `message` varchar(100) NOT NULL
)