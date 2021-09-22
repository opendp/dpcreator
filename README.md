# DP Creator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![integration tests](https://github.com/opendp/dpcreator/actions/workflows/cypress.yml/badge.svg)
![python server side tests](https://github.com/opendp/dpcreator/actions/workflows/python-app.yml/badge.svg)

DP Creator is a web application which guides users in the creation of [differentially private statistics](https://opendp.org/about#whatisdifferentialprivacy). Using the [OpenDP library](https://github.com/opendp/opendp) at its core, DP Creator has been designed to work with data repositories, with initial integration beginning with [Dataverse](https://dataverse.org/), an open source research data repository. 

DP Creator is part of the larger [OpenDP Project](https://opendp.org), a community effort to build trustworthy, open source software tools for analysis of private data. 


## Status

DP Creator is under development and we expect to have a test version, connected to a example Dataverse installation publicly available this fall. Please see the [OpenDP project Roadmap](https://opendp.org/roadmap) for more details.

The application is designed to be deployed using [kubernetes](https://kubernetes.io/) and the development environment is available through [Docker Compose](https://docs.docker.com/compose/).

Several screenshots of DP Creator appear below (click for a larger image):

[<img src="doc_images/dpcreator_home.png" alt="DP Creator home" height="140">](doc_images/dpcreator_home.png)&nbsp;
[<img src="doc_images/dpcreator_02_questions.png" alt="DP Creator home" height="130">](doc_images/dpcreator_02_questions.png)&nbsp;
[<img src="doc_images/dpcreator_03_set.png" alt="DP Creator home" height="130">](doc_images/dpcreator_03_set.png)&nbsp;
[<img src="doc_images/dpcreator_04.create.png" alt="DP Creator home" height="130">](doc_images/dpcreator_04.create.png)


## Contact / Getting Help

If you would like to learn more or want to submit feedback, please reach out! Here are some ways to contact us:

* Ask questions on our [discussions forum](https://github.com/opendp/opendp/discussions)
  * This forum is used for all of the OpenDP projects, including the [OpenDP library](https://github.com/opendp/opendp and DP Creator. 
* Open issues on our [issue tracker](https://github.com/opendp/dpcreator/issues)
* Send general queries to [info@opendp.org](mailto:info@opendp.org?subject=DP%20Creator)
* Reach us on Twitter at [@opendp_org](https://twitter.com/opendp_org)

## Contributing

DP Creator is a community effort, and we welcome your contributions to its development! Our current technology stack/development environment includes [Vue.js](https://vuejs.org/), [Python](https://www.python.org/), and [Docker](https://www.docker.com/). If you'd like to participate, please reach out using the contact information above.
