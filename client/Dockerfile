FROM node:12

# Create app directory
WORKDIR /code/client
COPY package*.json /code/client/


RUN npm install
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
#COPY . .

EXPOSE 8080
CMD [ "npm", "run", "serve", "--quiet" ]