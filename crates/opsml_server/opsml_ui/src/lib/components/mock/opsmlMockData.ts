import { Provider, ResponseType, type Prompt } from "$lib/components/agent/types";
import type { MessageNum } from "$lib/components/agent/provider/types";
import type { AgentSpec } from "$lib/components/card/agent/types";
import type {
  DataCard,
  DataCardMetadata,
  DataInterfaceMetadata,
  DataInterfaceSaveMetadata,
  FeatureSchema,
} from "$lib/components/card/card_interfaces/datacard";
import {
  DataInterfaceType,
  DataType as DataCardType,
} from "$lib/components/card/card_interfaces/datacard";
import type {
  ExperimentCard,
  Metric,
  Parameter,
} from "$lib/components/card/card_interfaces/experimentcard";
import type { ModelCard } from "$lib/components/card/card_interfaces/modelcard";
import {
  DataType as ModelDataType,
  ModelInterfaceType,
  ModelType,
  ProcessorType,
  TaskType,
  type DataProcessor,
  type ModelInterfaceMetadata,
  type ModelInterfaceSaveMetadata,
} from "$lib/components/card/card_interfaces/modelcard";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type {
  Card as LinkedCard,
  CardList,
  DeploymentConfig,
  ServiceCard,
  ServiceConfig,
  ServiceMetadata,
} from "$lib/components/card/card_interfaces/servicecard";
import {
  McpCapability,
  McpTransport,
  ServiceType,
} from "$lib/components/card/card_interfaces/servicecard";
import type {
  Experiment,
  GroupedMetrics,
  UiHardwareMetrics,
} from "$lib/components/card/experiment/types";
import type { DataProfile } from "$lib/components/card/data/types";
import type {
  CardSummary,
  RegistryPageReturn,
  RegistryStatsResponse,
  VersionPageResponse,
} from "$lib/components/card/types";
import type { FileTreeResponse, RawFile } from "$lib/components/files/types";
import type { Card as HomeCard } from "$lib/components/home/types";
import type {
  HomePageStats,
  RecentCards,
} from "$lib/components/home/utils.server";
import type { ReadMe } from "$lib/components/readme/util";
import type { SpaceRecord, SpaceStatsResponse } from "$lib/components/space/types";
import type { CardLayoutData, CardMetadata } from "$lib/server/card/layout";
import { RegistryType } from "$lib/utils";
import { buildMockAgentEvalProfile } from "$lib/components/scouter/evaluation/mockData";

const ONE_BY_ONE_PNG =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9p0SUs8AAAAASUVORK5CYII=";

function iso(minutesAgo: number): string {
  return new Date(Date.now() - minutesAgo * 60_000).toISOString();
}

function mockUid(prefix: string, space: string, name: string): string {
  return `${prefix}_${space.replace(/[^a-z0-9]/gi, "_")}_${name.replace(/[^a-z0-9]/gi, "_")}`;
}

function buildFeatureSchema(): FeatureSchema {
  return {
    items: {
      transaction_amount: {
        feature_type: "Float32",
        shape: [1],
        extra_args: {},
      },
      customer_region: {
        feature_type: "Utf8",
        shape: [1],
        extra_args: {},
      },
      risk_score: {
        feature_type: "Float32",
        shape: [1],
        extra_args: {},
      },
    },
  };
}

function buildMockPrompt(name: string): Prompt {
  const messages: MessageNum[] = [
    {
      role: "developer",
      content: `You are the ${name} prompt. Return concise structured analysis.`,
    },
    {
      role: "user",
      content:
        "Analyze the customer interaction and summarize the next best action.",
    },
  ];

  return {
    provider: Provider.OpenAI,
    model: "gpt-4o",
    version: "1.0.0",
    parameters: ["customer_profile", "transaction_history"],
    response_type: ResponseType.Pydantic,
    request: {
      model: "gpt-4o",
      messages,
    },
  };
}

function buildMockAgentSpec(name: string): AgentSpec {
  return {
    capabilities: {
      streaming: true,
      pushNotifications: false,
      extendedAgentCard: true,
      extensions: [],
    },
    defaultOutputModes: ["text/plain"],
    defaultInputModes: ["text/plain"],
    description: `${name} coordinates tool calls and produces structured responses for demo workflows.`,
    documentationUrl: "https://docs.demml.io/opsml/",
    name,
    skills: [
      {
        format: "standard",
        name: "triage_support_case",
        description: "Classify support requests and decide the next tool to call.",
        body: "Use support context, then return the next best action.",
        allowedTools: ["lookup_customer", "search_kb"],
      },
    ],
    supportedInterfaces: [
      {
        url: "http://localhost:8080/a2a",
        protocolBinding: "http",
        protocolVersion: "1.0",
        tenant: "local-dev",
      },
    ],
    version: "1.0.0",
  };
}

function buildLinkedCards(space: string): CardList {
  return {
    cards: [
      {
        name: "customer-events",
        space,
        version: "0.3.0",
        uid: mockUid("data", space, "customer-events"),
        registry_type: "data",
        alias: "Input Data",
      },
      {
        name: "fraud-detector",
        space,
        version: "1.4.2",
        uid: mockUid("model", space, "fraud-detector"),
        registry_type: "model",
        alias: "Primary Model",
      },
      {
        name: "support-classifier",
        space,
        version: "0.9.1",
        uid: mockUid("prompt", space, "support-classifier"),
        registry_type: "prompt",
        alias: "Prompt Template",
      },
    ],
  };
}

function buildServiceMetadata(): ServiceMetadata {
  return {
    description: "Mock service configuration for local UI development.",
    language: "python",
    tags: ["mock", "demo", "development"],
  };
}

function buildDeployConfig(name: string): DeploymentConfig[] {
  return [
    {
      environment: "development",
      provider: "local",
      location: ["localhost"],
      urls: [`http://localhost:8080/${name}`],
      resources: {
        cpu: 2,
        memory: "4Gi",
        storage: "20Gi",
      },
      healthcheck: "/health",
    },
  ];
}

function buildHomeCardBase(
  type: HomeCard["type"],
  space: string,
  name: string,
  version: string,
  createdAt: string,
) {
  return {
    uid: mockUid(type.toLowerCase(), space, name),
    created_at: createdAt,
    app_env: "development",
    name,
    space,
    version,
    tags: ["mock", "demo"],
    username: "demo_user",
  };
}

function buildMockDataCardSummary(space: string, createdAt: string): HomeCard {
  const base = buildHomeCardBase(
    "Data",
    space,
    "customer-events",
    "0.3.0",
    createdAt,
  );

  return {
    ...base,
    type: "Data",
    data: {
      ...base,
      data_type: "Pandas",
      interface_type: "Pandas",
    },
  };
}

function buildMockModelCardSummary(space: string, createdAt: string): HomeCard {
  const base = buildHomeCardBase(
    "Model",
    space,
    "fraud-detector",
    "1.4.2",
    createdAt,
  );

  return {
    ...base,
    type: "Model",
    data: {
      ...base,
      data_type: "Pandas",
      model_type: "XGBClassifier",
      task_type: "Classification",
      interface_type: "XGBoost",
    },
  };
}

function buildMockExperimentCardSummary(
  space: string,
  createdAt: string,
): HomeCard {
  const base = buildHomeCardBase(
    "Experiment",
    space,
    "fraud-baseline",
    "2.0.0",
    createdAt,
  );

  return {
    ...base,
    type: "Experiment",
    data: {
      ...base,
      datacard_uids: [mockUid("data", space, "customer-events")],
      modelcard_uids: [mockUid("model", space, "fraud-detector")],
      promptcard_uids: [mockUid("prompt", space, "support-classifier")],
      experimentcard_uids: [],
    },
  };
}

function buildMockPromptCardSummary(space: string, createdAt: string): HomeCard {
  const base = buildHomeCardBase(
    "Prompt",
    space,
    "support-classifier",
    "0.9.1",
    createdAt,
  );

  return {
    ...base,
    type: "Prompt",
    data: {
      ...base,
      experimentcard_uid: mockUid("experiment", space, "fraud-baseline"),
    },
  };
}

export function buildMockRecentCards(space = "fraud-detection"): RecentCards {
  return {
    modelcards: [buildMockModelCardSummary(space, iso(18))],
    datacards: [buildMockDataCardSummary(space, iso(27))],
    experimentcards: [buildMockExperimentCardSummary(space, iso(36))],
    promptcards: [buildMockPromptCardSummary(space, iso(44))],
  };
}

export function mergeRecentCardsWithMock(
  cards: RecentCards,
  space = "fraud-detection",
): RecentCards {
  const mockCards = buildMockRecentCards(space);

  return {
    modelcards: cards.modelcards.length > 0 ? cards.modelcards : mockCards.modelcards,
    datacards: cards.datacards.length > 0 ? cards.datacards : mockCards.datacards,
    experimentcards:
      cards.experimentcards.length > 0
        ? cards.experimentcards
        : mockCards.experimentcards,
    promptcards: cards.promptcards.length > 0 ? cards.promptcards : mockCards.promptcards,
  };
}

export function isRecentCardsEmpty(cards: RecentCards): boolean {
  return (
    cards.modelcards.length === 0 &&
    cards.datacards.length === 0 &&
    cards.experimentcards.length === 0 &&
    cards.promptcards.length === 0
  );
}

export function buildMockHomeData(): {
  cards: RecentCards;
  stats: HomePageStats;
} {
  return {
    cards: buildMockRecentCards(),
    stats: {
      nbrModels: 12,
      nbrData: 8,
      nbrPrompts: 6,
      nbrExperiments: 15,
    },
  };
}

export function buildMockSpaceStats(): SpaceStatsResponse {
  return {
    stats: [
      {
        space: "fraud-detection",
        model_count: 4,
        data_count: 3,
        prompt_count: 2,
        experiment_count: 5,
      },
      {
        space: "support-ops",
        model_count: 2,
        data_count: 1,
        prompt_count: 4,
        experiment_count: 3,
      },
      {
        space: "growth-analytics",
        model_count: 3,
        data_count: 2,
        prompt_count: 1,
        experiment_count: 4,
      },
    ],
  };
}

export function buildMockSpaceRecord(space: string): SpaceRecord {
  return {
    space,
    description: `Mock space record for ${space}.`,
  };
}

function buildMockCardSummaries(
  registryType: RegistryType,
  spaceFilter?: string,
  nameFilter?: string,
): CardSummary[] {
  const space = spaceFilter ?? "fraud-detection";
  const items: CardSummary[] = [
    {
      uid: mockUid(registryType, space, "primary"),
      space,
      name:
        nameFilter ??
        ({
          [RegistryType.Model]: "fraud-detector",
          [RegistryType.Data]: "customer-events",
          [RegistryType.Experiment]: "fraud-baseline",
          [RegistryType.Service]: "fraud-api",
          [RegistryType.Prompt]: "support-classifier",
          [RegistryType.Agent]: "triage-agent",
          [RegistryType.Mcp]: "knowledge-mcp",
        }[registryType] ?? "mock-card"),
      version: "1.0.0",
      versions: 3,
      updated_at: iso(12),
      created_at: iso(120),
      status: "Ok",
    },
    {
      uid: mockUid(registryType, space, "candidate"),
      space,
      name:
        ({
          [RegistryType.Model]: "churn-predictor",
          [RegistryType.Data]: "application-features",
          [RegistryType.Experiment]: "ablation-run",
          [RegistryType.Service]: "churn-api",
          [RegistryType.Prompt]: "renewal-assistant",
          [RegistryType.Agent]: "support-router",
          [RegistryType.Mcp]: "filesystem-mcp",
        }[registryType] ?? "mock-secondary"),
      version: "0.9.0",
      versions: 2,
      updated_at: iso(36),
      created_at: iso(240),
      status: "Active",
    },
  ];

  const search = nameFilter?.toLowerCase();
  return items.filter((item) => {
    const matchesSpace = !spaceFilter || item.space === spaceFilter;
    const matchesName = !search || item.name.toLowerCase().includes(search);
    return matchesSpace && matchesName;
  });
}

export function buildMockRegistryPageData(
  registryType: RegistryType,
  space?: string,
  name?: string,
): RegistryPageReturn {
  const items = buildMockCardSummaries(registryType, space, name);

  return {
    spaces: buildMockSpaceStats().stats.map((record) => record.space),
    tags: ["mock", "demo", "baseline", registryType],
    registry_type: registryType,
    registryStats: {
      stats: {
        nbr_names: items.length,
        nbr_spaces: space ? 1 : 3,
        nbr_versions: items.reduce((sum, item) => sum + item.versions, 0),
      },
    },
    registryPage: {
      items,
      has_next: false,
      has_previous: false,
      page_info: {
        page_size: items.length,
        offset: 0,
        filters: {
          search_term: name,
          spaces: space ? [space] : undefined,
        },
      },
    },
  };
}

export function isRegistryPageEmpty(page: RegistryPageReturn): boolean {
  return page.registryPage.items.length === 0;
}

export function buildMockVersionPage(
  space: string,
  name: string,
): VersionPageResponse {
  return {
    items: [
      { space, name, version: "1.0.0", created_at: iso(45), row_num: 1 },
      { space, name, version: "0.9.0", created_at: iso(240), row_num: 2 },
      { space, name, version: "0.8.0", created_at: iso(720), row_num: 3 },
    ],
    has_next: false,
    has_previous: false,
  };
}

export function buildMockVersionStats(): RegistryStatsResponse {
  return {
    stats: {
      nbr_names: 1,
      nbr_spaces: 1,
      nbr_versions: 3,
    },
  };
}

function buildMockDataCard(
  space: string,
  name: string,
  version: string,
): DataCard {
  const saveMetadata: DataInterfaceSaveMetadata = {
    data_uri: `mock://${space}/${name}/${version}/data.parquet`,
    data_profile_uri: `mock://${space}/${name}/${version}/profile.json`,
  };

  const interfaceMetadata: DataInterfaceMetadata = {
    save_metadata: saveMetadata,
    schema: buildFeatureSchema(),
    extra_metadata: {},
    sql_logic: { queries: {} },
    interface_type: DataInterfaceType.Pandas,
    data_splits: { splits: [] },
    dependent_vars: {
      column_names: ["fraud_label"],
      column_indices: [0],
      is_idx: false,
    },
    data_type: DataCardType.Pandas,
    data_specific_metadata: {
      rows: 250000,
      columns: 18,
    },
  };

  const metadata: DataCardMetadata = {
    schema: interfaceMetadata.schema,
    experimentcard_uid: mockUid("experiment", space, "fraud-baseline"),
    interface_metadata: interfaceMetadata,
  };

  return {
    name,
    space,
    version,
    uid: mockUid("data", space, name),
    tags: ["mock", "tabular", "development"],
    metadata,
    registry_type: RegistryType.Data,
    app_env: "development",
    created_at: iso(90),
    is_card: true,
    opsml_version: "1.0.0",
  };
}

function buildMockModelCard(
  space: string,
  name: string,
  version: string,
): ModelCard {
  const dataProcessorMap: Record<string, DataProcessor> = {
    normalize: {
      name: "normalize",
      uri: `mock://${space}/${name}/normalize.pkl`,
      type: ProcessorType.Preprocessor,
    },
  };

  const saveMetadata: ModelInterfaceSaveMetadata = {
    model_uri: `mock://${space}/${name}/${version}/model.bin`,
    data_processor_map: dataProcessorMap,
    extra: { artifact_backend: "mock" },
  };

  const interfaceMetadata: ModelInterfaceMetadata = {
    task_type: TaskType.Classification,
    model_type: ModelType.XgbClassifier,
    data_type: ModelDataType.Pandas,
    schema: buildFeatureSchema(),
    save_metadata: saveMetadata,
    extra_metadata: {},
    interface_type: ModelInterfaceType.XGBoost,
    model_specific_metadata: {
      feature_count: 18,
      class_labels: ["legit", "fraud"],
    },
  };

  return {
    name,
    space,
    version,
    uid: mockUid("model", space, name),
    tags: ["mock", "classification", "development"],
    metadata: {
      datacard_uid: mockUid("data", space, "customer-events"),
      experimentcard_uid: mockUid("experiment", space, "fraud-baseline"),
      interface_metadata: interfaceMetadata,
    },
    registry_type: RegistryType.Model,
    app_env: "development",
    created_at: iso(110),
    is_card: true,
    opsml_version: "1.0.0",
  };
}

function buildMockExperimentCard(
  space: string,
  name: string,
  version: string,
): ExperimentCard {
  return {
    space,
    name,
    version,
    uid: mockUid("experiment", space, name),
    tags: ["mock", "baseline", "training"],
    uids: {
      datacard_uids: [mockUid("data", space, "customer-events")],
      modelcard_uids: [mockUid("model", space, "fraud-detector")],
      promptcard_uids: [mockUid("prompt", space, "support-classifier")],
      experimentcard_uids: [],
    },
    compute_environment: {
      cpu_count: 8,
      total_memory: 32 * 1024 * 1024 * 1024,
      total_swap: 8 * 1024 * 1024 * 1024,
      system: "Darwin",
      os_version: "14.4",
      hostname: "devbox.local",
      python_version: "3.11.8",
    },
    registry_type: RegistryType.Experiment,
    app_env: "development",
    created_at: iso(150),
    subexperiment: false,
    is_card: true,
    opsml_version: "1.0.0",
  };
}

function buildMockPromptCard(
  space: string,
  name: string,
  version: string,
): PromptCard {
  return {
    prompt: buildMockPrompt(name),
    name,
    space,
    version,
    uid: mockUid("prompt", space, name),
    tags: ["mock", "agent", "development"],
    metadata: {
      experimentcard_uid: mockUid("experiment", space, "fraud-baseline"),
    },
    registry_type: RegistryType.Prompt,
    app_env: "development",
    created_at: iso(70),
    is_card: true,
    opsml_version: "1.0.0",
    eval_profile: buildMockAgentEvalProfile(),
  };
}

function buildMockServiceCard(
  registryType: RegistryType.Service | RegistryType.Mcp | RegistryType.Agent,
  space: string,
  name: string,
  version: string,
): ServiceCard {
  const cards = buildLinkedCards(space);
  const metadata = buildServiceMetadata();
  const serviceConfig: ServiceConfig = {
    version,
    cards: cards.cards,
    write_dir: "/tmp/opsml-mock",
  };

  if (registryType === RegistryType.Agent) {
    serviceConfig.agent = buildMockAgentSpec(name);
  }

  if (registryType === RegistryType.Mcp) {
    serviceConfig.mcp = {
      capabilities: [McpCapability.Tools, McpCapability.Resources],
      transport: McpTransport.Http,
    };
  }

  return {
    name,
    space,
    version,
    uid: mockUid(registryType, space, name),
    created_at: iso(55),
    cards,
    opsml_version: "1.0.0",
    app_env: "development",
    is_card: true,
    registry_type: registryType,
    experimentcard_uid: mockUid("experiment", space, "fraud-baseline"),
    service_type:
      registryType === RegistryType.Agent
        ? ServiceType.Agent
        : registryType === RegistryType.Mcp
          ? ServiceType.Mcp
          : ServiceType.Api,
    metadata,
    deploy: buildDeployConfig(name),
    service_config: serviceConfig,
    tags: metadata.tags,
  };
}

export function buildMockAgentPromptCards(
  space: string,
  cards: LinkedCard[] = buildLinkedCards(space).cards,
): PromptCard[] {
  const promptCards = cards
    .filter((card) => card.registry_type.toLowerCase() === "prompt")
    .map((card) =>
      buildMockPromptCard(card.space, card.name, card.version),
    );

  if (promptCards.length > 0) {
    return promptCards;
  }

  return [buildMockPromptCard(space, "mock-intent-classifier", "1.0.0")];
}

export function buildMockCardMetadata(
  registryType: RegistryType,
  space: string,
  name: string,
  version: string,
): CardMetadata {
  switch (registryType) {
    case RegistryType.Data:
      return buildMockDataCard(space, name, version);
    case RegistryType.Model:
      return buildMockModelCard(space, name, version);
    case RegistryType.Experiment:
      return buildMockExperimentCard(space, name, version);
    case RegistryType.Prompt:
      return buildMockPromptCard(space, name, version);
    case RegistryType.Mcp:
      return buildMockServiceCard(RegistryType.Mcp, space, name, version);
    case RegistryType.Agent:
      return buildMockServiceCard(RegistryType.Agent, space, name, version);
    case RegistryType.Service:
    default:
      return buildMockServiceCard(RegistryType.Service, space, name, version);
  }
}

export function buildMockReadme(
  registryType: RegistryType,
  name: string,
): ReadMe {
  return {
    exists: true,
    readme: `# ${name}\n\nThis is mock ${registryType} content rendered in local development.\n\n- Uses realistic placeholder metadata\n- Lets you inspect layouts without saved backend state\n- Should disappear when real data is available`,
  };
}

export function buildMockCardLayout(
  registryType: RegistryType,
  space: string,
  name: string,
  version: string,
): CardLayoutData {
  return {
    metadata: buildMockCardMetadata(registryType, space, name, version),
    registryType,
    readme: buildMockReadme(registryType, name),
    activeTab: "card",
  };
}

export function buildMockFileTree(basePath: string): FileTreeResponse {
  return {
    files: [
      {
        name: "README.md",
        created_at: iso(30),
        object_type: "file",
        size: 1024,
        path: `${basePath}/README.md`,
        suffix: "md",
      },
      {
        name: "schema.json",
        created_at: iso(40),
        object_type: "file",
        size: 768,
        path: `${basePath}/schema.json`,
        suffix: "json",
      },
      {
        name: "pipeline.py",
        created_at: iso(50),
        object_type: "file",
        size: 512,
        path: `${basePath}/pipeline.py`,
        suffix: "py",
      },
    ],
  };
}

export function buildMockRawFile(path: string): RawFile {
  if (path.endsWith(".json")) {
    return {
      content: JSON.stringify(
        { source: "mock", path, generated_at: new Date().toISOString() },
        null,
        2,
      ),
      suffix: "json",
      mime_type: "application/json",
    };
  }

  if (path.endsWith(".py")) {
    return {
      content: `def run_pipeline():\n    return {"status": "mock", "path": "${path}"}\n`,
      suffix: "py",
      mime_type: "text/x-python",
    };
  }

  return {
    content: `# Mock file\n\nViewing \`${path}\` in local mock mode.\n`,
    suffix: "md",
    mime_type: "text/markdown",
  };
}

export function buildMockDataProfile(): DataProfile {
  return {
    features: {
      transaction_amount: {
        id: "transaction_amount",
        timestamp: iso(15),
        numeric_stats: {
          mean: 124.3,
          stddev: 38.1,
          min: 4.2,
          max: 982.5,
          distinct: { count: 1280, percent: 94.1 },
          quantiles: {
            q25: 81.2,
            q50: 118.5,
            q75: 156.9,
            q99: 410.4,
          },
          histogram: {
            bins: [0, 50, 100, 150, 200, 250],
            bin_counts: [12, 48, 66, 33, 18],
          },
        },
      },
      customer_region: {
        id: "customer_region",
        timestamp: iso(15),
        string_stats: {
          distinct: { count: 4, percent: 100 },
          char_stats: {
            min_length: 2,
            max_length: 14,
            median_length: 6,
            mean_length: 7.5,
          },
          word_stats: {
            words: {
              us: { count: 42, percent: 31.1 },
              eu: { count: 33, percent: 24.4 },
              apac: { count: 29, percent: 21.5 },
            },
          },
        },
      },
    },
  };
}

export function buildMockExperimentMetricsIndex(
  currentVersion: string,
): {
  metricNames: string[];
  recentExperiments: Experiment[];
} {
  return {
    metricNames: ["accuracy", "precision", "recall", "latency_ms"],
    recentExperiments: [
      { uid: "exp_prev_1", version: currentVersion === "1.0.0" ? "0.9.0" : "1.0.0" },
      { uid: "exp_prev_2", version: "0.8.0" },
    ],
  };
}

export function buildMockGroupedMetrics(
  experiments: Experiment[],
  selectedMetrics: string[],
): GroupedMetrics {
  const timestamps = [5, 4, 3, 2, 1].map(
    (hoursAgo) => Date.now() - hoursAgo * 60 * 60 * 1000,
  );
  const steps = [1, 2, 3, 4, 5];

  return Object.fromEntries(
    selectedMetrics.map((metricName, metricIndex) => [
      metricName,
      experiments.map((experiment, experimentIndex) => ({
        uid: experiment.uid,
        version: experiment.version,
        value: steps.map(
          (step) => Number((0.72 + metricIndex * 0.04 + experimentIndex * 0.03 + step * 0.01).toFixed(4)),
        ),
        step: steps,
        timestamp: timestamps,
      })),
    ]),
  );
}

export function buildMockHardwareMetrics(): UiHardwareMetrics {
  const createdAt = [6, 5, 4, 3, 2, 1].map((minutesAgo) => iso(minutesAgo));

  return {
    createdAt,
    cpuUtilization: [42, 55, 61, 58, 49, 53],
    usedPercentMemory: [61, 63, 64, 66, 65, 62],
    networkMbRecv: [12, 16, 14, 18, 11, 13],
    networkMbSent: [8, 9, 11, 10, 7, 8],
  };
}

export function buildMockFigures(): RawFile[] {
  return [
    {
      content: ONE_BY_ONE_PNG,
      suffix: "png",
      mime_type: "image/png",
    },
    {
      content: ONE_BY_ONE_PNG,
      suffix: "png",
      mime_type: "image/png",
    },
  ];
}

export function buildMockParameters(): Parameter[] {
  return [
    { name: "learning_rate", value: { Float: 0.1 } },
    { name: "max_depth", value: { Int: 6 } },
    { name: "objective", value: { Str: "binary:logistic" } },
  ];
}

export function buildMockMetrics(): Metric[] {
  return [
    { name: "accuracy", value: 0.94, step: 1, created_at: iso(45) },
    { name: "precision", value: 0.91, step: 1, created_at: iso(45) },
  ];
}
