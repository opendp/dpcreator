FROM node:15

# Create app directory
WORKDIR /code/client
COPY . /code/client/


RUN npm install
# If you are building your code for production
# RUN npm ci --only=production


# Convert Locale CSV to JSON and copy it to locale src dir
# make directory if it doesn't already exist
RUN mkdir -p /code/client/src/locales
RUN node /code/client/build_locale/CreateLocaleJson.js

# Bundle app source
#COPY . .

EXPOSE 8080
CMD [ "npm", "run", "serve", "--quiet" ]