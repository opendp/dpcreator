# Development

This page lists contains rudimentary instructions for building the development environment with [Docker Compose](https://docs.docker.com/compose/).

## Running with Docker Compose

1. **Clone the repository** and `cd` into the directory.
   ```
   git clone https://github.com/opendp/dpcreator.git && \
   cd dpcreator
   ```

2. **Run Docker**
   - This will take a few minutes to run the first time! It includes postgres, redis, npm, etc.:
   ```
   docker-compose up
   ```
   
   **Note**: If major configuration changes have been made (new dependencies, etc.) then the containers will need to be rebuilt:
   ```
   docker-compose up --build
   ```
3. **Initialize the database.** The first time you run (or anytime schema changes have been made):
   - Open a separate Terminal
   - `cd` into the `dpcreator/` directory
   - Manually run this migration:
   ```
   docker-compose run server ./migrate.sh
   ```
   - Note: In general, any command can be run by adding "docker compose run server" to the beginning. For example:
      ```
      # Run a Python shell on a Docker container with access to Django
      docker-compose run server python manage.py shell
      ```
4. **Access DP Creator**
   - Open http://127.0.0.1:80 in your browser
   - The following credentials are available
     - login/pw: `dev_admin`/`admin`
     
## Accessing the API

1. Follow steps 1-4 under _Running with Docker Compose_
2. Open `http://127.0.0.1:8000/api/` in your browser. 
3. The following credentials provide administrative access.
     - login/pw: `dev_admin`/`admin`
4. Note, not all APIs are traditional REST APIs and they are not full documented.
