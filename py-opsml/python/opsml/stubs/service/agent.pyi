#### begin imports ####
from typing import Any, Dict, List, Optional, Union

#### end of imports ####

class AgentProvider:
    """Provider configuration for agent services.

    Defines the organization and URL for an agent provider, used to configure
    connections to external agent services.
    """

    def __init__(
        self,
        organization: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """Initialize an AgentProvider.

        Args:
            organization (str | None):
                Organization identifier for the agent provider. Defaults to empty string.
            url (str | None):
                Base URL for the agent provider service. Defaults to empty string.
        """

    @property
    def organization(self) -> str:
        """Organization identifier for the agent provider."""

    @organization.setter
    def organization(self, organization: str) -> None: ...
    @property
    def url(self) -> str:
        """Base URL for the agent provider service."""

    @url.setter
    def url(self, url: str) -> None: ...

class AgentInterface:
    """Interface configuration for agent communication protocols.

    Defines the connection parameters and protocol settings for communicating
    with agent services, including URL, protocol binding, version, and tenant
    information.
    """

    def __init__(
        self,
        url: str,
        protocol_binding: str,
        protocol_version: str,
        tenant: Optional[str] = None,
    ) -> None:
        """Initialize an AgentInterface.

        Args:
            url (str):
                Complete URL for the agent interface endpoint.
            protocol_binding (str):
                Protocol binding type (e.g., "http", "grpc", "websocket").
            protocol_version (str):
                Version of the protocol being used.
            tenant (str | None):
                Tenant identifier for multi-tenant deployments. Defaults to empty string.
        """

    @property
    def url(self) -> str:
        """Complete URL for the agent interface endpoint."""

    @url.setter
    def url(self, url: str) -> None: ...
    @property
    def protocol_binding(self) -> str:
        """Protocol binding type for agent communication."""

    @protocol_binding.setter
    def protocol_binding(self, protocol_binding: str) -> None: ...
    @property
    def protocol_version(self) -> str:
        """Version of the communication protocol."""

    @protocol_version.setter
    def protocol_version(self, protocol_version: str) -> None: ...
    @property
    def tenant(self) -> str:
        """Tenant identifier for multi-tenant deployments."""

    @tenant.setter
    def tenant(self, tenant: str) -> None: ...

class AgentExtension:
    """Extension configuration for agent capabilities.

    Defines custom extensions that can be added to an agent to provide additional
    functionality beyond the standard A2A specification. Extensions include a URI,
    optional description, parameters, and whether they are required.
    """

    def __init__(
        self,
        uri: str,
        description: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        required: bool = False,
    ) -> None:
        """Initialize an AgentExtension.

        Args:
            uri (str):
                URI identifying the extension specification or implementation.
            description (str | None):
                Human-readable description of the extension's purpose and functionality.
            params (Dict[str, Any] | None):
                Configuration parameters for the extension as a dictionary.
            required (bool):
                Whether this extension must be supported by clients. Defaults to False.
        """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the extension."""

    @description.setter
    def description(self, description: Optional[str]) -> None: ...
    @property
    def params(self) -> Optional[Dict[str, Any]]:
        """Configuration parameters for the extension."""

    @property
    def required(self) -> bool:
        """Whether this extension must be supported by clients."""

    @required.setter
    def required(self, required: bool) -> None: ...
    @property
    def uri(self) -> str:
        """URI identifying the extension specification."""

    @uri.setter
    def uri(self, uri: str) -> None: ...

class AgentCapabilities:
    """Capabilities configuration for agent features.

    Defines the set of capabilities that an agent supports, including streaming,
    push notifications, extended agent card support, and custom extensions.
    """

    def __init__(
        self,
        streaming: bool = False,
        push_notifications: bool = False,
        extended_agent_card: bool = False,
        extensions: Optional[List[AgentExtension]] = None,
    ) -> None:
        """Initialize AgentCapabilities.

        Args:
            streaming (bool):
                Whether the agent supports streaming responses. Defaults to False.
            push_notifications (bool):
                Whether the agent supports server-initiated push notifications. Defaults to False.
            extended_agent_card (bool):
                Whether the agent supports the extended agent card format. Defaults to False.
            extensions (List[AgentExtension] | None):
                List of custom extensions supported by the agent. Defaults to empty list.
        """

    @property
    def streaming(self) -> bool:
        """Whether the agent supports streaming responses."""

    @streaming.setter
    def streaming(self, streaming: bool) -> None: ...
    @property
    def push_notifications(self) -> bool:
        """Whether the agent supports push notifications."""

    @push_notifications.setter
    def push_notifications(self, push_notifications: bool) -> None: ...
    @property
    def extended_agent_card(self) -> bool:
        """Whether the agent supports extended agent card format."""

    @extended_agent_card.setter
    def extended_agent_card(self, extended_agent_card: bool) -> None: ...
    @property
    def extensions(self) -> List[AgentExtension]:
        """List of custom extensions supported by the agent."""

    @extensions.setter
    def extensions(self, extensions: List[AgentExtension]) -> None: ...

class SecurityRequirement:
    """Security scheme requirement specification.

    Defines which security schemes must be satisfied for access, allowing
    multiple schemes to be required simultaneously.
    """

    def __init__(
        self,
        schemes: List[str],
    ) -> None:
        """Initialize a SecurityRequirement.

        Args:
            schemes (List[str]):
                List of security scheme names that must be satisfied.
        """

    @property
    def schemes(self) -> List[str]:
        """List of required security scheme names."""

    @schemes.setter
    def schemes(self, schemes: List[str]) -> None: ...

class AgentSkill:
    """Agent capability or skill definition.

    Describes a specific capability that an agent can perform, including
    examples, supported input/output modes, and security requirements.
    """

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tags: Optional[List[str]] = None,
        examples: Optional[List[str]] = None,
        input_modes: Optional[List[str]] = None,
        output_modes: Optional[List[str]] = None,
        security_requirements: Optional[List[SecurityRequirement]] = None,
    ) -> None:
        """Initialize an AgentSkill.

        Args:
            id (str):
                Unique identifier for the skill.
            name (str):
                Human-readable name of the skill.
            description (str):
                Detailed description of what the skill does.
            tags (List[str] | None):
                Categorization tags for the skill. Defaults to empty list.
            examples (List[str] | None):
                Example usage scenarios or prompts. Defaults to empty list.
            input_modes (List[str] | None):
                Supported input modalities (e.g., "text", "image", "audio").
            output_modes (List[str] | None):
                Supported output modalities (e.g., "text", "image", "audio").
            security_requirements (List[SecurityRequirement] | None):
                Security requirements needed to access this skill.
        """

    @property
    def description(self) -> str:
        """Detailed description of the skill."""

    @description.setter
    def description(self, description: str) -> None: ...
    @property
    def examples(self) -> List[str]:
        """Example usage scenarios for the skill."""

    @examples.setter
    def examples(self, examples: List[str]) -> None: ...
    @property
    def id(self) -> str:
        """Unique identifier for the skill."""

    @id.setter
    def id(self, id: str) -> None: ...
    @property
    def input_modes(self) -> Optional[List[str]]:
        """Supported input modalities for the skill."""

    @input_modes.setter
    def input_modes(self, input_modes: Optional[List[str]]) -> None: ...
    @property
    def name(self) -> str:
        """Human-readable name of the skill."""

    @name.setter
    def name(self, name: str) -> None: ...
    @property
    def output_modes(self) -> Optional[List[str]]:
        """Supported output modalities for the skill."""

    @output_modes.setter
    def output_modes(self, output_modes: Optional[List[str]]) -> None: ...
    @property
    def security_requirements(self) -> Optional[List[SecurityRequirement]]:
        """Security requirements for accessing the skill."""

    @security_requirements.setter
    def security_requirements(self, security_requirements: Optional[List[SecurityRequirement]]) -> None: ...
    @property
    def tags(self) -> List[str]:
        """Categorization tags for the skill."""

    @tags.setter
    def tags(self, tags: List[str]) -> None: ...

class ApiKeySecurityScheme:
    """API Key authentication security scheme.

    Defines authentication using an API key that can be placed in headers,
    query parameters, or cookies.
    """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the security scheme."""

    @property
    def location(self) -> str:
        """Location of the API key (e.g., "header", "query", "cookie")."""

    @property
    def name(self) -> str:
        """Name of the header, query parameter, or cookie."""

class HttpAuthSecurityScheme:
    """HTTP authentication security scheme.

    Defines HTTP-based authentication using schemes like Basic, Bearer, or Digest.
    Commonly used for JWT tokens and OAuth 2.0 Bearer tokens.
    """

    @property
    def scheme(self) -> str:
        """Authentication scheme (e.g., "Basic", "Bearer", "Digest")."""

    @property
    def bearer_format(self) -> str:
        """Format hint for Bearer tokens (e.g., "JWT")."""

    @property
    def description(self) -> str:
        """Human-readable description of the authentication scheme."""

class MtlsSecurityScheme:
    """Mutual TLS (mTLS) authentication security scheme.

    Defines certificate-based mutual authentication where both client and server
    present certificates to establish trust.
    """

    @property
    def description(self) -> str:
        """Human-readable description of the mTLS requirements."""

class Oauth2SecurityScheme:
    """OAuth 2.0 security scheme definition.

    Configures OAuth 2.0 authentication flows, including authorization endpoints,
    token endpoints, and available scopes for authorization.
    """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the OAuth 2.0 configuration."""

    @property
    def flows(self) -> "OAuthFlows":
        """OAuth 2.0 flow configurations (authorization code, client credentials, etc.)."""

    @property
    def oauth2_metadata_url(self) -> Optional[str]:
        """URL to OAuth 2.0 Authorization Server Metadata (RFC 8414)."""

class OpenIdConnectSecurityScheme:
    """OpenID Connect security scheme definition.

    Configures OpenID Connect authentication, which extends OAuth 2.0 to provide
    identity verification and user profile information.
    """

    @property
    def description(self) -> Optional[str]:
        """Human-readable description of the OpenID Connect configuration."""

    @property
    def open_id_connect_url(self) -> Optional[str]:
        """OpenID Connect discovery document URL (typically /.well-known/openid-configuration)."""

class SecurityScheme:
    """Union type for all supported security schemes.

    Represents one of several authentication/authorization mechanisms that can be
    used to secure agent access. The specific scheme type is determined at runtime
    based on the provided configuration object.
    """

    def __init__(
        self,
        scheme: Union[
            ApiKeySecurityScheme,
            HttpAuthSecurityScheme,
            MtlsSecurityScheme,
            Oauth2SecurityScheme,
            OpenIdConnectSecurityScheme,
        ],
    ) -> None:
        """Initialize a SecurityScheme from a specific scheme type.

        Args:
            scheme (
                ApiKeySecurityScheme |
                HttpAuthSecurityScheme |
                MtlsSecurityScheme |
                Oauth2SecurityScheme |
                OpenIdConnectSecurityScheme
                ):
                The specific security scheme configuration. Must be one of the supported scheme types.

        Raises:
            TypeError:
                If the provided scheme is not a recognized security scheme type.

        Example:
            ```python
            from opsml import SecurityScheme, ApiKeySecurityScheme

            api_key_scheme = ApiKeySecurityScheme()
            security = SecurityScheme(api_key_scheme)
            ```
        """

class OAuthFlows:
    """OAuth 2.0 flow configurations container.

    Groups various OAuth 2.0 authentication flows that can be supported by the agent,
    allowing clients to choose the most appropriate flow for their use case.
    """

    @property
    def authorization_code(self) -> Optional[AuthorizationCodeFlow]:
        """Authorization Code flow configuration with optional PKCE support."""

    @property
    def client_credentials(self) -> Optional[ClientCredentialsFlow]:
        """Client Credentials flow for machine-to-machine authentication."""

    @property
    def device_code(self) -> Optional[DeviceCodeFlow]:
        """Device Code flow for devices with limited input capabilities."""

    @property
    def implicit(self) -> Optional[ImplicitAuthFlow]:
        """Implicit flow (legacy, not recommended for new applications)."""

    @property
    def password(self) -> Optional[PassWordAuthFlow]:
        """Resource Owner Password Credentials flow (use with caution)."""

class AuthorizationCodeFlow:
    """OAuth 2.0 Authorization Code flow configuration.

    The most secure OAuth 2.0 flow for web and mobile applications, with
    optional PKCE (Proof Key for Code Exchange) for enhanced security.
    """

    @property
    def authorization_url(self) -> str:
        """URL where users grant authorization (e.g., /oauth/authorize)."""

    @property
    def pkce_required(self) -> bool:
        """Whether PKCE is required for this flow."""

    @property
    def refresh_url(self) -> str:
        """URL for refreshing access tokens."""

    @property
    def scopes(self) -> Dict[str, str]:
        """Available OAuth scopes mapped to their descriptions."""

    @property
    def token_url(self) -> str:
        """URL for exchanging authorization code for tokens."""

class ClientCredentialsFlow:
    """OAuth 2.0 Client Credentials flow configuration.

    Used for machine-to-machine authentication where no user interaction
    is required. Suitable for backend services and automated processes.
    """

    @property
    def refresh_url(self) -> str:
        """URL for refreshing access tokens."""

    @property
    def scopes(self) -> Dict[str, str]:
        """Available OAuth scopes mapped to their descriptions."""

    @property
    def token_url(self) -> str:
        """URL for obtaining access tokens using client credentials."""

class DeviceCodeFlow:
    """OAuth 2.0 Device Code flow configuration.

    Designed for devices with limited input capabilities (smart TVs, IoT devices).
    Users authenticate on a separate device using a code displayed on the target device.
    """

    @property
    def device_authorization_url(self) -> str:
        """URL where device requests a user code and device code."""

    @property
    def refresh_url(self) -> str:
        """URL for refreshing access tokens."""

    @property
    def scopes(self) -> Dict[str, str]:
        """Available OAuth scopes mapped to their descriptions."""

    @property
    def token_url(self) -> str:
        """URL for polling to exchange device code for tokens."""

class ImplicitAuthFlow:
    """OAuth 2.0 Implicit flow configuration.

    Legacy flow originally designed for browser-based applications. Not recommended
    for new applications due to security concerns. Use Authorization Code with PKCE instead.
    """

    @property
    def authorization_url(self) -> str:
        """URL where tokens are obtained directly from authorization endpoint."""

    @property
    def refresh_url(self) -> str:
        """URL for refreshing access tokens."""

    @property
    def scopes(self) -> Dict[str, str]:
        """Available OAuth scopes mapped to their descriptions."""

class PassWordAuthFlow:
    """OAuth 2.0 Resource Owner Password Credentials flow configuration.

    Allows direct exchange of username/password for tokens. Only use when other
    flows are not feasible and with highly trusted first-party applications.
    """

    @property
    def refresh_url(self) -> str:
        """URL for refreshing access tokens."""

    @property
    def scopes(self) -> Dict[str, str]:
        """Available OAuth scopes mapped to their descriptions."""

    @property
    def token_url(self) -> str:
        """URL for exchanging username/password for tokens."""

class AgentCardSignature:
    """Digital signature for agent card verification.

    Implements JSON Web Signature (JWS) for cryptographically verifying the
    authenticity and integrity of agent card metadata.
    """

    @property
    def header(self) -> Optional[Dict[str, str]]:
        """JWS unprotected header with additional metadata (e.g., key ID)."""

    @property
    def protected(self) -> str:
        """Base64url-encoded JWS protected header containing algorithm and other claims."""

    @property
    def signature(self) -> str:
        """Base64url-encoded signature over the protected header and payload."""

class AgentSpec:
    """Complete agent specification conforming to A2A protocol.

    Comprehensive definition of an agent, including its capabilities, skills,
    supported interfaces, security requirements, and metadata. This is the root
    object for agent discovery and integration.
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        supported_interfaces: List[AgentInterface],
        capabilities: AgentCapabilities,
        default_input_modes: List[str],
        default_output_modes: List[str],
        skills: List[AgentSkill],
        provider: Optional[AgentProvider] = None,
        documentation_url: Optional[str] = None,
        icon_url: Optional[str] = None,
        security_schemes: Optional[Dict[str, SecurityScheme]] = None,
        security_requirements: Optional[List[SecurityRequirement]] = None,
        signatures: Optional[List[AgentCardSignature]] = None,
    ) -> None:
        """Initialize an AgentSpec.

        Args:
            name (str):
                Human-readable name of the agent.
            description (str):
                Detailed description of the agent's purpose and functionality.
            version (str):
                Semantic version of the agent specification (e.g., "1.0.0").
            supported_interfaces (List[AgentInterface]):
                List of protocol interfaces the agent supports for communication.
            capabilities (AgentCapabilities):
                Feature capabilities the agent provides (streaming, extensions, etc.).
            default_input_modes (List[str]):
                Default input modalities supported (e.g., ["text", "image"]).
            default_output_modes (List[str]):
                Default output modalities provided (e.g., ["text", "json"]).
            skills (List[AgentSkill]):
                List of specific skills/capabilities the agent can perform.
            provider (AgentProvider | None):
                Organization or entity providing the agent.
            documentation_url (str | None):
                URL to comprehensive agent documentation.
            icon_url (str | None):
                URL to agent's icon/logo for UI display.
            security_schemes (Dict[str, SecurityScheme] | None):
                Named security scheme definitions available for authentication.
            security_requirements (List[SecurityRequirement] | None):
                Security requirements that must be satisfied to access the agent.
            signatures (List[AgentCardSignature] | None):
                Cryptographic signatures verifying the agent card's authenticity.
        """

    @property
    def capabilities(self) -> AgentCapabilities:
        """Feature capabilities the agent provides."""

    @capabilities.setter
    def capabilities(self, capabilities: AgentCapabilities) -> None: ...
    @property
    def default_output_modes(self) -> List[str]:
        """Default output modalities provided by the agent."""

    @default_output_modes.setter
    def default_output_modes(self, default_output_modes: List[str]) -> None: ...
    @property
    def default_input_modes(self) -> List[str]:
        """Default input modalities supported by the agent."""

    @default_input_modes.setter
    def default_input_modes(self, default_input_modes: List[str]) -> None: ...
    @property
    def description(self) -> str:
        """Detailed description of the agent's purpose and functionality."""

    @description.setter
    def description(self, description: str) -> None: ...
    @property
    def documentation_url(self) -> Optional[str]:
        """URL to comprehensive agent documentation."""

    @documentation_url.setter
    def documentation_url(self, documentation_url: Optional[str]) -> None: ...
    @property
    def icon_url(self) -> Optional[str]:
        """URL to agent's icon for UI display."""

    @icon_url.setter
    def icon_url(self, icon_url: Optional[str]) -> None: ...
    @property
    def name(self) -> str:
        """Human-readable name of the agent."""

    @name.setter
    def name(self, name: str) -> None: ...
    @property
    def provider(self) -> Optional[AgentProvider]:
        """Organization or entity providing the agent."""

    @provider.setter
    def provider(self, provider: Optional[AgentProvider]) -> None: ...
    @property
    def security_requirements(self) -> Optional[List[SecurityRequirement]]:
        """Security requirements for accessing the agent."""

    @security_requirements.setter
    def security_requirements(self, security_requirements: Optional[List[SecurityRequirement]]) -> None: ...
    @property
    def security_schemes(self) -> Optional[Dict[str, SecurityScheme]]:
        """Named security scheme definitions for authentication."""

    @security_schemes.setter
    def security_schemes(self, security_schemes: Optional[Dict[str, SecurityScheme]]) -> None: ...
    @property
    def signatures(self) -> Optional[List[AgentCardSignature]]:
        """Cryptographic signatures verifying agent card authenticity."""

    @signatures.setter
    def signatures(self, signatures: Optional[List[AgentCardSignature]]) -> None: ...
    @property
    def skills(self) -> List[AgentSkill]:
        """List of specific skills the agent can perform."""

    @skills.setter
    def skills(self, skills: List[AgentSkill]) -> None: ...
    @property
    def supported_interfaces(self) -> List[AgentInterface]:
        """Protocol interfaces the agent supports for communication."""

    @supported_interfaces.setter
    def supported_interfaces(self, supported_interfaces: List[AgentInterface]) -> None: ...
    @property
    def version(self) -> str:
        """Semantic version of the agent specification."""

    @version.setter
    def version(self, version: str) -> None: ...

__all__ = [
    "AgentProvider",
    "AgentInterface",
    "AgentExtension",
    "AgentCapabilities",
    "SecurityRequirement",
    "AgentSkill",
    "ApiKeySecurityScheme",
    "HttpAuthSecurityScheme",
    "MtlsSecurityScheme",
    "Oauth2SecurityScheme",
    "OpenIdConnectSecurityScheme",
    "SecurityScheme",
    "OAuthFlows",
    "AuthorizationCodeFlow",
    "ClientCredentialsFlow",
    "DeviceCodeFlow",
    "ImplicitAuthFlow",
    "PassWordAuthFlow",
    "AgentCardSignature",
    "AgentSpec",
]
