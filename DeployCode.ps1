###########################################################################################
# Very Very simple deployment script using putty secure copy 
#
#DeployCode.psq -password ******* -computer user@computer
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
Invoke-Expression -Command "pscp -r -pw $($password) www\*.*  $($computer):$($targetPath)www"
Invoke-Expression -Command "pscp -r -pw $($password) www\js\*.*  $($computer):$($targetPath)www/js"
Invoke-Expression -Command "pscp -r -pw $($password) www\css\*.*  $($computer):$($targetPath)www/css"
Invoke-Expression -Command "pscp -r -pw $($password) www\fonts\*.*  $($computer):$($targetPath)www/fonts"
Invoke-Expression -Command "pscp -r -pw $($password) lib\*.py  $($computer):$($targetPath)lib"
Invoke-Expression -Command "pscp -r -pw $($password) Devices\*.py  $($computer):$($targetPath)Devices"
Invoke-Expression -Command "pscp -r -pw $($password) Services\*.py  $($computer):$($targetPath)Services"
Invoke-Expression -Command "pscp -r -pw $($password) IO\*.py  $($computer):$($targetPath)IO"
Invoke-Expression -Command "pscp -r -pw $($password) data\*.*  $($computer):$($targetPath)data"