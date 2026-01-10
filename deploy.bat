@echo off
REM =============================================================================
REM Task Management App - Automated Deployment Script (Windows Batch)
REM =============================================================================
REM This script calls the PowerShell deployment script
REM Usage: deploy.bat
REM =============================================================================

echo Starting deployment...
powershell -ExecutionPolicy Bypass -File deploy.ps1
