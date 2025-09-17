# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['OptiX.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['scipy._lib._util', 'scipy._lib._ccallback', 'scipy._cythonized_array_utils', 'scipy._cyutility'],
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
    name='OptiX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Optix_Icon.ico'],
)
