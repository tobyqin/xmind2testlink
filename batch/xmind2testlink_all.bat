@echo off
echo Batch xmind to testlink...
echo.

python -m pip install xmind2testlink -U >NUL
python -c "import glob, os;[os.system('xmind2testlink ""{}""'.format(f)) for f in glob.glob('*.xmind')]"

echo.
echo OK!