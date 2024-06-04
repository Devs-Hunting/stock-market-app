# Programmers-stock-market

* [Description](#description)
* [Tech-stack](#tech-stack)
* [Live demo](#live-demo)
* [Setup](#setup)
* [Tests](#tests)
* [Contributors](#contributors)
* [Screenshot](#screenshot)


## Description
<b>General info</b><br>
This web application simplifies access to programming services for those seeking help, and connects freelance programmers with potential clients. It serves as a platform where clients can post coding tasks and programmers can offer their services. The user interface is available in English and Polish. The application is designed to facilitate smooth interactions and transactions between clients and programmers.

<details><summary><b>Application purpose</b></summary>
The primary goal of this application is to create a marketplace where users can publish programming tasks and receive multiple offers from freelance programmers. Once the task is completed, clients can review the submitted solutions, accept them, and proceed with payment. This system aims to streamline the process of finding and hiring programming talent while ensuring quality and satisfaction for both parties involved.</details>

<details><summary><b>Application flow</b></summary>

1. Register and login
2. Select your role: client (CL) or contractor (CO)
3. (CL) Publish a task, set a budget, and define the task completion time
4. (CO) Find a task that matches your tech stack and respond with a price offer
5. (CL) Choose and accept an offer from a programmer
6. (CO) Prepare and submit your solution
7. (CL) Review the solution and accept or decline it
8. (CL/CO) If declined, discuss the issues or use an arbiter
9. (CL) If the solution is accepted, pay the programmer

</details>

## Tech-stack
<ul>
<li>Python</li>
<li>Django</li>
<li>HTML/CSS</li>
<li>Bootstrap 5</li>
<li>PostgreSQL</li>
<li>Celery</li>
<li>Redis</li>
<li>Docker Compose</li>
<li>Selenium</li>
<li>Sendgrid</li>
</ul>

## Live-demo
We have prepared a live demo of the app on Mikr.us server. Please sign up and feel free to test it.<br>
[stockmarket.toadres.pl](https://stockmarket.toadres.pl)

## Setup
<details><summary><b>Poetry</b></summary>
We use Poetry for dependency management and packaging.<br>

* Install dependencies: `poetry install`<br>
* Install with development packages: `poetry install --with dev --sync`
* More information about Poetry - [python-poetry.org/docs/basic-usage/#installing-dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies)
</details>

<details><summary><b>Deployment - General Info</b></summary>

1. Select a folder depending on the installation you need.
<ul>
 <li> Local - deployment/local
 <li> Mikr.us - deployment/mikrus
 </ul>

2. Set the environment variables based on the env_example file. The description for each installation is below.
3. Open a terminal and build the Docker containers:
    ```bash
    docker-compose -f docker-compose.yml up --build -d
    ```

</details>

<details><summary><b>Local - Environments</b></summary>

To use app locally with docker, rename the env_example file to .env and set the environment variables:
```
DEBUG=True # for development
SECRET_KEY=<YOUR_SECRET_KEY>
DJANGO_SETTINGS_MODULE=psmproject.settings.development
HOST_NAME=http://localhost:8000
DB_ENGINE=django.db.backends.postgresql_psycopg2
POSTGRES_HOST=stock-market-db
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
REDIS_HOST=redis
REDIS_PORT=6379
```
</details>

<details><summary><b>Mikr.us - Environments</b></summary>

To use the Mikr.us server, rename the env_example file to .env and set the environment variables:
```
# GLOBAL
DJANGO_SETTINGS_MODULE=psmproject.settings.mikrus
HOST_NAME=https://host.name.com
IP4_PORT=<ip port>
SECRET_KEY=<key>
TZ=Europe/Warsaw
# DATABASE
POSTGRES_ENGINE=django.db.backends.postgresql_psycopg2
POSTGRES_DB=db_name
POSTGRES_USER=db_user
POSTGRES_PASSWORD=db_pass
POSTGRES_HOST=stock-market-db
POSTGRES_PORT=5432
# REDIS
REDIS_HOST=redis
REDIS_PORT=6379
# MAIL
SENDGRID_API_KEY=<key>
DEFAULT_FROM_EMAIL=<email address>
# ADMIN CREDENTIALS
ADMIN_USER=<admin_user>
ADMIN_EMAIL=<adminuser@adminmail.mail>
ADMIN_PASS=<admin_password>
```
</details>


## Tests
Unit tests are implemented in Django, and some integration tests are conducted using Selenium and pytest with Selenium for script testing the app running on Docker.

## Contributors
- [rafal-gbc](https://github.com/rafal-gbc)
- [Nicolas Destrieux](https://github.com/ndestrieux)
- [Bartosz Wisniewski](https://github.com/bartwisniewski)
- [Adam Jaworski](https://github.com/adamj2k)
- [ZduBart](https://github.com/ZduBart)

## Screenshot
![Screenshot of task page](src\psmproject\project_static\default\images\screen.png)
