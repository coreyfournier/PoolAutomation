###########################################################################################
# Very Very simple deployment script using putty secure copy 
#
#
###########################################################################################
Param(	
	[string]$password,
    #Format is {user account}@{Ip or server name}
    [string]$computer,
    [string]$targetPath = "/home/pi/pool/"
)

#Stop execution on the first error
$ErrorActionPreference = "Stop"

#Copy the files specified from the current directory
Invoke-Expression -Command "pscp -r -pw $($password) *.py  $($computer):$($targetPath)"
Invoke-Expression -Command "pscp -r -pw $($password) *.txt  $($computer):$($targetPath)"
Invoke-Expression -Command "pscp -r -pw $($password) *.html $($computer):$($targetPath)"
Invoke-Expression -Command "pscp -r -pw $($password) lib\*.py  $($computer):$($targetPath)lib"
Invoke-Expression -Command "pscp -r -pw $($password) Pumps\*.py  $($computer):$($targetPath)Pumps"
Invoke-Expression -Command "pscp -r -pw $($password) Services\*.py  $($computer):$($targetPath)Services"