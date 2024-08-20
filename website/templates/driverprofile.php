<?php
	$fullName = $_POST['fullName'];
	$gender = $_POST['gender'];
	$dateandTime = $_POST['dateandTime'];
	$pickup = $_POST['pickup'];
	$dropoff = $_POST['dropoff'];
	$carplate = $_POST['carplate'];
    $carmodel = $_POST['carmodel'];
    $totalperson = $_POST['totalperson'];
    $fees = $_POST['fees'];
    $duitnowid = $_POST['duitnowid'];
    $message = $_POST['message'];

	$conn = new mysqli('localhost','root','','IDENTITY');
	if($conn->connect_error){
		echo "$conn->connect_error";
		die("Connection Failed : ". $conn->connect_error);} 
		else {mysqli_close($conn);
				$stmt = $conn->prepare("insert into driverprofile(fullName, gender, dateandTime, pickup, dropoff, carplate, carmodel, totalperson, fees, qrcode, message ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
				$stmt->bind_param("sssssssisis", $fullName, $gender, $dateandTime, $pickup, $dropoff, $carplate, $carmodel, $totalperson, $fees, $qrcode ,$message);
				$execval = $stmt->execute();
				echo $execval;
				echo "Registration successfully...";
				$stmt->close();
				$conn->close();
			}
?>