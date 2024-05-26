# Programmers-stock-market

* [Description](#description)
* [Tech-stack](#tech-stack)
* [Live demo](#live-demo)
* [Setup](#setup)
* [Environment](#environment)


## Description
<b>General info</b><br>
Application makes it easy to access programming services for those seeking help, and for freelance programmers to connect with potential clients. Place to link programmers and people who need some coding done.<BR>
User interface is in English, but also has translation to Polish.

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
We prepare the live demo of app on Mikr.us server. Please sing up and feel free to test it.<br>
[stockmarket.toadres.pl](https://stockmarket.toadres.pl)

## Setup
<details><summary><b>Poetry</b></summary>
We use Poetry for dependency management and packaging.
<ul>
  <li>Update dependencies with development packages: `poetry install --with dev --sync`</li>
</ul>
</details>

<details><summary><b>Environment</b></summary>

Most environment variables have their default values in setting files.<br>
Environment variables to set:
```
SECRET_KEY=<your secret key>
ALLOWED_HOSTS = <allowed host name>
```
If you want to use PostgreSQL please set:
```
"ENGINE"="YOUR_DATABASE_ENGINE
"NAME"="YOUR_DATABASE_NAME"
"USER": "YOUR_DATABASE_USER"
"PASSWORD": "YOUR_DATABASE_PASSWORD"
"HOST": "YOUR_DATABASE_HOST"
"PORT": "YOUR_"DATABASE_PORT"
```
</details>

<details><summary><b>Docker</b></summary>

Go to deployment/local directory.
In docker.compose.yml set variable to choose django setting file:
```
DJANGO_SETTINGS_MODULE = <psmproject.settings.(development|production|mikrus)>
```
 Open in terminal:
```bash
docker-compose -f docker-compose.yml up --build -d
```


<details><summary><b>Mikr.us</b></summary>

If you want to use server Mikr.us, you must set environment variables.
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

## Contributors
- [rafal-gbc](https://github.com/rafal-gbc)
- [Nicolas Destrieux](https://github.com/ndestrieux)
- [Bartosz Wisniewski](https://github.com/bartwisniewski)
- [Adam Jaworski](https://github.com/adamj2k)
- [ZduBart](https://github.com/ZduBart)

## Screenshot
![Screenshot of task page](src\psmproject\project_static\default\images\screen.png)
