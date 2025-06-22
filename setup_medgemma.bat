@echo off
echo 🔬 MedFlow + Real MedGemma Setup
echo ================================
echo.
echo This will set up REAL MedGemma AI analysis via Hugging Face
echo.
echo Step 1: Get your Hugging Face token
echo   - Go to: https://huggingface.co/settings/tokens
echo   - Create account (free)
echo   - Generate new token with "Read" access
echo   - Copy the token (starts with hf_...)
echo.
set /p HF_TOKEN="Enter your Hugging Face token (hf_...): "

if "%HF_TOKEN%"=="" (
    echo ❌ No token provided. Using demo mode.
    pause
    exit /b
)

echo.
echo 🔧 Setting environment variable...
setx HUGGINGFACE_TOKEN "%HF_TOKEN%"

echo.
echo ✅ MedGemma setup complete!
echo.
echo Next steps:
echo 1. Restart your terminal/conda environment
echo 2. Run: conda activate medflow ^&^& python demo_api.py
echo 3. Look for "🤖 Real MedGemma service initialized!"
echo 4. Upload an image to test REAL AI analysis!
echo.
echo Your system will now use Google's real MedGemma AI model! 🚀
echo.
pause 