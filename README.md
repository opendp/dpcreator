# Django + Vue CLI + Webpack branch

This is based on an [existing project](https://github.com/EugeneDae/django-vue-cli-webpack-demo) by EugeneDae. See his project for original documentation.

## Building
1. Install virtualenv for Python: `pip3 install virtualenv`
2. Clone the repo and `cd` into the directory. `cd $HOME && git clone https://github.com/opendifferentialprivacy/opendp-ux.git && cd $HOME/opendp-ux`
3. Create a virtual environment: `cd $HOME/opendp-ux && virtualenv -p \`which python3\` venv`
4. Install Django project dependencies: `pip install -r requirements.txt`
5. Install Vue.js project dependencies: `cd $HOME/opendp-ux/client && npm install`

## Running
1. Run the Vue.js dev server: `cd $HOME/opendp-ux/client && npm run serve`
   - build for production: `npm run build`
2. Run the Django dev server: `cd $HOME/opendp-ux/server && python manage.py runserver`
3. Open `http://127.0.0.1:8000/` in your browser. Note that the port you specify should match the port in the output of step 2, directly above.

## Accessing the API
1. Follow steps under [Building](building) and [Running](running)
2. Open `http://127.0.0.1:8000/api/` in your browser.

## Accessing the API via command-line
1. Access your command-line terminal
2. Issue a HTTP command for the API area of interest. This example uses curl to issue the HTTP command. Note that the port you specify should match the port in the output of step 2 under [Running](running), above
```
curl http://127.0.0.1:8000/api/
curl http://127.0.0.1:8000/api/users/
```
