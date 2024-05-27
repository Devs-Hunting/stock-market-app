# Programmers-stock-market

* [Description](#description)
* [Tech-stack](#tech-stack)


## Description
<details><summary><b>General info</b></summary>Place to link programmers and people who need some coding done</details>
<details><summary><b>Application purpose</b></summary>
Application where users can publish programming tasks and select from many offers given by programmers. After delivering solution they can accept it and pay for the job.
There will be also discussion and dispute resolutin mechanism</details>
<details><summary><b>Application flow</b></summary>
- Register and login
- Select your role: customer (C) / provider (P)
- (C) Publish a task
- (P) Find a task that suits your tech-stack and respond with price offer
- (C) Accept from programmers proposals
- (P) Prepare and publish your solution
- (C) Review the solution and accept/decline it
- (C/P) If declined discuss it or use one of the arbiters
- (C) If you have accepted the solution, pay the programmer
- (C/P) Rate each other

</details>

## Tech-stack
<ul>
<li>Python</li>
<li>Django</li>
</ul>

## Usage
### Poetry
<ul>
  <li>Update dependencies with development packages: `poetry install --with dev --sync`</li>
</ul>

### Set OAuth providers for OAuth2 login
Before setting up providers in the application you must register your app on every provider developer console to retrieve client ID and secret. <br>
Our app allows OAuth implementation for Google, LinkedIn and GitHub, for the provider specifics, please follow the link below: <br>
https://docs.allauth.org/en/latest/socialaccount/providers/index.html <br>
The callback URL to be set on provider developer console should look as follows: <br>
http://<your-domain>/accounts/<provider-name>/login/callback/

The first step is to register your domain through the admin panel, go to the "Sites" model and update the already existing instance "example.com" by the domain you will use. <br>
Then configure the provider by creating a new instance "Social applications", choosing the proper provider and giving the client ID and secret you retrieved when registering your app. And add your domain (site) to the chosen sites, then save.

For further documentation, please check: https://docs.allauth.org/en/latest/index.html
