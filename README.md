# PBL6_backend
Managing the backend services for the PBL6 project

# Setup 
## Clone the repository
```bash
git clone https:\\github.com\NgLam2911\PBL6_backend.git
```

## Create a virtual environment (Optional)
```bash
python -m venv venv
```
### Note:
* The python command may vary depending on your system. It could be `python3` or `py` or `python`
* In case you are using `py`, you may need to specify the version of python you want to use. For example: `py -3.8 -m venv venv`
* In Linux, you may need to install the `python3-venv` package. You can do this by running `sudo apt-get install python3-venv`

## Activate the virtual environment
### Windows
```bash
venv\Scripts\activate
```
### Linux
```bash
source venv/bin/activate
```

## Install the required packages
```bash
pip install -r reqs.txt
```
### Note:
* The `pip` command may vary depending on your system. It could be `pip3` or `py -m pip` or `python -m pip`
* In some systems that have limited space of RAM, you may need to disable package cache to avoid running out of memory. You can do this by running `pip install --no-cache-dir -r reqs.txt`

## Create a `.env` file for configuration
* Create a file named `<something>.env` in the root directory of the project. The `<something>` can be anything you want, but it should have the `.env` extension at the end. For example: `config.env` or `production.env`, only one `.env` file is needed. Its content should be like this:
```env
host=localhost # The IP address where the server is running
port=80 # The port where the server is listening to
db_HOST =mongodb://localhost:27017/ # The connection string to the MongoDB database
db_auth_user =admin # The username to authenticate to the database
db_auth_pswd =12345678 # The password to authenticate to the database
db_auth_source=admin # The source of the authentication
db_name=test # The name of the database
video_save_path=videos # The path to save the uploaded videos
```

## Run the server
```bash
python main.py
```
* Its should output the server IP address and port where its listening to, to access to the api doc page, go to `http://<ip>:<port>/api/v1`, default is http://127.0.0.1/api/v1