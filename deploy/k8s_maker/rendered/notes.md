

Exists:

Container Registry: Github's registry
 - Postgres Image
 - dpcreator-app Image
 - dpcreator-nginx images
    - Web server
    - /static/  - directly serves css/js including vue app
    - / -> app
    
    
- shared directory
  - dpcreator-app static files
    -> /dpreator_volume/static
  - dpcreator-nginx
   -> /dpreator_volume/static

 