<?php
	$fullName = $_POST['fullName'];
	$gender = $_POST['gender'];
	$dateandTime = $_POST['dateandTime'];
	$pickup = $_POST['pickup'];
	$dropoff = $_POST['dropoff'];
    $totalperson = $_POST['totalperson'];
    $message = $_POST['message'];

	// Database connection
	$conn = new mysqli('localhost','root','','IDENTITY');
	if($conn->connect_error){
		echo "$conn->connect_error";
		die("Connection Failed : ". $conn->connect_error);
	} else {
		$stmt = $conn->prepare("insert into passengerprofile(fullName, gender, dateandTime, pickup, dropoff, totalperson,nmessage ) values(?, ?, ?, ?, ?, ?, ?)");
		$stmt->bind_param("sssssis", $fullName, $gender, $dateandTime, $pickup, $dropoff, $totalperson,$message);
		$execval = $stmt->execute();
		echo $execval;
		echo "Registration successfully...";
		$stmt->close();
		$conn->close();
	}
?>