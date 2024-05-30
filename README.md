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
This web application makes it easy to access programming services for those seeking help, and for freelance programmers to connect with potential clients.<BR>
User interface is in English, but a Polish version is also available.

<details><summary><b>Application purpose</b></summary>
Application where users can publish programming tasks and select from many offers given by programmers. After delivering solution they can accept it and pay for the job.</details>

<details><summary><b>Application flow</b></summary>

- Register and login
- Select your role: client (CL) / contractor (CO)
- (CL) Publish a task, set budget and time to complete task
- (CO) Find a task that suits your tech-stack and respond with price offer
- (CL) Choose and accept offer from programmer
- (CO) Prepare and publish your solution
- (CL) Review the solution and accept/decline it
- (CL/CO) If declined discuss it or use one of the arbiters
- (CL) If you have accepted the solution, pay the programmer

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

More information about Poetry - [python-poetry.org/docs/basic-usage/#installing-dependencies](https://python-poetry.org/docs/basic-usage/#installing-dependencies)
</details>

<details><summary><b>Deployment - general info</b></summary>

1. Wybierz folder w zależności od instalacji jaka jest Ci potrzebna.
<ul>
 <li> Local - deployment/local
 <li> Mikr.us - deployment/mikrus
 </ul>

2. Ustaw zmienne środowiskoe na podstawie pliku env_example (mikr.us) lub w pliku docker-compose.yml. Opis dla poszczególnych instalacji jest poniżej.
3. In docker.compose.yml set variable to choose main Django setting file:
    ```
    DJANGO_SETTINGS_MODULE = <psmproject.settings.(development|production|mikrus)>
    ```
4. Open in terminal and build docker containers.
    ```bash
    docker-compose -f docker-compose.yml up --build -d
    ```

</details>

<details><summary><b>Local - environments</b></summary>

If you want to use app locally with docker, you must set environment variables in file docker-compose.yml.
```
- DEBUG=True # for development
- DJANGO_SETTINGS_MODULE=psmproject.settings.development
- HOST_NAME=http://localhost:8000
- DB_ENGINE=django.db.backends.postgresql_psycopg2
- POSTGRES_HOST=stock-market-db
- POSTGRES_DB=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- POSTGRES_PORT=5432
- CELERY_BROKER_URL=redis://redis:6379
- CELERY_RESULT_BACKEND=redis://redis:6379
- REDIS_HOST=redis
- REDIS_PORT=6379
```
</details>

<details><summary><b>Mikr.us - environments</b></summary>

If you want to use Mikr.us server, you must change name of file 'env_example' to '.env' and set environment variables.
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
Unit tests were made in Django and some live integration test with use of Selenium and pytest with selenium for script testing app running on docker.

## Contributors
- [rafal-gbc](https://github.com/rafal-gbc)
- [Nicolas Destrieux](https://github.com/ndestrieux)
- [Bartosz Wisniewski](https://github.com/bartwisniewski)
- [Adam Jaworski](https://github.com/adamj2k)
- [ZduBart](https://github.com/ZduBart)

## Screenshot
![Screenshot of task page](src\psmproject\project_static\default\images\screen.png)
