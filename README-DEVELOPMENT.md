# Development

This page lists contains rudimentary instructions for building the development environment with [Docker Compose](https://docs.docker.com/compose/).

## Building with Docker Compose
1. Clone the repo and `cd` into the directory.

    `git clone https://github.com/opendp/dpcreator.git && cd dpcreator`

2. Tell Docker to turn on the webserver and database: 

    `docker-compose up`
   
   If major configuration changes have been made (new dependencies, etc.) then the containers will need to be rebuilt:
   
   `docker-compose up --build`

1. All subsequent commands should be run from the `server` directory
   
   `cd server`

3. The first time you run (or anytime schema changes have been made), open a separate Terminal, `cd` into the `dpcreator/` directory
and manually run this migration:

    `docker-compose run server ./migrate.sh`

    (In general, any command can be run by adding "docker-compose run server" to the beginning, 
such as:

    `docker-compose run server python manage.py shell`
    
which will drop you into the Django shell on the Docker container.)

## Running without Containers (not recommended)

1. Clone the repo and `cd` into the directory. `git clone https://github.com/opendifferentialprivacy/dpcreator.git && cd dpcreator`
1. Create virtual environment: `python3 -m venv venv`
1. Activate virtual environment: `. venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Ensure latest version of npm: `npm install -g npm@latest`
4. Install Vue.js project dependencies: `cd dpcreator/client && npm install`
5. Run the Vue.js dev server: `cd dpcreator/client && npm run serve`
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

## Generating code diagrams
(not used)
1. Create a Python virtualenv to set up your environment `python3 -m venv venv`
2. Install PyDotPlus
`pip install pydotplus`
3. Install Django Extensions
`pip install django-extensions`
4. Configure your Django project to use Django Extensions in settings.py under `server/opendp-projects/`
```
INSTALLED_APPS = (
	...
	'django_extensions',
	...
)
```
5. Invoke Django manager with graph models option, from the server/ subdirectory
`python manage.py graph_models -a -o opendpapp_models.png`
6. Use a browser or viewer to view the created png file, found in the `server/` subdirectory

(This is based on an [existing project](https://github.com/EugeneDae/django-vue-cli-webpack-demo) by EugeneDae. See his project for original documentation.)

## Generating code diagrams

1. Create a Python virtualenv to set up your environment `python3 -m venv venv`
2. Install PyDotPlus
`pip install pydotplus`
3. Install Django Extensions
`pip install django-extensions`
4. Configure your Django project to use Django Extensions in settings.py under `server/opendp-projects/`
```
INSTALLED_APPS = (
	...
	'django_extensions',
	...
)
```
5. Invoke Django manager with graph models option, from the server/ subdirectory
`python manage.py graph_models -a -o opendpapp_models.png`
6. Use a browser or viewer to view the created png file, found in the `server/` subdirectory

(This is based on an [existing project](https://github.com/EugeneDae/django-vue-cli-webpack-demo) by EugeneDae. See his project for original documentation.)
