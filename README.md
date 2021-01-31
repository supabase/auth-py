
# Gotrue-py

## Status: POC
This is a hacky `gotrue-py` client conceived during a very draggy class. It was developed against the [supabase](https://github.com/supabase/gotrue) fork of netlify's gotrue. The design mirrors that of [GoTrue-elixir](https://github.com/joshnuss/gotrue-elixir)

## Installation

Here's how you'd install the library with gotrue 
### With Poetry

`poetry add gotrue`

### With pip
`pip3 install gotrue`


### Usage
```
import gotrue

client = gotrue.Client("www.genericauthwebsite.com")
credentials = {"email": "anemail@gmail.com", "password": "gmebbnok"}
client.sign_up(credentials)
client.sign_in(credentials)


```


### TODOS:
- [] Add Documentation

