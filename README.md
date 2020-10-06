# Django + Vue CLI + Webpack branch

This is based on an [existing project](https://github.com/EugeneDae/django-vue-cli-webpack-demo) by EugeneDae. See his project for original documentation.

## Running

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

1. Follow steps 1-5 under Running, above
2. Open `http://127.0.0.1:8000/api/` in your browser.

## Accessing the API via command-line
1. Access your command-line terminal
2. Issue a HTTP command for the API area of interest. This example uses curl to issue the HTTP command. Note that the port you specify should match the port in the output of step 5 under Running, above
```
curl http://127.0.0.1:8000/api/
curl http://127.0.0.1:8000/api/users/
```
