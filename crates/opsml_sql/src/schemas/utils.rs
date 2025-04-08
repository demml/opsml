use crate::schemas::schema::{
    AuditCardRecord, DataCardRecord, ExperimentCardRecord, ModelCardRecord, PromptCardRecord,
};

use opsml_types::contracts::{
    AuditCardClientRecord, CardDeckClientRecord, CardRecord, DataCardClientRecord,
    ExperimentCardClientRecord, ModelCardClientRecord, PromptCardClientRecord,
};

use super::CardDeckRecord;

pub fn convert_datacard(record: DataCardRecord) -> CardRecord {
    let card = DataCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        space: record.space,
        version: record.version,
        tags: record.tags.0, // Assuming Json<HashMap<String, String>> is used
        data_type: record.data_type,
        experimentcard_uid: record.experimentcard_uid,
        auditcard_uid: record.auditcard_uid,
        interface_type: record.interface_type,
        username: record.username,
        opsml_version: record.opsml_version,
    };

    CardRecord::Data(card)
}

pub fn convert_modelcard(record: ModelCardRecord) -> CardRecord {
    let card = ModelCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        space: record.space,
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
        opsml_version: record.opsml_version,
    };

    CardRecord::Model(card)
}

pub fn convert_experimentcard(record: ExperimentCardRecord) -> CardRecord {
    let card = ExperimentCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        space: record.space,
        version: record.version,
        tags: record.tags.0,
        datacard_uids: record.datacard_uids.0,
        modelcard_uids: record.modelcard_uids.0,
        promptcard_uids: record.promptcard_uids.0,
        experimentcard_uids: record.experimentcard_uids.0,
        username: record.username,
        opsml_version: record.opsml_version,
    };

    CardRecord::Experiment(card)
}

pub fn convert_auditcard(record: AuditCardRecord) -> CardRecord {
    let card = AuditCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        space: record.space,
        version: record.version,
        tags: record.tags.0,
        approved: record.approved,
        datacard_uids: record.datacard_uids.0,
        modelcard_uids: record.modelcard_uids.0,
        experimentcard_uids: record.experimentcard_uids.0,
        username: record.username,
        opsml_version: record.opsml_version,
    };

    CardRecord::Audit(card)
}

pub fn convert_promptcard(record: PromptCardRecord) -> CardRecord {
    let card = PromptCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        space: record.space,
        version: record.version,
        tags: record.tags.0,
        username: record.username,
        experimentcard_uid: record.experimentcard_uid,
        auditcard_uid: record.auditcard_uid,
        opsml_version: record.opsml_version,
    };

    CardRecord::Prompt(card)
}

pub fn convert_card_deck(record: CardDeckRecord) -> CardRecord {
    let card = CardDeckClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: record.app_env,
        name: record.name,
        space: record.space,
        version: record.version,
        username: record.username,
        opsml_version: record.opsml_version,
    };

    CardRecord::Deck(card)
}
