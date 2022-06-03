FROM node:16.15.0

# Create app directory
WORKDIR /code/client
COPY package*.json /code/client/
COPY build_locale/*.* /code/client/build_locale/
# COPY src/locales/* /code/client/src/locales/

RUN npm install
# If you are building your code for production
# RUN npm ci --only=production


# Convert Locale CSV to JSON and copy it to locale src dir
# make directory if it doesn't already exist
# RUN mkdir -p /code/client/src/locales
# RUN node /code/client/build_locale/CreateLocaleJson.js
# COPY src/locales/* /code/client/src/locales/

# Bundle app source
# COPY . .

EXPOSE 8080
CMD [ "./run_client.sh" ]
