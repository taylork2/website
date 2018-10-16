<?php
    session_start();
?>
<?php
    $data = json_decode(file_get_contents('php://input'), true);
    
    $User = $data[username];
    $Pass = $data[password];
    $Spoof = $data[spoof];


    ( $mysqli = new mysqli ("sql1.njit.edu", "tkt7", "cs490", "tkt7") )
                or die ( "Unable to connect to MySQL database\n" );

    if ($mysqli->connect_errno){
        printf("Connection failed: %s\n", $mysqli->connect_error);
        exit();
    }

    $pw_hash = ""; //will store hash retrieved from db in here later 

    $result = $mysqli->query("SELECT * FROM users WHERE user='".$User."'");
    $Database = "false";
    // check if it returns 1 row meaning username is in db 
    if ($result->num_rows==1) {
        $row = $result->fetch_row();
        $pw_hash = $row[1];
        if (password_verify($Pass, $pw_hash)){
            $Database = "true";
        }
    }

    $mysqli->close();

        if ($Database == "true" && $Spoof == "false") {
            session_start();
            $_SESSION['Database'] = "true";
            echo "Failed to log in to NJIT spoof. Successfully logged in to database.<br><br>";
            echo "<a href = 'https://web.njit.edu/~kjw26/download/490/test.php'>Click here to try logging in again.</a>";
        }
        else if ($Database == "false" && $Spoof == "true"){
            session_start();
            $_SESSION['Spoof'] = "true";
            echo "Successfully logged in to NJIT spoof. Failed to login to database.<br><br>";
            echo "<a href = 'https://web.njit.edu/~kjw26/download/490/test.php'>Click here to try logging in again.</a>";
        } 
        else {
            session_start();
            $_SESSION['Fail'] = "true";
            echo "Failed to login to both systems.<br><br>";
            echo "<a href = 'https://web.njit.edu/~kjw26/download/490/test.php'>Click here to try logging in again.</a>";
            //print '<script type="text/javascript"> window.location = "https://www.google.com"</script>';
        }



    //file_put_contents("after_backlogin.txt", $Database);
    //print '<script type="text/javascript"> window.location = "https://www.njit.edu/~kjw26/download/490/test.php"</script>';
?>