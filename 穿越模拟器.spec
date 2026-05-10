# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates/index.html', 'templates'),
        ('static', 'static'),
        ('app', 'app'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'flask_socketio',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext.declarative',
        'engineio.async_drivers.threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='超级穿越模拟器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
