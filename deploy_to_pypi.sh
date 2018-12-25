rm -rf dist/ build/ atcoder_tools.egg-info/
python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
