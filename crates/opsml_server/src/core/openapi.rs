use crate::core::capabilities::route::{
    AgenticInfo, AuthInfo, CapabilitiesResponse, DocumentationInfo, FeaturesInfo,
};
use crate::core::docs::route::{
    DocListResponse, DocResponse, DocSummary, SearchResponse, SearchResult,
};
use crate::core::error::OpsmlServerError;
use utoipa::OpenApi;

#[derive(OpenApi)]
#[openapi(
    paths(
        crate::core::docs::route::list_docs,
        crate::core::docs::route::get_doc,
        crate::core::docs::route::search_docs,
        crate::core::docs::route::list_examples,
        crate::core::docs::route::get_example,
        crate::core::capabilities::route::capabilities,
    ),
    components(
        schemas(
            DocListResponse,
            DocSummary,
            DocResponse,
            SearchResponse,
            SearchResult,
            CapabilitiesResponse,
            FeaturesInfo,
            DocumentationInfo,
            AgenticInfo,
            AuthInfo,
            OpsmlServerError,
        )
    ),
    tags(
        (name = "docs", description = "Embedded documentation and Python examples — no auth required"),
        (name = "capabilities", description = "Server capability index and endpoint discovery — no auth required"),
    ),
    info(
        title = "OpsML API",
        version = "1.0.0",
        description = "AI lifecycle platform — cards, experiments, and agentic primitives. \
            All protected endpoints require a Bearer JWT obtained from POST /opsml/api/auth/login. \
            Start with GET /opsml/api/v1/capabilities to discover available endpoints."
    )
)]
pub struct ApiDoc;
