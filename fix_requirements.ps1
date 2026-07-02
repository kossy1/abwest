# fix_requirements.ps1
Write-Host "Fixing requirements.txt..." -ForegroundColor Yellow

# Create clean requirements
@"
Django==4.2.11
whitenoise==6.6.0
python-dotenv==1.0.1
pymongo==4.6.1
"@ | Out-File -FilePath requirements.txt -Encoding ascii

Write-Host "✅ requirements.txt recreated without BOM" -ForegroundColor Green

# Verify
Get-Content requirements.txt
