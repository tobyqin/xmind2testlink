@echo off
echo start batch xmind to testlink...
cd ~%dp0

if "" -eq "%1" do (
 xmind2testlink %1
 ) else(
 python -c "import glob, os;[os.system('xmind2testlink {}'.format(f)) for f in glob.glob('*.xmind')]"
 )

if %errorlevel% 0 goto done
goto :err

:done
echo OK!
timeout /t 10
exit /b 0

:err
echo something wrong, please check
pause