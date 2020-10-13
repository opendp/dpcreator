# The OpenDP Web Application

## Building
1. Install virtualenv for Python
``` shell
    pip3 install virtualenv
```
2. Clone the repo and change directory into the directory
``` shell
    cd $HOME && git clone https://github.com/opendifferentialprivacy/opendp-ux.git && cd $HOME/opendp-ux
```
3. Create a virtual environment
``` shell
    cd $HOME/opendp-ux && virtualenv -p `which python3` venv
```
4. Install Django project dependencies
``` shell
    pip install -r requirements.txt
```
5. Install Vue.js project dependencies
``` shell
    cd $HOME/opendp-ux/client && npm install
```
6. Build the Vue.js project
``` shell
    npm run build
```

1. Clone the repo and `cd` into the directory. `git clone https://github.com/opendifferentialprivacy/opendp-ux.git && cd opendp-ux`
1. Create virtual environment: `python3 -m venv venv`
1. Activate virtual environment: `. venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Ensure latest version of npm: `npm install -g npm@latest`
4. Install Vue.js project dependencies: `cd opendp-ux/client && npm install`
5. Run the Vue.js dev server: `cd opendp-ux/client && npm run serve`
   - build for production: `npm run build`
6. `cd server/` 
7. First time, run migrations: `python manage.py migrate` 
8. Run Django dev server: `python manage.py runserver`
9. Open `http://127.0.0.1:8000/` in your browser.

## Accessing the API
1. Follow steps under [Building](building) and [Running](running)
2. Open `http://127.0.0.1:8000/api/` in your browser.
``` shell
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --kiosk http://127.0.0.1:8000/api/
```

## Accessing the API via command-line
1. Access your command-line terminal
2. Issue a HTTP command for the API area of interest. This example uses curl to issue the HTTP command. Note that the port you specify should match the port in the output of step 2 under [Running](running), above
``` shell
curl http://127.0.0.1:8000/api/
curl http://127.0.0.1:8000/api/users/
```

(This is based on an [existing project](https://github.com/EugeneDae/django-vue-cli-webpack-demo) by EugeneDae. See his project for original documentation.)
