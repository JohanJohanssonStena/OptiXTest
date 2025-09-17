# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['OptiX.py'],
    pathex=[],
    binaries=[],
    datas=[('Optix_Icon.ico', '.')],
    hiddenimports=['scipy.optimize._linprog', 'scipy.linalg._decomp_ldl', 'scipy.stats._stats', 'scipy._cythonized_array_utils', 'scipy._cyutility', 'matplotlib.backends.backend_tkagg', 'matplotlib.pyplot'],
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
