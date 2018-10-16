<?php

if(isset($_POST['username'])){
	$user = $_POST['username'];
	$pass = $_POST['password'];

	$datamap = Array('username'=>$user,
			  'password'=>$pass,
			  );
}

else if(isset($_POST['query'])){
	
	$datamap = Array('getquestions'=>$_POST['query'],
			  );	
}

else if(isset($_POST['questionList'])){
	
		$datamap = Array(
				'questionList'=>$_POST['questionList'],
				'pointAmounts'=>$_POST['pointAmounts'],
				'testName'=>$_POST['testName'],
			  );
}
else if(isset($_POST['studentTestQuery'])){
	
		$datamap = Array('studentTestQuery'=>$_POST['studentTestQuery'],
			  );
}
else if(isset($_POST['studentResponseQuery'])){
	
	$datamap = Array(
			'studentResponseQuery'=>$_POST['studentResponseQuery'],
			'testId'=>$_POST['TestId'],
		);	
}
else if(isset($_POST['teacherGetGrade'])){
	
			$datamap = Array('teacherGetGrade'=>$_POST['teacherGetGrade'],
			  );
}
else if(isset($_POST['studentGetGrade'])){
	
			$datamap = Array('studentGetGrade'=>$_POST['studentGetGrade'],
			  );
}
else if(isset($_POST['teacherManageTests'])){
	
			$datamap = Array('teacherManageTests'=>$_POST['teacherManageTests'],
			  );
}
else if(isset($_POST['makeTestTakeable'])){
	
			$datamap = Array('makeTestTakeable'=>$_POST['makeTestTakeable'],
			  );
}
else if(isset($_POST['makeGradesVisible'])){
	
			$datamap = Array('makeGradesVisible'=>$_POST['makeGradesVisible'],
			  );
}
else if(isset($_POST['logout'])){
	
	$datamap = Array('logout'=>$_POST['logout'],
			  );	
}
else if(isset($_POST['addQuestion'])){
	
	$datamap = Array('addQuestion'=>$_POST['addQuestion'],
			  );	
}
else if(isset($_POST['teacherAddComments'])){
	
	$datamap = Array('teacherAddComments'=>$_POST['teacherAddComments'],
					 'teacherNewGrade'=>$_POST['teacherNewGrade'],
					 'testName'=>$_POST['testName'],
			  );	
}
else{
	
	echo "unrecognized query";
}
//curl request


$senddata = json_encode($datamap);



$request = curl_init();

//curl_setopt($request, CURLOPT_URL, "https://web.njit.edu/~tkt7/beta/forwarding.php");
curl_setopt($request, CURLOPT_URL, "https://web.njit.edu/~kjw26/download/Personal/middleLogin.php");
curl_setopt($request, CURLOPT_POST, 1);
curl_setopt($request, CURLOPT_POSTFIELDS, $senddata);
curl_setopt($request, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($request, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($request, CURLOPT_HTTPHEADER,array('Content-Type: application/json'));

$result = curl_exec($request);

echo $result;
curl_close($request);

?>

