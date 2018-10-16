<?php

	$input = file_get_contents("php://input");
	$ch = curl_init();

	$arr = json_decode($input, true);

	if(isset($arr['getquestions'])){
		curl_setopt($ch, CURLOPT_URL, "https://web.njit.edu/~rs637/download/beta/questions.php");
	}
	else if(isset($arr['submitTest']) || isset($arr['studentTestQuery']) || isset($arr['studentResponseQuery']) || isset($arr['studentGetGrade']) || isset($arr['teacherGetGrade']) || isset($arr['teacherManageTests']) || isset($arr['makeGradesVisible']) || isset($arr['makeTestTakeable'])){
		curl_setopt($ch, CURLOPT_URL, "https://web.njit.edu/~rs637/download/beta/test.php");
	}
	else if(isset($arr['logout'])){
		curl_setopt($ch, CURLOPT_URL, "https://web.njit.edu/~rs637/download/beta/logout.php");
	}
	else{
		curl_setopt($ch, CURLOPT_URL, "https://web.njit.edu/~rs637/download/beta/databaseLogin.php");
		
	}

	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($ch, CURLOPT_HTTPHEADER,array('Content-Type: application/json'));

	$c = curl_exec($ch);

	echo $c;

	curl_close($ch);


?>

