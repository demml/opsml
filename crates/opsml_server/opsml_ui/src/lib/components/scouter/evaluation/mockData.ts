/**
 * Mock data for the Agent evaluation dashboard.
 * Used in dev mode when no live Scouter instance is available.
 * Follows the same style as $lib/server/trace/mockData.ts.
 */

import type { RegistryType } from "$lib/utils";
import type { TimeRange } from "$lib/components/trace/types";
import type {
  AgentEvalProfile,
  AgentEvalConfig,
  AgentAlertConfig,
  AssertionTasks,
  EvalRecord,
  EvalRecordPaginationResponse,
  AgentEvalWorkflowPaginationResponse,
} from "$lib/components/scouter/agent/types";
import { Status } from "$lib/components/scouter/agent/types";
import type {
  AgentAssertionTask,
  AssertionTask,
  LLMJudgeTask,
  TraceAssertionTask,
  AgentEvalWorkflowResult,
  ExecutionPlan,
  ExecutionNode,
  EvalTaskResult,
} from "$lib/components/scouter/agent/task";
import type {
  DriftAlertPaginationResponse,
  Alert,
} from "$lib/components/scouter/alert/types";
import { AlertThreshold } from "$lib/components/scouter/types";
import { DriftType, EntityType } from "$lib/components/scouter/types";
import { Provider, ResponseType } from "$lib/components/agent/types";
import type { Prompt } from "$lib/components/agent/types";
import type {
  BinnedMetrics,
  BinnedMetric,
  BinnedMetricStats,
} from "$lib/components/scouter/custom/types";
import type {
  AgentMonitoringPageData,
  SelectedAgentData,
} from "$lib/components/scouter/dashboard/utils";

// ── Helpers ───────────────────────────────────────────────────────────────────

const NOW = Date.now();

function iso(offsetMs: number = 0): string {
  return new Date(NOW + offsetMs).toISOString();
}

/** Generate 30 time-series timestamps spaced 5 minutes apart ending at NOW. */
function buildTimestamps(count: number = 30): string[] {
  return Array.from({ length: count }, (_, i) =>
    new Date(NOW - (count - 1 - i) * 5 * 60_000).toISOString(),
  );
}

function buildStats(base: number, jitter: number): BinnedMetricStats[] {
  return buildTimestamps().map(() => {
    const avg = base + (Math.random() * 2 - 1) * jitter;
    return {
      avg: parseFloat(avg.toFixed(4)),
      lower_bound: parseFloat((avg - jitter * 0.5).toFixed(4)),
      upper_bound: parseFloat((avg + jitter * 0.5).toFixed(4)),
    };
  });
}

function buildBinnedMetric(
  name: string,
  base: number,
  jitter: number,
): BinnedMetric {
  return {
    metric: name,
    created_at: buildTimestamps(),
    stats: buildStats(base, jitter),
  };
}

// ── Task definitions ──────────────────────────────────────────────────────────

const assertionTasks: AssertionTask[] = [
  {
    id: "check_response_format",
    context_path: "response",
    item_context_path: null,
    operator: "IsJson",
    expected_value: true,
    description: "Verify the model response is valid JSON",
    depends_on: [],
    task_type: "Assertion",
    condition: true,
  },
  {
    id: "check_intent_label",
    context_path: "response.intent",
    item_context_path: null,
    operator: "ContainsAny",
    expected_value: ["greeting", "faq", "complaint", "purchase", "support"],
    description: "Intent label must be one of the known categories",
    depends_on: ["check_response_format"],
    task_type: "Assertion",
    condition: true,
  },
  {
    id: "check_confidence_score",
    context_path: "response.confidence",
    item_context_path: null,
    operator: "GreaterThanOrEqual",
    expected_value: 0.6,
    description: "Confidence score must be at least 0.6",
    depends_on: ["check_response_format"],
    task_type: "Assertion",
    condition: true,
  },
];

const mockJudgePrompt: Prompt = {
  provider: Provider.OpenAI,
  model: "gpt-4o",
  version: "1.0",
  parameters: [],
  response_type: ResponseType.Score,
  request: {
    model: "gpt-4o",
    messages: [
      {
        role: "developer",
        content:
          "You are an expert LLM judge. Evaluate the quality and relevance of the assistant's response on a scale of 1 to 5, where 1 is very poor and 5 is excellent. Return only the numeric score.",
      } as any,
      {
        role: "user",
        content:
          "Context: {{context}}\n\nAssistant response: {{response.text}}\n\nRate the response quality (1–5):",
      } as any,
    ],
  } as any,
};

const judgeTasks: LLMJudgeTask[] = [
  {
    id: "judge_response_quality",
    prompt: mockJudgePrompt,
    context_path: "response.text",
    expected_value: 3,
    operator: "GreaterThanOrEqual",
    task_type: "LLMJudge",
    depends_on: ["check_response_format"],
    max_retries: 2,
    condition: true,
    description: "LLM judge rates response quality on a 1–5 scale",
  },
];

const traceTasks: TraceAssertionTask[] = [
  {
    id: "check_trace_latency",
    assertion: { TraceDuration: {} },
    operator: "LessThan",
    expected_value: 5000,
    description: "End-to-end trace duration must be under 5 000 ms",
    depends_on: [],
    task_type: "TraceAssertion",
    condition: true,
  },
];

const agentTasks: AgentAssertionTask[] = [
  {
    id: "check_tool_sequence",
    assertion: {
      ToolCallSequence: {
        names: ["classify_intent", "fetch_kb_answer"],
      },
    },
    operator: "Contains",
    expected_value: "fetch_kb_answer",
    description: "Verify the expected tool orchestration occurred",
    depends_on: ["check_response_format"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: null,
  },
];

const assertionTasksObj: AssertionTasks = {
  assertion: assertionTasks,
  judge: judgeTasks,
  trace: traceTasks,
  agent: agentTasks,
};

// ── Eval profile ──────────────────────────────────────────────────────────────

/** Builds a mock Agent evaluation profile (also used by eval layout to inject mock eval_profile) */
export function buildMockAgentEvalProfile(): AgentEvalProfile {
  const alertConfig: AgentAlertConfig = {
    dispatch_config: { Console: { enabled: true } },
    schedule: "0 * * * *",
    alert_condition: {
      alert_threshold: AlertThreshold.Below,
      baseline_value: 0.8,
    },
  };

  const config: AgentEvalConfig = {
    sample_ratio: 1.0,
    space: "mock-space",
    name: "intent-classifier",
    version: "1.0.0",
    uid: "mock-eval-uid-0001",
    alert_config: alertConfig,
    drift_type: DriftType.Agent,
  };

  return {
    config,
    tasks: assertionTasksObj,
    task_ids: [
      "check_response_format",
      "check_intent_label",
      "check_confidence_score",
      "judge_response_quality",
      "check_trace_latency",
      "check_tool_sequence",
    ],
    scouter_version: "0.6.0",
  };
}

// ── Binned metrics ────────────────────────────────────────────────────────────

function buildTaskMetrics(): BinnedMetrics {
  return {
    metrics: {
      pass_rate: buildBinnedMetric("pass_rate", 0.87, 0.06),
      avg_duration_ms: buildBinnedMetric("avg_duration_ms", 320, 40),
      total_evaluations: buildBinnedMetric("total_evaluations", 200, 30),
    },
  };
}

function buildWorkflowMetrics(): BinnedMetrics {
  return {
    metrics: {
      workflow_pass_rate: buildBinnedMetric("workflow_pass_rate", 0.82, 0.08),
      workflow_duration_ms: buildBinnedMetric("workflow_duration_ms", 850, 120),
    },
  };
}

// ── Eval records ──────────────────────────────────────────────────────────────

const RECORD_STATUSES: Status[] = [
  Status.Processed,
  Status.Processed,
  Status.Processed,
  Status.Processed,
  Status.Processed,
  Status.Processed,
  Status.Processed,
  Status.Failed,
  Status.Processing,
  Status.Pending,
];

function buildEvalRecord(index: number): EvalRecord {
  const createdAt = iso(-(index + 1) * 3 * 60_000);
  const status = RECORD_STATUSES[index % RECORD_STATUSES.length];
  const isProcessed = status === Status.Processed || status === Status.Failed;

  return {
    record_id: `rec-${String(index + 1).padStart(4, "0")}`,
    created_at: createdAt,
    uid: "mock-eval-uid-0001",
    context: {
      input: `User query #${index + 1}: What is your return policy for electronics?`,
      response: {
        text: `Our return policy allows returns within 30 days of purchase.`,
        intent:
          index % 3 === 0 ? "faq" : index % 3 === 1 ? "support" : "purchase",
        confidence: parseFloat((0.65 + (index % 5) * 0.07).toFixed(2)),
      },
    },
    id: 1000 + index,
    updated_at: isProcessed ? iso(-(index + 1) * 3 * 60_000 + 2_000) : null,
    processing_started_at: isProcessed
      ? iso(-(index + 1) * 3 * 60_000 + 500)
      : null,
    processing_ended_at: isProcessed
      ? iso(-(index + 1) * 3 * 60_000 + 2_000)
      : null,
    processing_duration: isProcessed ? 1500 + index * 100 : null,
    entity_id: 42,
    entity_uid: "mock-eval-uid-0001",
    status,
    entity_type: EntityType.Agent,
  };
}

function buildEvalRecords(): EvalRecord[] {
  return Array.from({ length: 10 }, (_, i) => buildEvalRecord(i));
}

// ── Workflow results ──────────────────────────────────────────────────────────

function buildExecutionPlan(): ExecutionPlan {
  const nodes: Record<string, ExecutionNode> = {
    check_response_format: {
      id: "check_response_format",
      stage: 0,
      parents: [],
      children: [
        "check_intent_label",
        "check_confidence_score",
        "judge_response_quality",
      ],
    },
    check_intent_label: {
      id: "check_intent_label",
      stage: 1,
      parents: ["check_response_format"],
      children: [],
    },
    check_confidence_score: {
      id: "check_confidence_score",
      stage: 1,
      parents: ["check_response_format"],
      children: [],
    },
    judge_response_quality: {
      id: "judge_response_quality",
      stage: 1,
      parents: ["check_response_format"],
      children: [],
    },
    check_trace_latency: {
      id: "check_trace_latency",
      stage: 2,
      parents: [],
      children: [],
    },
  };

  return {
    stages: [
      ["check_response_format"],
      [
        "check_intent_label",
        "check_confidence_score",
        "judge_response_quality",
      ],
      ["check_trace_latency"],
    ],
    nodes,
  };
}

function buildWorkflowResult(index: number): AgentEvalWorkflowResult {
  const totalTasks = 5;
  const failedVariants = [0, 0, 0, 1, 0, 2, 0, 1];
  const failedTasks = failedVariants[index % failedVariants.length];
  const passedTasks = totalTasks - failedTasks;
  const passRate = parseFloat((passedTasks / totalTasks).toFixed(2));

  return {
    id: 2000 + index,
    record_uid: `rec-${String(index + 1).padStart(4, "0")}`,
    entity_id: 42,
    entity_uid: "mock-eval-uid-0001",
    created_at: iso(-(index + 1) * 3 * 60_000 + 2_000),
    total_tasks: totalTasks,
    passed_tasks: passedTasks,
    failed_tasks: failedTasks,
    pass_rate: passRate,
    duration_ms: 800 + index * 50,
    execution_plan: buildExecutionPlan(),
  };
}

function buildWorkflowResults(): AgentEvalWorkflowResult[] {
  return Array.from({ length: 8 }, (_, i) => buildWorkflowResult(i));
}

// ── Eval task results ─────────────────────────────────────────────────────────

/** Extract numeric index from record_uid like "rec-0004" → 4. */
function recordIndex(record_uid: string): number {
  const match = record_uid.match(/(\d+)$/);
  return match ? parseInt(match[1], 10) : 0;
}

/**
 * Builds a realistic EvalTaskResult[] for a given workflow's record_uid.
 * Mirrors the 5 tasks defined in buildMockAgentEvalProfile() / buildExecutionPlan().
 */
export function buildMockEvalTasks(record_uid: string): EvalTaskResult[] {
  const idx = recordIndex(record_uid);
  const base = iso(-(idx + 1) * 3 * 60_000 + 2_000);
  const failedVariants = [0, 0, 0, 1, 0, 2, 0, 1];
  const failedCount = failedVariants[idx % failedVariants.length];

  // confidence score passes unless failedCount >= 1
  const confidencePass = failedCount < 1;
  const confidenceVal = confidencePass
    ? parseFloat((0.65 + (idx % 5) * 0.07).toFixed(2))
    : 0.45;

  // judge score passes unless failedCount >= 2
  const judgePass = failedCount < 2;
  const judgeVal = judgePass ? 4.0 : 2.0;

  const tasks: EvalTaskResult[] = [
    {
      created_at: base,
      start_time: iso(-(idx + 1) * 3 * 60_000 + 2_000),
      end_time: iso(-(idx + 1) * 3 * 60_000 + 2_080),
      record_uid,
      entity_id: 42,
      entity_uid: "mock-eval-uid-0001",
      task_id: "check_response_format",
      task_type: "Assertion",
      passed: true,
      value: 1.0,
      assertion: { FieldPath: "response" },
      operator: "IsJson",
      expected: true,
      actual: true,
      message: "Response is valid JSON",
      condition: true,
      stage: 0,
    },
    {
      created_at: base,
      start_time: iso(-(idx + 1) * 3 * 60_000 + 2_100),
      end_time: iso(-(idx + 1) * 3 * 60_000 + 2_160),
      record_uid,
      entity_id: 42,
      entity_uid: "mock-eval-uid-0001",
      task_id: "check_intent_label",
      task_type: "Assertion",
      passed: true,
      value: 1.0,
      assertion: { FieldPath: "response.intent" },
      operator: "ContainsAny",
      expected: ["greeting", "faq", "complaint", "purchase", "support"],
      actual: idx % 3 === 0 ? "faq" : idx % 3 === 1 ? "support" : "purchase",
      message: "Intent label is one of the known categories",
      condition: true,
      stage: 1,
    },
    {
      created_at: base,
      start_time: iso(-(idx + 1) * 3 * 60_000 + 2_100),
      end_time: iso(-(idx + 1) * 3 * 60_000 + 2_200),
      record_uid,
      entity_id: 42,
      entity_uid: "mock-eval-uid-0001",
      task_id: "check_confidence_score",
      task_type: "Assertion",
      passed: confidencePass,
      value: confidenceVal,
      assertion: { FieldPath: "response.confidence" },
      operator: "GreaterThanOrEqual",
      expected: 0.6,
      actual: confidenceVal,
      message: confidencePass
        ? `Confidence ${confidenceVal} >= 0.6`
        : `Confidence ${confidenceVal} is below threshold 0.6`,
      condition: true,
      stage: 1,
    },
    {
      created_at: base,
      start_time: iso(-(idx + 1) * 3 * 60_000 + 2_200),
      end_time: iso(-(idx + 1) * 3 * 60_000 + 2_650),
      record_uid,
      entity_id: 42,
      entity_uid: "mock-eval-uid-0001",
      task_id: "judge_response_quality",
      task_type: "LLMJudge",
      passed: judgePass,
      value: judgeVal,
      assertion: { FieldPath: "response.text" },
      operator: "GreaterThanOrEqual",
      expected: 3,
      actual: judgeVal,
      message: judgePass
        ? `Quality score ${judgeVal} meets threshold`
        : `Quality score ${judgeVal} is below threshold 3`,
      condition: true,
      stage: 1,
    },
    {
      created_at: base,
      start_time: iso(-(idx + 1) * 3 * 60_000 + 2_700),
      end_time: iso(-(idx + 1) * 3 * 60_000 + 2_780),
      record_uid,
      entity_id: 42,
      entity_uid: "mock-eval-uid-0001",
      task_id: "check_trace_latency",
      task_type: "TraceAssertion",
      passed: true,
      value: 950 + idx * 20,
      assertion: { TraceAssertion: { TraceDuration: {} } },
      operator: "LessThan",
      expected: 5000,
      actual: 950 + idx * 20,
      message: `Trace duration ${950 + idx * 20}ms < 5000ms`,
      condition: true,
      stage: 2,
    },
  ];

  return tasks;
}

// ── Alerts ────────────────────────────────────────────────────────────────────

function buildDriftAlerts(): DriftAlertPaginationResponse {
  const alert: Alert = {
    created_at: iso(-15 * 60_000),
    entity_name: "pass_rate",
    alert: {
      [DriftType.Agent]: {
        metric_name: "pass_rate",
        baseline_value: 0.8,
        observed_value: 0.72,
        delta: null,
        alert_threshold: AlertThreshold.Below,
      },
    } as any,
    id: 9001,
    active: true,
  };

  return {
    items: [alert],
    has_next: false,
    has_previous: false,
  };
}

// ── Page data ─────────────────────────────────────────────────────────────────

/**
 * Returns a mock AgentMonitoringPageData (success) for prompt evaluation.
 */
export function getMockAgentMonitoringPageData(
  uid: string,
  registryType: RegistryType,
  timeRange: TimeRange,
): Extract<AgentMonitoringPageData, { status: "success" }> {
  const profile = buildMockAgentEvalProfile();
  // Override uid in the profile config so it matches the caller's uid.
  profile.config.uid = uid;

  const records: EvalRecordPaginationResponse = {
    items: buildEvalRecords(),
    has_next: false,
    has_previous: false,
  };

  const workflows: AgentEvalWorkflowPaginationResponse = {
    items: buildWorkflowResults(),
    has_next: false,
    has_previous: false,
  };

  const selectedData: SelectedAgentData = {
    metrics: {
      task: buildTaskMetrics(),
      workflow: buildWorkflowMetrics(),
    },
    driftAlerts: buildDriftAlerts(),
    records,
    workflows,
  };

  return {
    status: "success",
    profile,
    profileUri: "",
    selectedData,
    uid,
    registryType,
    selectedTimeRange: timeRange,
  };
}
