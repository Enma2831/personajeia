# Test script for PersonajeIA services

Write-Host "Testing PersonajeIA Services..." -ForegroundColor Green

# Test Node.js backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/" -Method GET -TimeoutSec 5
    Write-Host "✅ Node.js Backend: $($response.Content)" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js Backend: Not responding" -ForegroundColor Red
}

# Test Python backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 5
    Write-Host "✅ Python Backend: FastAPI docs available" -ForegroundColor Green
} catch {
    Write-Host "❌ Python Backend: Not responding" -ForegroundColor Red
}

# Test Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 10
    if ($response.Content -match "PersonajeIA") {
        Write-Host "✅ Frontend: React app loaded" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Frontend: Loaded but content check failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend: Not responding" -ForegroundColor Red
}

Write-Host "`nTest completed. Check individual services if any failed." -ForegroundColor Cyan