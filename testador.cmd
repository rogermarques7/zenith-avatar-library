@echo off
REM Sobe o testador de avatares. Clique duas vezes neste arquivo.
REM
REM POR QUE ISTO EXISTE
REM O avatar_tester.html so funciona servido por HTTP: ele faz fetch do
REM library.json e o model-viewer carrega o GLB e o HDR por URL relativa. Aberto
REM por file:// o navegador barra tudo isso e a pagina sobe em branco.
REM
REM Ate 15/08 o servidor subia junto com a sessao de trabalho e morria com ela -
REM foi assim que o ambiente "parou de abrir" sem nada ter quebrado. Este .cmd e
REM independente da sessao: fecha a janela preta, cai o servidor; deixa aberta,
REM fica de pe.
REM O `cd /d "%~dp0"` nao e enfeite: sem ele o http.server serve a pasta de onde
REM o cmd foi aberto, e o testador sobe 404 em tudo.
cd /d "%~dp0"
echo.
echo   Testador Zenith
echo   http://localhost:8765/test/avatar_tester.html
echo.
echo   (deixe esta janela aberta; Ctrl+C para parar)
echo.
start "" "http://localhost:8765/test/avatar_tester.html"
python -m http.server 8765 --bind 127.0.0.1
