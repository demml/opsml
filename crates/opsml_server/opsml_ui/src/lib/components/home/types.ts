type BaseCard = {
  uid: string;
  created_at: string;
  app_env: string;
  name: string;
  repository: string;
  version: string;
  tags: string[];
  username: string;
};

interface DataCard extends BaseCard {
  type: "Data";
  data: {
    data_type: string;
    interface_type: string;
    experimentcard_uid?: string;
    auditcard_uid?: string;
  };
}

interface ModelCard extends BaseCard {
  type: "Model";
  data: {
    data_type: string;
    model_type: string;
    task_type: string;
    interface_type: string;
    datacard_uid?: string;
    experimentcard_uid?: string;
    auditcard_uid?: string;
  };
}

interface ExperimentCard extends BaseCard {
  type: "Experiment";
  data: {
    datacard_uids: string[];
    modelcard_uids: string[];
    promptcard_uids: string[];
    experimentcard_uids: string[];
  };
}

interface AuditCard extends BaseCard {
  type: "Audit";
  data: {
    approved: boolean;
    datacard_uids: string[];
    modelcard_uids: string[];
    experimentcard_uids: string[];
  };
}

interface PromptCard extends BaseCard {
  type: "Prompt";
  data: {
    prompt_type: string;
    experimentcard_uid?: string;
    auditcard_uid?: string;
  };
}

export type Card =
  | DataCard
  | ModelCard
  | ExperimentCard
  | AuditCard
  | PromptCard;

export interface CardQueryArgs {
  registry_type: string;
  limit?: number;
  sort_by_timestamp?: boolean;
}
