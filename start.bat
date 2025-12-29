@echo off
echo Iniciando PersonajeIA...

echo Verificando dependencias...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js no encontrado. Instala Node.js desde https://nodejs.org
    pause
    exit /b 1
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instala Python desde https://python.org
    pause
    exit /b 1
)

echo Iniciando servicios...

echo 1. Iniciando backend Node.js...
start "Backend-Node" cmd /k "cd backend-node && node server.js"

timeout /t 2 /nobreak >nul

echo 2. Iniciando backend Python...
start "Backend-Python" cmd /k "cd backend-python && python main.py"

timeout /t 2 /nobreak >nul

echo 3. Iniciando frontend React...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo Servicios iniciados!
echo - Frontend: http://localhost:3000
echo - Backend Node: http://localhost:3001
echo - Backend Python: http://localhost:8000
echo.
echo Presiona cualquier tecla para cerrar todos los servicios...
pause >nul

echo Cerrando servicios...
taskkill /f /im node.exe >nul 2>nul
taskkill /f /im python.exe >nul 2>nul
echo Servicios cerrados.