@echo off
title Launch Free Public Domain Tunnel (Cloudflare)
echo =====================================================================
echo   OPTIMIZING DIGITAL FORENSIC SECURITY VIA SECURE STORAGE
echo   Launching Free Public HTTPS Domain (Cost: Rs 0)
echo =====================================================================
echo.
echo [*] Starting Cloudflare Tunnel on port 8000...
echo.
.\cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
