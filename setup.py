from setuptools import setup

APP = ['your_script.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['required_package1', 'required_package2'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
