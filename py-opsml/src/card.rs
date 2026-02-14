use opsml_cards::{
    DataCard, DataCardMetadata, ExperimentCard, ModelCard, ModelCardMetadata, PromptCard,
    ServiceCard, UidMetadata,
};

use opsml_registry::{CardRegistries, CardRegistry};
use opsml_types::contracts::{Card, CardList, CardRecord};
use opsml_types::{cards::ComputeEnvironment, RegistryMode, RegistryType};
use pyo3::prelude::*;

use opsml_types::contracts::agent::{
    AgentCapabilities, AgentCardSignature, AgentExtension, AgentInterface, AgentProvider,
    AgentSkill, AgentSpec, ApiKeySecurityScheme, AuthorizationCodeFlow, ClientCredentialsFlow,
    DeviceCodeFlow, HttpAuthSecurityScheme, ImplicitAuthFlow, MtlsSecurityScheme, OAuthFlows,
    Oauth2SecurityScheme, OpenIdConnectSecurityScheme, PassWordAuthFlow, SecurityRequirement,
    SecurityScheme,
};

pub fn add_card_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CardRecord>()?;
    m.add_class::<CardList>()?;
    m.add_class::<DataCard>()?;
    m.add_class::<DataCardMetadata>()?;

    // opsml_registry
    m.add_class::<CardRegistry>()?;
    m.add_class::<CardRegistries>()?;
    m.add_class::<RegistryType>()?;
    m.add_class::<RegistryMode>()?;

    // ModelCard
    m.add_class::<ModelCard>()?;
    m.add_class::<ModelCardMetadata>()?;
    // experimentcard
    m.add_class::<ExperimentCard>()?;
    m.add_class::<ComputeEnvironment>()?;
    m.add_class::<UidMetadata>()?;
    // promptcard
    m.add_class::<PromptCard>()?;
    // ServiceCard
    m.add_class::<ServiceCard>()?;
    m.add_class::<Card>()?;

    // AgentCard
    m.add_class::<AgentSpec>()?;
    m.add_class::<AgentInterface>()?;
    m.add_class::<AgentSkill>()?;
    m.add_class::<AgentExtension>()?;
    m.add_class::<AgentProvider>()?;
    m.add_class::<AgentCapabilities>()?;
    m.add_class::<AgentCardSignature>()?;
    // Security Schemes
    m.add_class::<SecurityScheme>()?;
    m.add_class::<SecurityRequirement>()?;
    m.add_class::<OAuthFlows>()?;
    m.add_class::<ApiKeySecurityScheme>()?;
    m.add_class::<HttpAuthSecurityScheme>()?;
    m.add_class::<MtlsSecurityScheme>()?;
    m.add_class::<Oauth2SecurityScheme>()?;
    m.add_class::<AuthorizationCodeFlow>()?;
    m.add_class::<ClientCredentialsFlow>()?;
    m.add_class::<DeviceCodeFlow>()?;
    m.add_class::<ImplicitAuthFlow>()?;
    m.add_class::<PassWordAuthFlow>()?;
    m.add_class::<OpenIdConnectSecurityScheme>()?;

    Ok(())
}
