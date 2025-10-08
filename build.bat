@echo off
echo ==============================================
echo   BUILD DO PROJETO ITAMINAS-CONCILIACAO-FORN
echo ==============================================

:: Remove pastas antigas de build
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo.
echo [1/5] Instalando navegadores Playwright...
echo.
playwright install chromium

echo.
echo [2/5] Gerando executável com PyInstaller...
echo.

pyinstaller -F -n itaminas-conciliacao ^
    --add-data="config;config" ^
    --add-data="scraper;scraper" ^
    --add-data="templates;templates" ^
    --add-data="data;data" ^
    --hidden-import=pandas ^
    --hidden-import=playwright ^
    --hidden-import=openpyxl ^
    --hidden-import=jinja2 ^
    --hidden-import=dotenv ^
    --hidden-import=workalendar ^
    --hidden-import=workalendar.america ^
    --hidden-import=workalendar.america.brazil ^
    --hidden-import=pathlib ^
    --hidden-import=logging ^
    --hidden-import=asyncio ^
    --hidden-import=email.mime.text ^
    --hidden-import=email.mime.multipart ^
    --hidden-import=smtplib ^
    --hidden-import=ssl ^
    --hidden-import=json ^
    --hidden-import=os ^
    --hidden-import=sys ^
    --hidden-import=datetime ^
    --hidden-import=time ^
    --hidden-import=sqlite3 ^
    --hidden-import=playwright._impl._api_structures ^
    --hidden-import=playwright._impl._connection ^
    --hidden-import=playwright._impl._driver ^
    --hidden-import=playwright._impl._browser_type ^
    --collect-all=playwright ^
    --disable-windowed-traceback ^
    main.py

echo.
echo [3/5] Copiando arquivos extras...
echo.

copy .env dist /y 2>nul
copy parameters.json dist /y 2>nul
copy requirements.txt dist /y 2>nul

echo.
echo [3.1/5] Copiando CONTEÚDO das pastas...
echo.

:: Copia TODO o conteúdo das pastas
xcopy config dist\config /E /I /Y 2>nul
xcopy scraper dist\scraper /E /I /Y 2>nul
xcopy templates dist\templates /E /I /Y 2>nul
xcopy data dist\data /E /I /Y 2>nul

echo.
echo [4/5] Verificando estrutura de arquivos...
echo.
echo Conteúdo de dist\scraper:
dir dist\scraper /B
echo.
echo Conteúdo de dist\config:
dir dist\config /B

echo.
echo [5/5] BUILD CONCLUÍDO!
echo ==============================================
echo Executável: dist\itaminas-conciliacao.exe
echo.
echo INSTRUÇÕES IMPORTANTES:
echo 1. SEMPRE execute pelo Prompt de Comando
echo 2. Navegue até a pasta: cd dist
echo 3. Execute: itaminas-conciliacao.exe
echo.
echo NÃO clique duas vezes no executável!
echo ==============================================
echo.

pause