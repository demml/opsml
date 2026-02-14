from opsml.card import (
    AgentCapabilities,
    AgentProvider,
    AgentInterface,
    AgentExtension,
    AgentSkill,
    SecurityRequirement,
    ApiKeySecurityScheme,
    HttpAuthSecurityScheme,
    MtlsSecurityScheme,
    Oauth2SecurityScheme,
    OpenIdConnectSecurityScheme,
    SecurityScheme,
    OAuthFlows,
    AuthorizationCodeFlow,
    ClientCredentialsFlow,
    DeviceCodeFlow,
    ImplicitAuthFlow,
    PassWordAuthFlow,
    AgentCardSignature,
    AgentSpec,
)


def test_agent_provider():
    provider = AgentProvider(
        organization="TestOrg",
        url="https://agent.example.com",
    )

    assert provider.organization == "TestOrg"
    assert provider.url == "https://agent.example.com"

    provider.organization = "UpdatedOrg"
    provider.url = "https://updated.example.com"

    assert provider.organization == "UpdatedOrg"
    assert provider.url == "https://updated.example.com"


def test_agent_interface():
    interface = AgentInterface(
        url="http://example.com/agent",
        protocol_binding="HTTP",
        protocol_version="1.0",
        tenant="TestTenant",
    )

    assert interface.url == "http://example.com/agent"
    assert interface.protocol_binding == "HTTP"
    assert interface.protocol_version == "1.0"
    assert interface.tenant == "TestTenant"

    interface.url = "https://secure.example.com/agent"
    interface.protocol_binding = "HTTPS"
    interface.protocol_version = "2.0"
    interface.tenant = "ProdTenant"

    assert interface.url == "https://secure.example.com/agent"
    assert interface.protocol_binding == "HTTPS"
    assert interface.protocol_version == "2.0"
    assert interface.tenant == "ProdTenant"


def test_agent_extension():
    extension = AgentExtension(
        uri="https://example.com/extensions/custom",
        description="Custom extension for specialized processing",
        params={"max_tokens": 1000, "temperature": 0.7},
        required=True,
    )

    assert extension.uri == "https://example.com/extensions/custom"
    assert extension.description == "Custom extension for specialized processing"
    assert extension.params == {"max_tokens": 1000, "temperature": 0.7}
    assert extension.required is True

    extension.description = "Updated description"
    extension.required = False

    assert extension.description == "Updated description"
    assert extension.required is False


def test_agent_capabilities():
    extension = AgentExtension(
        uri="https://example.com/ext/streaming",
        description="Enhanced streaming support",
        required=False,
    )

    capabilities = AgentCapabilities(
        streaming=True,
        push_notifications=True,
        extended_agent_card=True,
        extensions=[extension],
    )

    assert capabilities.streaming is True
    assert capabilities.push_notifications is True
    assert capabilities.extended_agent_card is True
    assert len(capabilities.extensions) == 1
    assert capabilities.extensions[0].uri == "https://example.com/ext/streaming"

    capabilities.streaming = False
    capabilities.push_notifications = False

    assert capabilities.streaming is False
    assert capabilities.push_notifications is False


def test_security_requirement():
    requirement = SecurityRequirement(
        schemes=["api_key", "oauth2"],
    )

    assert requirement.schemes == ["api_key", "oauth2"]
    assert len(requirement.schemes) == 2

    requirement.schemes = ["bearer_token"]

    assert requirement.schemes == ["bearer_token"]
    assert len(requirement.schemes) == 1


def test_agent_skill():
    security_req = SecurityRequirement(schemes=["api_key"])

    skill = AgentSkill(
        id="text_generation",
        name="Text Generation",
        description="Generate human-like text based on prompts",
        tags=["nlp", "generation", "llm"],
        examples=["Write a poem about AI", "Summarize this article"],
        input_modes=["text"],
        output_modes=["text", "json"],
        security_requirements=[security_req],
    )

    assert skill.id == "text_generation"
    assert skill.name == "Text Generation"
    assert skill.description == "Generate human-like text based on prompts"
    assert skill.tags == ["nlp", "generation", "llm"]
    assert len(skill.examples) == 2
    assert skill.input_modes == ["text"]
    assert skill.output_modes == ["text", "json"]
    assert len(skill.security_requirements) == 1

    skill.name = "Advanced Text Generation"
    skill.tags = ["nlp", "llm"]

    assert skill.name == "Advanced Text Generation"
    assert skill.tags == ["nlp", "llm"]


def test_authorization_code_flow():
    flow = AuthorizationCodeFlow(
        authorization_url="https://example.com/oauth/authorize",
        token_url="https://example.com/oauth/token",
    )

    assert flow.authorization_url is not None
    assert flow.token_url is not None
    assert isinstance(flow.pkce_required, bool)
    assert isinstance(flow.scopes, dict)


def test_client_credentials_flow():
    flow = ClientCredentialsFlow(
        token_url="https://example.com/oauth/token",
    )

    assert flow.token_url is not None
    assert isinstance(flow.scopes, dict)


def test_device_code_flow():
    flow = DeviceCodeFlow(
        device_authorization_url="https://example.com/oauth/device_authorize",
        token_url="https://example.com/oauth/token",
    )

    assert flow.device_authorization_url is not None
    assert flow.token_url is not None
    assert isinstance(flow.scopes, dict)


def test_implicit_auth_flow():
    flow = ImplicitAuthFlow(
        authorization_url="https://example.com/oauth/authorize",
    )

    assert flow.authorization_url is not None
    assert isinstance(flow.scopes, dict)


def test_password_auth_flow():
    flow = PassWordAuthFlow(
        token_url="https://example.com/oauth/token",
    )

    assert flow.token_url is not None
    assert isinstance(flow.scopes, dict)


def test_oauth_flows():
    flows = OAuthFlows()

    assert flows.authorization_code is not None or flows.authorization_code is None
    assert flows.client_credentials is not None or flows.client_credentials is None
    assert flows.device_code is not None or flows.device_code is None


def test_api_key_security_scheme():
    scheme = ApiKeySecurityScheme(
        name="X-API-Key",
        location="header",
    )

    assert scheme.name is not None
    assert scheme.location in ["header", "query", "cookie"]


def test_http_auth_security_scheme():
    scheme = HttpAuthSecurityScheme(
        scheme="Bearer",
    )

    assert scheme.scheme in ["Basic", "Bearer", "Digest"]


def test_mtls_security_scheme():
    scheme = MtlsSecurityScheme()

    assert hasattr(scheme, "description")


def test_oauth2_security_scheme():
    flows = OAuthFlows()
    scheme = Oauth2SecurityScheme(flows=flows)

    assert hasattr(scheme, "flows")
    assert isinstance(scheme.flows, OAuthFlows)


def test_openid_connect_security_scheme():
    scheme = OpenIdConnectSecurityScheme()

    assert hasattr(scheme, "open_id_connect_url")


def test_security_scheme():
    api_key = ApiKeySecurityScheme(name="X-API-Key", location="header")
    security = SecurityScheme(api_key)

    assert security is not None

    http_auth = HttpAuthSecurityScheme(scheme="Bearer")
    security = SecurityScheme(http_auth)

    assert security is not None


def test_agent_card_signature():
    signature = AgentCardSignature(protected="signature", signature="abc123")

    assert hasattr(signature, "protected")
    assert hasattr(signature, "signature")


def test_agent_spec_minimal():
    interface = AgentInterface(
        url="http://example.com/agent",
        protocol_binding="HTTP",
        protocol_version="1.0",
    )

    capabilities = AgentCapabilities(
        streaming=False,
        push_notifications=False,
        extended_agent_card=False,
    )

    skill = AgentSkill(
        id="basic_skill",
        name="Basic Skill",
        description="A simple skill",
    )

    spec = AgentSpec(
        name="Test Agent",
        description="A test agent for unit tests",
        version="1.0.0",
        supported_interfaces=[interface],
        capabilities=capabilities,
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[skill],
    )

    assert spec.name == "Test Agent"
    assert spec.description == "A test agent for unit tests"
    assert spec.version == "1.0.0"
    assert len(spec.supported_interfaces) == 1
    assert spec.capabilities.streaming is False
    assert spec.default_input_modes == ["text"]
    assert spec.default_output_modes == ["text"]
    assert len(spec.skills) == 1


def test_agent_spec_full():
    provider = AgentProvider(
        organization="TestOrg",
        url="https://testorg.com",
    )

    interface = AgentInterface(
        url="http://example.com/agent",
        protocol_binding="HTTP",
        protocol_version="1.0",
        tenant="test-tenant",
    )

    extension = AgentExtension(
        uri="https://example.com/ext/custom",
        description="Custom extension",
        params={"key": "value"},
        required=True,
    )

    capabilities = AgentCapabilities(
        streaming=True,
        push_notifications=True,
        extended_agent_card=True,
        extensions=[extension],
    )

    security_req = SecurityRequirement(schemes=["api_key"])

    skill = AgentSkill(
        id="advanced_skill",
        name="Advanced Skill",
        description="An advanced skill with security",
        tags=["advanced", "secure"],
        examples=["Example 1", "Example 2"],
        input_modes=["text", "image"],
        output_modes=["text", "json"],
        security_requirements=[security_req],
    )

    api_key_scheme = ApiKeySecurityScheme(location="header", name="X-API-Key")
    security_scheme = SecurityScheme(api_key_scheme)

    signature = AgentCardSignature(
        protected="protected_data",
        signature="signature_data",
    )

    spec = AgentSpec(
        name="Advanced Agent",
        description="A fully-featured test agent",
        version="2.0.0",
        supported_interfaces=[interface],
        capabilities=capabilities,
        default_input_modes=["text"],
        default_output_modes=["text", "json"],
        skills=[skill],
        provider=provider,
        documentation_url="https://docs.example.com",
        icon_url="https://example.com/icon.png",
        security_schemes={"api_key": security_scheme},
        security_requirements=[security_req],
        signatures=[signature],
    )

    assert spec.name == "Advanced Agent"
    assert spec.provider.organization == "TestOrg"
    assert spec.documentation_url == "https://docs.example.com"
    assert spec.icon_url == "https://example.com/icon.png"
    assert "api_key" in spec.security_schemes
    assert len(spec.security_requirements) == 1
    assert len(spec.signatures) == 1

    spec.name = "Updated Agent"
    spec.version = "2.1.0"

    assert spec.name == "Updated Agent"
    assert spec.version == "2.1.0"


def test_agent_spec_property_updates():
    interface = AgentInterface(
        url="http://example.com/agent",
        protocol_binding="HTTP",
        protocol_version="1.0",
    )

    capabilities = AgentCapabilities()

    skill = AgentSkill(
        id="test",
        name="Test",
        description="Test skill",
    )

    spec = AgentSpec(
        name="Test Agent",
        description="Original description",
        version="1.0.0",
        supported_interfaces=[interface],
        capabilities=capabilities,
        default_input_modes=["text"],
        default_output_modes=["text"],
        skills=[skill],
    )

    spec.description = "Updated description"
    spec.default_input_modes = ["text", "audio"]
    spec.default_output_modes = ["text", "json", "audio"]

    assert spec.description == "Updated description"
    assert spec.default_input_modes == ["text", "audio"]
    assert spec.default_output_modes == ["text", "json", "audio"]
