try {
    [Console]::Out.Flush()

    $pythonPath = "C:\Users\rpa.dclick\Documents\projetos\itaminas-conciliacao-fornecedores\venv\Scripts\python.exe"
    $projectPath = "C:\Users\rpa.dclick\Documents\projetos\itaminas-conciliacao-fornecedores\main.py"

    cd $projectPath

    # Caminho para o script Python
    $scriptPath = "$projectPath\main.py"

    $exeProcessName = "python"
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

    $arguments = "-u `"$scriptPath`""

    # Inicia o processo e espera terminar
    $process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -PassThru -NoNewWindow -Wait

}
catch {
    Write-Output "Exce��o ao iniciar processo: $_"
    exit 2
}
finally {
    Write-Output "Processo finalizado (try/catch)."
    [Console]::Out.Flush()
}