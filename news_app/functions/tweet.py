import json
from requests_oauthlib import OAuth1Session


class Tweet():
    """A singleton class to handle authentication and posting tweets to
      X."""
    # Singleton instance to ensure only one authentication session is
    #  active.
    _instance = None
    # Consumer keys from your X developer app.
    CONSUMER_KEY = '4vR6GxOTZYgu1j63dSBlhEds2'
    CONSUMER_SECRET = 'tUE49zQLaM2bjF9TOixA3rRlVW3xunzKnH6lyNYInwhqE7vuhK'
    # Holds the authenticated OAuth1 session.
    oauth = None

    def __new__(cls):
        """Implements the Singleton pattern. Creates the object and
           authenticates on first call."""
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(Tweet, cls).__new__(cls)
            # Authenticate when the first instance is created.
            cls._instance.authenticate()
        return cls._instance

    def authenticate(self):
        """Handles OAuth1 authentication with the X API."""
        # Step 1: Get a request token from X.
        # Get request token
        request_token_url = (
            "https://api.x.com/oauth/request_token"
            "?oauth_callback=oob&x_auth_access_type=write"
        )
        oauth_session = OAuth1Session(Tweet.CONSUMER_KEY,
                                      client_secret=Tweet.CONSUMER_SECRET)
        try:
            fetch_response = oauth_session.fetch_request_token(
                request_token_url)
        except ValueError:
            print("There may have been an issue with the consumer_key or"
                  " consumer_secret you entered.")
            return

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print(f"Got OAuth token: {resource_owner_key}")

        # Step 2: Prompt the user to authorize the application.
        # Get authorization
        base_authorization_url = "https://api.x.com/oauth/authorize"
        authorization_url = oauth_session.authorization_url(
            base_authorization_url)
        print(f"Please go here and authorize: {authorization_url}")
        verifier = input("Paste the PIN here: ")

        # Step 3: Exchange the request token and verifier for an access
        #  token.
        # Get the access token
        access_token_url = "https://api.x.com/oauth/access_token"
        oauth_session = OAuth1Session(
            Tweet.CONSUMER_KEY,
            client_secret=Tweet.CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,)
        try:
            oauth_tokens = oauth_session.fetch_access_token(access_token_url)
            access_token = oauth_tokens["oauth_token"]
            access_token_secret = oauth_tokens["oauth_token_secret"]

            # Step 4: Create a new OAuth1Session with the access tokens
            #  for making API requests.
            self.oauth = OAuth1Session(
                Tweet.CONSUMER_KEY,
                client_secret=Tweet.CONSUMER_SECRET,
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret,)
        except Exception as e:
            print(f"Failed to get access token: {e}")

    def make_tweet(self, tweet):
        """Posts a tweet using the authenticated OAuth1 session."""
        # Ensure authentication was successful before trying to tweet.
        if not self.oauth:
            raise ValueError('Authentication failed or was not completed!')

        # Post the tweet to the X API v2 endpoint.
        response = self.oauth.post("https://api.x.com/2/tweets", json=tweet)
        # Check for a successful response (201 Created).
        if response.status_code != 201:
            raise Exception(
                f"Request returned an error: {response.status_code}",
                f" {response.text}")

        # Print the success response.
        print(f"Response code: {response.status_code}")
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
