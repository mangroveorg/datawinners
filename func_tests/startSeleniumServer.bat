@ECHO ON
rem set WEBDRIVER=selenium-server-standalone-2.0b1.jar 
set WEBDRIVER=selenium-server-standalone-2.0a4.jar
echo Start Webdriver %WEBDRIVER%

echo Starting Webdriver for FireFox using the following command:
echo start java -jar lib//%WEBDRIVER%
start "Webdriver %WEBDRIVER%" java -jar lib//%WEBDRIVER%
