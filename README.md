# psts-api
An API that serves as a backend for a blog website or mobile app.  
Check it out here at [api.psts.xyz](https://api.psts.xyz/).
The front end is here at [fastapi.psts.xyz/](https://fastapi.psts.xyz/)

## Description
The purpose of the api is largely to be a CRUD (create, read, update, delete) app with a database to store the data handled on the front end.
Has some simple endpoints for CRUD of users, blog posts and replies to blog posts.
Has some larger more complicated endpoints to gather several posts and their specific replies all into one object to minimize the number of queries the front end requires. Has endpoints and functionality for users to follow other users to see their posts. I deployed this app myself on a Linode server remotely through ssh using nginx and uvicorn.

![](https://i.imgur.com/M0u4EVd.png)

## Learned on project
- got a familiarity to FastAPI web framework (was very similar coming from Flask)
- using REST API principles in project
- testing in pytest
  - integration test for every endpoint
  - setup separate test database
  - dependancy override to mock user authentication
  - pytest fixtures to monkeypatch database functions to not commit to db
 - learned to make back end and front end and connect the two

## Tech
- Python
- FastAPI web framework
- SQLAlchemy + SQLite for database
- Pytest for testing
- Swagger UI/OpenAPI for interactive documentation
- JWT for user/API authentication
- Nginx and Uvicorn hosted on my Linode Ubuntu server
