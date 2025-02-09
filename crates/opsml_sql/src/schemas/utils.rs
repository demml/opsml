use crate::schemas::schema::{
    AuditCardRecord, DataCardRecord, ModelCardRecord, PipelineCardRecord, ProjectCardRecord,
    RunCardRecord,
};

use opsml_types::contracts::{
    AuditCardClientRecord, Card, DataCardClientRecord, ModelCardClientRecord,
    PipelineCardClientRecord, ProjectCardClientRecord, RunCardClientRecord,
};

pub fn convert_datacard(record: DataCardRecord) -> Card {
    let card = DataCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: Some(record.app_env),
        name: record.name,
        repository: record.repository,
        version: record.version,
        contact: record.contact,
        tags: record.tags.0, // Assuming Json<HashMap<String, String>> is used
        data_type: record.data_type,
        runcard_uid: Some(record.runcard_uid),
        pipelinecard_uid: Some(record.pipelinecard_uid),
        auditcard_uid: Some(record.auditcard_uid),
        interface_type: record.interface_type,
        checksums: record.checksums.0,
    };

    Card::Data(card)
}

pub fn convert_modelcard(record: ModelCardRecord) -> Card {
    let card = ModelCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: Some(record.app_env),
        name: record.name,
        repository: record.repository,
        version: record.version,
        contact: record.contact,
        tags: record.tags.0,
        datacard_uid: Some(record.datacard_uid),
        data_type: record.data_type,
        model_type: record.model_type,
        runcard_uid: Some(record.runcard_uid),
        pipelinecard_uid: Some(record.pipelinecard_uid),
        auditcard_uid: Some(record.auditcard_uid),
        interface_type: record.interface_type,
        task_type: record.task_type,
        checksums: record.checksums.0,
    };

    Card::Model(card)
}

pub fn convert_runcard(record: RunCardRecord) -> Card {
    let card = RunCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: Some(record.app_env),
        name: record.name,
        repository: record.repository,
        version: record.version,
        contact: record.contact,
        tags: record.tags.0,
        datacard_uids: Some(record.datacard_uids.0),
        modelcard_uids: Some(record.modelcard_uids.0),
        pipelinecard_uid: Some(record.pipelinecard_uid),
        project: record.project,
        artifact_uris: Some(record.artifact_uris.0),
        compute_environment: Some(record.compute_environment.0),
        checksums: record.checksums.0,
    };

    Card::Run(card)
}

pub fn convert_auditcard(record: AuditCardRecord) -> Card {
    let card = AuditCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: Some(record.app_env),
        name: record.name,
        repository: record.repository,
        version: record.version,
        contact: record.contact,
        tags: record.tags.0,
        approved: record.approved,
        datacard_uids: Some(record.datacard_uids.0),
        modelcard_uids: Some(record.modelcard_uids.0),
        runcard_uids: Some(record.runcard_uids.0),
    };

    Card::Audit(card)
}

pub fn convert_pipelinecard(record: PipelineCardRecord) -> Card {
    let card = PipelineCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        app_env: Some(record.app_env),
        name: record.name,
        repository: record.repository,
        version: record.version,
        contact: record.contact,
        tags: record.tags.0,
        pipeline_code_uri: record.pipeline_code_uri,
        datacard_uids: Some(record.datacard_uids.0),
        modelcard_uids: Some(record.modelcard_uids.0),
        runcard_uids: Some(record.runcard_uids.0),
    };

    Card::Pipeline(card)
}

pub fn convert_projectcard(record: ProjectCardRecord) -> Card {
    let card = ProjectCardClientRecord {
        uid: record.uid,
        created_at: record.created_at,
        name: record.name,
        repository: record.repository,
        version: record.version,
        project_id: record.project_id,
    };

    Card::Project(card)
}
