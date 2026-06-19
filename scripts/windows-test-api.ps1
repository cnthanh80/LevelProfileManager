Write-Host "Testing Level Profile Manager v0.3 API..."

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method GET
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/db" -Method GET

$loginBody = @{
    username = "admin"
    password = "Admin@123"
} 

$tokenResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded"
$token = $tokenResponse.access_token
$headers = @{ Authorization = "Bearer $token" }

Write-Host "Login OK. Token received."
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" -Method GET -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/roles" -Method GET -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users" -Method GET -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/organizations" -Method GET
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/information-systems" -Method GET
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/level-profiles" -Method GET

Write-Host "v0.3 API test completed."
