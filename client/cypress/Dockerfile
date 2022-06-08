## Start with Cypress base image
FROM cypress/included:9.7.0


# docker-compose-wait: Set env variable to wait 60 seconds for the server to be ready
# Reference: https://github.com/ufoscout/docker-compose-wait#additional-configuration-options
#
ENV WAIT_TIMEOUT=60

## docker-compose-wait: Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait


## Launch the wait tool and then Cypress
## (The server to wait for is set as an environment variable)
CMD /wait && cypress run --config-file cypress_github_ci.json
