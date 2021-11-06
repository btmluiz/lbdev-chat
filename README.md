
# ChatSystem - Backend

This project is a example of a small chat system where the users could send messages to each other.

#### Obs: this project still in development some features may not work, please any bug found or any sugestion please open a issue.

## Deployment

To deploy this project create a `.env` file at the root of the project use the example bellow:

```bash
  ALLOWED_HOSTS='{HOSTS}' # (optional) default='*'
  SECRET_KEY='{DJANGO SECRET KEY}' # (optional) default = generate a random secret key
  DB_ENGINE='{DATABASE ENGINE}' # (default = 'psql') 'psql' or 'mysql'
  DB_HOST='{DATABASE HOST}' # default='127.0.0.1'
  DB_NAME='{DATABASE NAME}' # default = 'postgres'
  DB_USER='{DATABASE USER}' # default = 'postgres'
  DB_PASSWORD='{DATABASE PASSWORD}' # default = 'development'
  DB_PORT='{DATABASE PORT}' # default = 5432
  DEBUG='{DEBUG ENABLE}' # default = 0
  
  # REDIS SETUP
  REDIS_URL='{REDIS_URL}' # (optional) if set is used insted of REDIS_HOST and REDIS_PORT
  REDIS_HOST='{REDIS HOST}' # default = 'channel_layer'
  REDIS_PORT='{REDIS PORT}' # default = 6379

  # GOOGLE BUCKET SETUP (optional)
  GS_BUCKET_NAME='{GOOGLE BUCKET NAME}'

  # POSTGRES SETUP
  POSTGRES_DB="{POSTGRES DATABASE NAME}"
  POSTGRES_USER="{POSTGRES USER NAME}"
  POSTGRES_PASSWORD="{"POSTGRES USER PASSWORD}"

```

To deploy the client you can use [lbdev-chat-client](https://github.com/btmluiz/lbdev-chat-client)
## API Reference

Api reference can be find in the swagger endpoint

```
  /swagger/
```

or at redoc

```
  /redoc/
```



## WebSocket reference

```
   /chat/
```

This is the main endpoint to connect to all chat function.

#### Content syntax

```json
 {
     "type": "string",
     "data": "object"
 }
```

### Request types

#### authorization
syntax:
```json
 {
     "token": "string"
 }
```
Use the token provided at the login endpoint from API

#### get_contacts
syntax:
```json
 {}
```

#### message
syntax:
```json
 {
     "to": "string",
     "content": "string"
 }
```
send a message to a user

#### get_contact

```json
 {
     "id": "string",
 }
```
get informations abount a contact
## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/lfsbraga/)

