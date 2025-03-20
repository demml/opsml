use crate::schemas::schema::{
    AuditCardRecord, DataCardRecord, ExperimentCardRecord, ModelCardRecord, PromptCardRecord,
};

use opsml_types::contracts::{
    AuditCardClientRecord, Card, DataCardClientRecord, ExperimentCardClientRecord,
    ModelCardClientRecord, PromptCardClientRecord,
};

pub fn convert_datacard(record: DataCardRecord) -> Card {
    let card = DataCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        repository: record.repository,
        version: record.version,
        tags: record.tags.0, // Assuming Json<HashMap<String, String>> is used
        data_type: record.data_type,
        experimentcard_uid: record.experimentcard_uid,
        auditcard_uid: record.auditcard_uid,
        interface_type: record.interface_type,
        username: record.username,
    };

    Card::Data(card)
}

pub fn convert_modelcard(record: ModelCardRecord) -> Card {
    let card = ModelCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        repository: record.repository,
        version: record.version,
        tags: record.tags.0,
        datacard_uid: record.datacard_uid,
        data_type: record.data_type,
        model_type: record.model_type,
        experimentcard_uid: record.experimentcard_uid,
        auditcard_uid: record.auditcard_uid,
        interface_type: record.interface_type,
        task_type: record.task_type,
        username: record.username,
    };

    Card::Model(card)
}

pub fn convert_experimentcard(record: ExperimentCardRecord) -> Card {
    let card = ExperimentCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        repository: record.repository,
        version: record.version,
        tags: record.tags.0,
        datacard_uids: record.datacard_uids.0,
        modelcard_uids: record.modelcard_uids.0,
        promptcard_uids: record.promptcard_uids.0,
        experimentcard_uids: record.experimentcard_uids.0,
        username: record.username,
    };

    Card::Experiment(card)
}

pub fn convert_auditcard(record: AuditCardRecord) -> Card {
    let card = AuditCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        repository: record.repository,
        version: record.version,
        tags: record.tags.0,
        approved: record.approved,
        datacard_uids: record.datacard_uids.0,
        modelcard_uids: record.modelcard_uids.0,
        experimentcard_uids: record.experimentcard_uids.0,
        username: record.username,
    };

    Card::Audit(card)
}

pub fn convert_promptcard(record: PromptCardRecord) -> Card {
    let card = PromptCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        repository: record.repository,
        version: record.version,
        tags: record.tags.0,
        username: record.username,
        experimentcard_uid: record.experimentcard_uid,
        auditcard_uid: record.auditcard_uid,
    };

    Card::Prompt(card)
}
