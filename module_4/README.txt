python -m venv venv
source venv/bin/activate
python -m pip install pytest

python -m pip install Flask

brew install postgresql
brew services start postgresql
pip3 install "psycopg[binary]"


pytest -v