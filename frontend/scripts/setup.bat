@echo off
echo 🚀 Setting up RFP Frontend for Windows development...

REM Clean node_modules and package-lock.json to ensure fresh install
echo 🧹 Cleaning existing dependencies...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

REM Install dependencies
echo 📦 Installing dependencies...
npm install

REM Verify installation
echo ✅ Verifying installation...
npm list next >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Next.js installation failed
    pause
    exit /b 1
) else (
    echo ✅ Next.js installed successfully
)

npm list tailwindcss >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Tailwind CSS installation failed
    pause
    exit /b 1
) else (
    echo ✅ Tailwind CSS installed successfully
)

echo.
echo 🎉 Setup complete! You can now run:
echo    npm run dev    # Start development server
echo    npm run build  # Build for production
echo    npm run start  # Start production server
echo.
pause
