# SERVER
This is a server component for DeployMe package.

## Requirements
Python 3.x

- Flask
- SQLAlchemy
- pyCryptodome

## How to run
1. Execute `python3 createDb.py` to generate a database file and create a main api key (save that key as that's the only key that can create new users)
2. Deploy the package (run it from server.py)
    - If you have a hosting capable of running python apps follow their instructions
    - If you want to host it yourself in production you might need to get your own WSGI server package (for example tornado), here is more information: [wikipedia](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
    - If you just want to run a development server run (on linux) `FLASK_APP=server.py flask run`
3. Done (for information how to use it check documentation)