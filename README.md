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

## Install the required packages
```bash
pip install -r reqs.txt
```
### Note:
* The `pip` command may vary depending on your system. It could be `pip3` or `py -m pip` or `python -m pip`
* In some systems that have limited space of RAM, you may need to disable package cache to avoid running out of memory. You can do this by running `pip install --no-cache-dir -r reqs.txt`

## Run the server
```bash
python main.py
```
* Its should output the server IP address and port where its listening to, to access to the api doc page, go to `http://<ip>:<port>/api/v1`, default is http://127.0.0.1/api/v1