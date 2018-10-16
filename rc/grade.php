<?php

	$student_foldername = "student_answers"; //location where all student responses stored

	$data = json_decode(file_get_contents('php://input'), true);

	// $data = Array("testName"=>"New Test",
	// 	"questions"=>[
	// 		Array("question_id"=>"23",
	// 		"response"=>"sdgsgsd",
	// 		"test_cases"=>"print(operation('+',2,4))\/\/\/6\/\/\/10#print(operation('-',5,1))\/\/\/4\/\/\/10#print(operation('*',3,6))\/\/\/18\/\/\/20#print(operation('\/',4,2))\/\/\/2\/\/\/20#print(operation('@',2,4))\/\/\/-1\/\/\/10",
	// 		"requirements"=>"def\/\/\/if\/\/\/return",
	// 		"points"=>"80",
	// 		"functionName"=>"operation",
	// 		"parameters"=>"op\/\/\/a\/\/\/b"),
	// 		Array("question_id"=>"25","response"=>"sdgsg",
	// 		"test_cases"=>"Hi(2)\/\/\/'HIHIHIHI'\/\/\/20#Hi(3)\/\/\/\'HOHOHOHO\'\/\/\/20",
	// 		"requirements"=>"def\/\/\/if\/\/\/print",
	// 		"points"=>"60",
	// 		"functionName"=>"Hi",
	// 		"parameters"=>"num")
	// 		]);

	$feedback_str = ""; // will store the feedback seperated by /// 
	$test_score = 0; // will store the final test score 
	$total_testscore = 0;
	// will separate by # 

	// $test_num  = $data["testName"];
	$questions = $data["questions"];

	for ($q=0; $q<count($questions);$q++){
		//storing the data 
		$question = $questions[$q];
		$code = $question["response"]; 
		$func_name = $question["functionName"];
		$params = $question["parameters"];
		// $student = $data["student"];
		$question_num = $question["question_id"];
		$test_cases = $question["test_cases"];
		$reqs = $question["requirements"];
		$points = $question["points"];

		// allows code to be sent in as single argument 
		$escaped_code = escapeshellarg($code); 
		$escaped_reqs = escapeshellarg($reqs);
		$escaped_func = escapeshellarg($func_name);
		$escaped_testcases = escapeshellarg($test_cases);
		$escaped_params = escapeshellarg($params);
		$escaped_points = escapeshellarg($points);

		// parseTest.py will calculate the score and provide feedabck 
		exec("python parseTest.py ".$escaped_code." ".$escaped_reqs." ".$escaped_func." ".$escaped_params." ".$escaped_testcases." ".$points, $output);
		$score = $output[0];
		$feedback = $output[1];

		$feedback_str = $feedback_str.$feedback; //append feedback to send

		// test_score to send 
		$test_score = $test_score + $score;
		$total_testscore = $total_testscore + $points;
		$feedback_str = $feedback_str."///";

		unset($output); // unset the output variable so it doesn't keep concatenating output
	}

	if ($total_testscore != 0) {
		$score_final = round($test_score / $total_testscore * 100, 2);
	} else{
		$score_final = 0;
	}

	// remove last /// so use substring 
	echo substr($score_final."#".$feedback_str, 0, -3); 

?>