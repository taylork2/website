<?php
	include ("config.php");
	( $mysqli = new mysqli ( $hostname, $username, $password, $project ) )
		        or die ( "Unable to connect to MySQL database\n" );

    if ($mysqli->connect_errno){
    	printf("Connection failed: %s\n", $mysqli->connect_error);
    	exit();
    } else {
		print("Connected to MySQL\n");
    }

	$data = json_decode(file_get_contents('php://input'), true);

	$username = $data["username"];
	$password = $data["password"];

	$pw_hash = ""; //will store hash retrieved from db in here later 


	$result = $mysqli->query("SELECT * FROM users WHERE user='".$username."'");

	// check if it returns 1 row meaning username is in db 
	if ($result->num_rows==1) {
		$row = $result->fetch_row();
		$pw_hash = $row[1];
		if (password_verify($password, $pw_hash)){
			$return = array(
				"username" => $username, 
				"password"=> $password, 
				"spoof" => "NA", 
				"database" => "true");
			echo "SUCCESS\n";
		}
	} else {
		$return = array(
			"username" => $username, 
			"password"=>$password, 
			"spoof" => "NA", 
			"database" => "false");
		echo "FAIL\n";
	}

	$mysqli->close();

	$ch = curl_init('https://web.njit.edu/~rs637/download/cs490/Spoof2.php');
	curl_setopt_array($ch, array( 
	    CURLOPT_POST => TRUE,
	    CURLOPT_RETURNTRANSFER => TRUE,
	    CURLOPT_HTTPHEADER => array(
	        'Content-Type: application/json'
	    ),
	    CURLOPT_POSTFIELDS => json_encode($return)
	));     

	$chresult = curl_exec($ch);

	$file = 'newfile.txt';
	file_put_contents($file, $return);

	if ($chresult === FALSE){
		die(curl_error($ch));
	} else {
		echo "message sent :)";
	}

?>