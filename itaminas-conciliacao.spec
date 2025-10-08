# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('config', 'config'), ('scraper', 'scraper'), ('templates', 'templates'), ('data', 'data')]
binaries = []
hiddenimports = ['pandas', 'playwright', 'openpyxl', 'jinja2', 'dotenv', 'workalendar', 'workalendar.america', 'workalendar.america.brazil', 'pathlib', 'logging', 'asyncio', 'email.mime.text', 'email.mime.multipart', 'smtplib', 'ssl', 'json', 'os', 'sys', 'datetime', 'time', 'sqlite3', 'playwright._impl._api_structures', 'playwright._impl._connection', 'playwright._impl._driver', 'playwright._impl._browser_type']
tmp_ret = collect_all('playwright')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='itaminas-conciliacao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
