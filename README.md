# Django + Vue CLI + Webpack branch

This is based on an [existing project](https://github.com/EugeneDae/django-vue-cli-webpack-demo) by EugeneDae. See his project for original documentation.

## Running

1. Clone the repo and `cd` into the directory. `cd $HOME && git clone https://github.com/opendifferentialprivacy/opendp-ux.git && cd $HOME/opendp-ux`
2. Install Django: `pip install django`
3. Install Vue.js project dependencies: `cd $HOME/opendp-ux/client && npm install`
4. Run the Vue.js dev server: `cd $HOME/opendp-ux/client && npm run serve`
   - build for production: `npm run build`
5. `cd` to the `server/` directory and run Django dev server from it: `cd $HOME/opendp-ux/server && python manage.py runserver`
6. Open `http://127.0.0.1:8000/` in your browser. Note that the port you specify should match the port in the output of step 5, above.

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
