<?php
    $dbhost = ;  // mysql服务器主机地址
    $dbuser = ;            // mysql用户名
    $dbpass = '';          // mysql用户名密码
    $conn = mysqli_connect($dbhost, $dbuser, $dbpass);
    if(! $conn )
    {
    die('Connection Failed ' . mysqli_error($conn));
    }
    echo 'CONNECTION SUCESS<br />';
    $sql = 'CREATE DATABASE IDENTITY';
    $retval = mysqli_query($conn,$sql );
    if(! $retval )
    {
        die('CREATING DATABASE FAILED: ' . mysqli_error($conn));
    }
    echo "CREATING DATABASE SUCESS\n";
		$sql = "CREATE TABLE driverprofile( ".
				"fullName` varchar(50) NOT NULL, ".
				"gender` enum('male','female') NOT NULL, ".
				"dateandTime` datetime NOT NULL, ".
				"pickup` enum('HB1','HB2','HB3','HB4','FCI','STADIUM','DTC','Dpulze','TamarindSquare','MutiaraVille','TheArc') NOT NULL, ".
				"dropoff` enum('HB1','HB2','HB3','HB4','FCI','STADIUM','DTC','Dpulze','TamarindSquare','MutiaraVille','TheArc') NOT NULL, ".
				"carplate` varchar(50) NOT NULL, ".
				"carmodel` varchar(50) NOT NULL, ".
				"totalperson` int(10) NOT NULL,".
				"fees` enum('Free','RM1') NOT NULL,".
				"qrcode` int NOT NULL,".
				"message` varchar(100) NOT NULL; ";
		

        $sql = "CREATE TABLE passengerprofile( ".
				"fullName` varchar(50) NOT NULL, ".
				"gender` enum('male','female') NOT NULL, ".
				"dateandTime` datetime NOT NULL, ".
				"pickup` enum('HB1','HB2','HB3','HB4','FCI','STADIUM','DTC','Dpulze','TamarindSquare','MutiaraVille','TheArc') NOT NULL, ".
				"dropoff` enum('HB1','HB2','HB3','HB4','FCI','STADIUM','DTC','Dpulze','TamarindSquare','MutiaraVille','TheArc') NOT NULL, ".
				"totalperson` int(10) NOT NULL,".
				"message` varchar(100) NOT NULL; ";
		
		$retval = mysqli_query( $conn, $sql );
		if(! $retval )
		{
			die('数据表创建失败: ' . mysqli_error($conn));
		}
		echo "数据表创建成功\n";
		
    mysqli_close($conn);
?>