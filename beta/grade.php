<?php

	$student_foldername = "student_answers"; //location where all student responses stored

	$data = json_decode(file_get_contents('php://input'), true);

	// $data = Array("test_id"=>18,
	// 	"questions"=>[
	// 		Array("response"=>"def hello():\n\treturn 'hello world'",
	// 		// "student"=>1,
	// 		"question_id"=>1,
	// 		"test_cases"=>"hello()///'hello world'///50",
	// 		"requirements"=>"def hello():///20///return///20"),
	// 		Array("response"=>"def hello()\n\treturn 'hello world'",
	// 		// "student"=>1,
	// 		"question_id"=>2,
	// 		"test_cases"=>"hello()///'hello world'///50",
	// 		"requirements"=>"def hello():///20///print///20")]);

	$feedback_str = ""; // will store the feedback seperated by /// 
	$test_score = 0; // will store the final test score 
	// will separate by # 

	$test_num = $data["test_id"];
	$questions = $data["questions"];

	for ($q=0; $q<count($questions);$q++){
		//storing the data 
		$question = $questions[$q];
		$code = $question["response"]; 
		// $student = $data["student"];
		$question_num = $question["question_id"];
		$test_cases = explode("///", $question["test_cases"]);
		$reqs = $question["requirements"];

		// Creating filenames 
		$fn_code = $student_foldername."/code_t".$test_num."_q".$question_num.".py";
		$fn_test_cases = $student_foldername."/test_t".$test_num."_q".$question_num.".py";
		$fn_code_extless = "code_t".$test_num."_q".$question_num;

		// Creating files 
		$code_file = fopen($fn_code, "w");

		// Write the code to the file & close  
		fwrite($code_file, $code);
		fclose($code_file); 

		// allows code to be sent in as single argument 
		$escaped_code = escapeshellarg($code); 
		$escaped_reqs = escapeshellarg($reqs);

		// test.py will return the score after finding reqs, feedback, and True or False if compiles
		exec("python student_answers/test.py ".$escaped_code." ".$escaped_reqs, $output);
		$score = $output[0];
		$feedback = $output[1];
		$compiles_bool = $output[2]; 

		$feedback_str = $feedback_str.$feedback; //append feedback to send

		// check if compiles 
		if (strcmp($compiles_bool, 'True') == 0) {

			// write test cases to another file and test if matches expected result 
			$test_file = fopen($fn_test_cases, "w");
			fwrite($test_file, "import ".$fn_code_extless);

			// every third element is a test case formatted as functionName(parameter, ...)
			for ($i = 0; $i < count($test_cases); $i+=3){
				fwrite($test_file, "\nprint ".$fn_code_extless.".".$test_cases[$i]);
			}

			exec("python ".$fn_test_cases, $result);

			// compare expected result to result 
			for ($j = 0; $j < count($result); $j++){
				$expected_result = $test_cases[3*$j+1];
				$points = $test_cases[3*$j+2];
				// if results do not match, subtract points & give feedback
				if (!strcmp($expected_result, $result[$j])){
					$score = $score - $points;
					$feedback_str = $feedback_str."\nFailed test case :".($j+1)." -".$points.". ";
				} else {
					$feedback_str = $feedback_str."\nPassed test case :".($j+1);
				}
				
			}

			// close and unlink test cases file 
			fclose($test_file);
			unlink($fn_test_cases);
			unlink($fn_code."c"); //since file compiled, delete compile file 

		// For now, subtract 50 points if code does not compile 
		} else if (strcmp($compiles_bool, "False")==0){
			$score = $score - 50;
		}

		// test_score to send 
		$test_score = $test_score + $score;
		$feedback_str = $feedback_str."///";

		unlink($fn_code); //delete the files once we're done with it 
		unset($output); // unset the output variable so it doesn't keep concatenating output
	}

	$score_final = $test_score / count($questions);

	echo substr($score_final."#".$feedback_str, 0, -3);

	// TODO return feedback, question scores, total score 

?>