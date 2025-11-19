For individuals and teams that wish to provide an additional layer of security to their applications, Opsml offers an opt-in authentication system.

By default, all requests to Opsml use the guest username and password, `guest:guest` that is automatically created when the server is first started. If you wish to make this more strict, we encourage administrators to delete this user and create unique users via the CLI or the web interface.

## Opsml Authentication
Opsml authentication uses a JWT (JSON Web Token) based system. This means that users can authenticate once and receive a token that can be used for subsequent requests without needing to re-enter credentials. This is used for both programmatic access via the API and for the web interface. All Opsml requests are routed through an authentication middleware that checks and validates the JWT token before allowing access to the requested resource.

### Flow (Programmatic Access)

1. **Client Instantiation**: Upon the first instantiation of the Opsml client (this happens in the background), `OPSML_USERNAME` and `OPSML_PASSWORD` environment variables are used to authenticate the user.
2. **Token Retrieval**: Credentials are passed to the server, which validates them. If valid, a new JWT access and refresh token pair are generated. The refresh token is stored on the server and the access token is returned to the client.
3. **Subsequent Requests**: For all subsequent requests, the client uses the access token in the `Authorization` header as a Bearer token, which is automatically validated by the server authentication middleware.
4. **Token Expiry**: If the access token expires and fails validation on the server, the server will attempt to check if the refresh token is still valid. **Note**: The refresh token has a longer expiry time than the access token. If the refresh token is valid, a new access token is generated and returned to the client. If the refresh token is also invalid, the user must re-authenticate.

```shell
# Example of setting environment variables for authentication
export OPSML_USERNAME="your_username"
export OPSML_PASSWORD="your_password"
```

### Flow (Web Interface)
1. **Login Form**: Users access the Opsml web interface and are presented with a login form.
2. **Credentials Submission**: Users enter their credentials, which are sent to the server for validation.
3. **Token Generation**: If the credentials are valid, the server generates a JWT access and refresh token pair.
4. **Session Management**: The access token is stored in the browser's local storage or cookies, and is used for subsequent requests to the web interface.
5. **Token Expiry**: Similar to programmatic access, if the access token expires, the server checks the validity of the refresh token. If valid, a new access token is generated; otherwise, the user must log in again.

## Single Sign-On (SSO) Authentication
Opsml also supports Single Sign-On (SSO) authentication using the OAuth2 and OIDC (OpenID Connect) protocols. This allows users to authenticate using their existing credentials from identity providers such as Okta and Keycloak.

### Setup (Server)
To configure Opsml for SSO authentication, there are a few additional environment variables that need to be set when starting the Opsml server:

| Variable    |  Required By  |   Description       |
|-------------|-------------|--------------------------------------|
| <span class="text-alert">**SSO_PROVIDER**</span> | all | The SSO provider to use. Current options are `default`, `keycloak` and `okta`. |
| <span class="text-alert">**OPSML_CLIENT_ID**</span> | all | The client ID registered with the identity provider. |
| <span class="text-alert">**OPSML_CLIENT_SECRET**</span> | all | The client secret registered with the identity provider. |
| <span class="text-alert">**OPSML_REDIRECT_URI**</span> | all | The redirect URI for the application (must match the identity provider configuration). Note the standard callback for Opsml is `http://{{hostname}}/opsml/user/sso/callback` |
| <span class="text-alert">**OPSML_AUTH_DOMAIN**</span> | all | The domain of the identity provider (e.g., `https://your-identity-provider.com`). |
| <span class="text-alert">**OPSML_AUTH_SCOPE**</span> | all | The scopes to request from the identity provider (e.g., `openid profile email`). Default is `openid profile email`. |
| <span class="text-alert">**OPSML_AUTH_REALM**</span> | keycloak | The Keycloak auth realm |
| <span class="text-alert">**OPSML_AUTHORIZATION_SERVER_ID**</span> | okta | The Okta authorization server ID (if using a custom authorization server). |
| <span class="text-alert">**OPSML_TOKEN_ENDPOINT**</span> | default | The token endpoint for the identity provider. |
| <span class="text-alert">**OPSML_CERT_ENDPOINT**</span> | default | The certificate endpoint for the identity provider. |
| <span class="text-alert">**OPSML_AUTHORIZATION_ENDPOINT**</span> | default | The authorization endpoint for the identity provider. |

### Provider Types and Examples
Opsml supports multiple SSO provider types, each with its own configuration requirements. The following are the currently supported provider types (we will add more in the future):

#### Default
This is a generic default provider type that can be used for most SSO providers.

##### Example Configuration (using Auth0 as an example)
```shell
export SSO_PROVIDER=default && \
export OPSML_CLIENT_ID=my-client-id && \
export OPSML_CLIENT_SECRET=my-client-secret && \
export OPSML_REDIRECT_URI={{opsml-server-domain}}/opsml/user/sso/callback && \
export OPSML_AUTH_DOMAIN={{auth0-domain}} && \
export OPSML_TOKEN_ENDPOINT=oauth/token && \
export OPSML_AUTHORIZATION_ENDPOINT=oauth/authorize && \
export OPSML_CERT_ENDPOINT=.well-known/jwks.json
```

#### Keycloak
This provider type is specifically for [Keycloak](https://www.keycloak.org/) a popular open-source identity and access management solution.

##### Example Configuration
```shell
export SSO_PROVIDER=keycloak && \
export OPSML_CLIENT_ID=my-client-id && \
export OPSML_CLIENT_SECRET=my-client-secret && \
export OPSML_REDIRECT_URI={{opsml-server-domain}}/opsml/user/sso/callback && \
export OPSML_AUTH_DOMAIN={{keycloak-domain}} && \
export OPSML_AUTH_REALM={{keycloak-realm}}
```

#### Okta
This provider type is specifically for [Okta](https://www.okta.com/), a cloud-based identity management service.

##### Example Configuration
```shell
export SSO_PROVIDER=okta && \
export OPSML_CLIENT_ID=my-client-id && \
export OPSML_CLIENT_SECRET=my-client-secret && \
export OPSML_REDIRECT_URI={{opsml-server-domain}}/opsml/user/sso/callback && \
export OPSML_AUTH_DOMAIN={{okta-domain}} && \
export OPSML_AUTHORIZATION_SERVER_ID={{okta-auth-server-id}} # optional is using a custom server
```

### SSO Flow Requirements

#### Programmatic Access

- Opsml requires **Resource Owner Password Credentials (ROPC)** grant type when authenticating through the opsml client in order authenticate without requiring users to manually enter their credentials or redirect them to the identity provider's login page. Because of this, it is recommended to run client workflows in secure environments.

- Users must provide their credentials (username and password) to the Opsml client via the `OPSML_USERNAME` and `OPSML_PASSWORD` environment variables as well as set `OPSML_USE_SSO` to `true`. The Opsml client will then use these credentials to authenticate with the identity provider and obtain an access token.

```shell
# Example of setting environment variables for authentication
export OPSML_USERNAME="your_username"
export OPSML_PASSWORD="your_password"
export OPSML_USE_SSO="true"
```

#### Web Interface

- Opsml uses the **Authorization Code Flow** with PKCE (Proof Key for Code Exchange) to authenticate users via the web interface. This flow is more secure and is recommended for web applications.
- Users are redirected to the identity provider's login page, where they will be prompted to enter their credentials. For state and code validation, the Opsml server generates a random state and code verifier, which are stored in the session. After successful authentication, the user is redirected back to the Opsml web interface with an authorization code.

#### Endpoints

Opsml uses 2 main endpoints for SSO providers based on the OAuth2 and OIDC protocols. These endpoints are constructed based on the SSO provider configuration and the environment variables set in the Opsml server.

- **Certificate Endpoint**: This endpoint is used to retrieve the public keys used to verify the JWT tokens issued by the identity provider. **NOTE**: Opsml uses the JWK (JSON Web Key) format to retrieve the public keys, which are used to validate the JWT tokens received from the identity provider. As an example, this would be the `v1/keys` endpoint for Okta and the `protocol/openid-connect/certs` endpoint for Keycloak.
- **Token Endpoint**: This endpoint is used to obtain access and refresh tokens. **NOTE**: You must ensure your endpoint returns an `id_token` in the response. Opsml will generate its own JWT access token based on the `id_token` received from the identity provider. As an example, this would be the `v1/token` endpoint for Okta and the `protocol/openid-connect/token` endpoint for Keycloak.
- **Authorization Endpoint**: This endpoint is used to initiate the OAuth2 authorization code flow. Users are redirected to this endpoint to log in and authorize the application. Opsml uses the `code` response type to obtain an authorization code, which is then exchanged for tokens at the token endpoint.


