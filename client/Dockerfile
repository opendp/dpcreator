FROM node:12

# Create app directory
WORKDIR /code
COPY . /code/
WORKDIR /code/client

RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
COPY . .

EXPOSE 8080
CMD [ "npm", "run", "serve", "--quiet" ]