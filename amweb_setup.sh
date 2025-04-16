source .venv/bin/activate
python amweb.py "$@" && python kioskmodus.py "$@"
