# Gotrue-py
This is a Python port of the [supabase js gotrue client](https://github.com/supabase/gotrue-js/). The current status is that there is not complete feature pairity when compared with the js-client, but this something we are working on.

## Installation
We are still working on making the go-true python library more user-friendly. For now here are some sparse notes on how to install the module

### Poetry
```bash
poetry add gotrue
```

### Pip
```bash
pip install gotrue
```

## Differences to the JS client
It should be noted there are differences to the [JS client](https://github.com/supabase/gotrue-js/). If you feel particulaly strongly about them and want to motivate a change, feel free to make a GitHub issue and we can discuss it there. 

Firstly, feature pairity is not 100% with the [JS client](https://github.com/supabase/gotrue-js/). In most cases we match the methods and attributes of the [JS client](https://github.com/supabase/gotrue-js/) and api classes, but is some places (e.g for browser specific code) it didn't make sense to port the code line for line.

There is also a divergence in terms of how errors are raised. In the [JS client](https://github.com/supabase/gotrue-js/), the errors are returned as part of the object, which the user can choose to process in whatever way they see fit. In this Python client, we raise the errors directly where they originate, as it was felt this was more Pythonic and adhered to the idioms of the language more directly.

In JS we return the error, but in Python we just raise it.
```js
const { data, error } = client.sign_up(...)
```

The other key difference is we do not use pascalCase to encode variable and method names. Instead we use the snake_case convention adopted in the Python language. 

## Usage
To instanciate the client, you'll need the URL and any request headers at a minimum.
```python
from gotrue import Client

headers = {
    "apiKey": "my-mega-awesome-api-key",
    # ... any other headers you might need.
}
client: Client = Client(url="www.genericauthwebsite.com", headers=headers)
```

To send a magic email link to the user, just provide the email kwarg to the `sign_in` method:
```python
user: Dict[str, Any] = client.sign_up(email="example@gmail.com")
```

To login with email and password, provide both to the `sign_in` method:
```python
user: Dict[str, Any] = client.sign_up(email="example@gmail.com", password="*********")
```

To sign out of the logged in user, call the `sign_out` method. We can then assert that the session and user are null values.
```python
client.sign_out()
assert client.user() is None
assert client.session() is None
```

We can refesh a users session.
```python
# The user should already be signed in at this stage.
user = client.refresh_session()
assert client.user() is not None
assert client.session() is not None
```

## Tests
At the moment we use a pre-defined supabase instance to test the functionality. This may change over time. You can run the tests like so:
```bash
SUPABASE_TEST_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYxMjYwOTMyMiwiZXhwIjoxOTI4MTg1MzIyfQ.XL9W5I_VRQ4iyQHVQmjG0BkwRfx6eVyYB3uAKcesukg" \
SUPABASE_TEST_URL="https://tfsatoopsijgjhrqplra.supabase.co" \
pytest -sx
```

## Contributions
We would be immensely grateful for any contributions to this project. In particular are the following items:
- [x] Figure out to use either Sessions to manage headers or allow passing in of headers
- [ ] Add documentation.
- [ ] Add more tests.
- [ ] Ensuring feature-parity with the js-client.
- [ ] Supporting 3rd party provider authentication.
- [ ] Implement a js port of setTimeout for the refresh session code.

