source .venv/bin/activate
python src/amweb.py "$@" && python src/kioskmodus.py "$@"
