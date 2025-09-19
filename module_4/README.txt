python -m venv venv
source venv/bin/activate
python -m pip install pytest

pip install beautifulsoup4

python -m pip install Flask

brew install postgresql
brew services start postgresql
pip3 install "psycopg[binary]"


pytest -v