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
import type { MessageNum } from "$lib/components/agent/provider/types";
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

type MockDefinitionTask =
  | AssertionTask
  | LLMJudgeTask
  | TraceAssertionTask
  | AgentAssertionTask;

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
  {
    id: "check_response_text_not_empty",
    context_path: "response.text",
    item_context_path: null,
    operator: "IsNotEmpty",
    expected_value: true,
    description: "The final assistant response should not be empty",
    depends_on: ["check_response_format"],
    task_type: "Assertion",
    condition: true,
  },
];

const mockJudgeMessages: MessageNum[] = [
  {
    role: "developer",
    content:
      "You are an expert LLM judge. Evaluate the quality and relevance of the assistant's response on a scale of 1 to 5, where 1 is very poor and 5 is excellent. Return only the numeric score.",
  },
  {
    role: "user",
    content:
      "Context: {{context}}\n\nAssistant response: {{response.text}}\n\nRate the response quality (1-5):",
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
    messages: mockJudgeMessages,
  },
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
    description: "LLM judge rates response quality on a 1-5 scale",
  },
  {
    id: "judge_response_quality_success",
    prompt: mockJudgePrompt,
    context_path: "response.text",
    expected_value: 4,
    operator: "GreaterThanOrEqual",
    task_type: "LLMJudge",
    depends_on: ["check_response_format"],
    max_retries: 2,
    condition: true,
    description: "Mock success LLM judge task for theme validation",
  },
  {
    id: "judge_response_quality_failure",
    prompt: mockJudgePrompt,
    context_path: "response.text",
    expected_value: 4,
    operator: "GreaterThanOrEqual",
    task_type: "LLMJudge",
    depends_on: ["check_response_format"],
    max_retries: 2,
    condition: true,
    description: "Mock failure LLM judge task for theme validation",
  },
];

const traceTasks: TraceAssertionTask[] = [
  {
    id: "trace_span_sequence_core",
    assertion: {
      SpanSequence: {
        span_names: [
          "orchestrate_request",
          "classify_intent",
          "fetch_kb_answer",
          "compose_response",
        ],
      },
    },
    operator: "Equals",
    expected_value: true,
    description: "The core agent workflow should emit the expected span order",
    depends_on: [],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_set_required",
    assertion: {
      SpanSet: {
        span_names: ["classify_intent", "fetch_kb_answer", "compose_response"],
      },
    },
    operator: "ContainsAll",
    expected_value: ["classify_intent", "fetch_kb_answer", "compose_response"],
    description: "Required workflow spans must all be present in the trace",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_count_llm",
    assertion: {
      SpanCount: {
        filter: { ByNamePattern: { pattern: "llm.*" } },
      },
    },
    operator: "GreaterThanOrEqual",
    expected_value: 2,
    description: "At least two LLM-related spans should be emitted",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_exists_tool",
    assertion: {
      SpanExists: {
        filter: { ByName: { name: "fetch_kb_answer" } },
      },
    },
    operator: "Equals",
    expected_value: true,
    description: "Tool invocation span should exist for knowledge-base lookups",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_attribute_provider",
    assertion: {
      SpanAttribute: {
        filter: { ByName: { name: "llm.call" } },
        attribute_key: "gen_ai.request.model",
      },
    },
    operator: "Contains",
    expected_value: "gpt-4o",
    description: "LLM call span should expose the configured provider model",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_duration_tool",
    assertion: {
      SpanDuration: {
        filter: { ByName: { name: "fetch_kb_answer" } },
      },
    },
    operator: "LessThan",
    expected_value: 1200,
    description: "Tool lookup span should stay within the latency budget",
    depends_on: ["trace_span_exists_tool"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_aggregation_tokens",
    assertion: {
      SpanAggregation: {
        filter: { ByName: { name: "llm.call" } },
        attribute_key: "gen_ai.usage.total_tokens",
        aggregation: "Average",
      },
    },
    operator: "LessThanOrEqual",
    expected_value: 2000,
    description: "Average total-token usage for the LLM span should remain bounded",
    depends_on: ["trace_span_attribute_provider"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_duration_total",
    assertion: { TraceDuration: {} },
    operator: "LessThan",
    expected_value: 5000,
    description: "End-to-end trace duration must stay under 5 000 ms",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_span_count_total",
    assertion: { TraceSpanCount: {} },
    operator: "GreaterThanOrEqual",
    expected_value: 8,
    description: "A healthy orchestration should emit multiple spans across services",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_error_count",
    assertion: { TraceErrorCount: {} },
    operator: "Equals",
    expected_value: 0,
    description: "Workflow traces should not contain error spans",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_service_count",
    assertion: { TraceServiceCount: {} },
    operator: "GreaterThanOrEqual",
    expected_value: 2,
    description: "Trace should traverse at least two services during orchestration",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_max_depth",
    assertion: { TraceMaxDepth: {} },
    operator: "LessThanOrEqual",
    expected_value: 4,
    description: "Nested span depth should remain understandable and shallow",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_attribute_workflow",
    assertion: {
      TraceAttribute: {
        attribute_key: "workflow.name",
      },
    },
    operator: "Equals",
    expected_value: "agent-eval-workflow",
    description: "Workflow name should be stamped on the root trace metadata",
    depends_on: ["trace_span_sequence_core"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_attribute_filter_assertion",
    assertion: {
      AttributeFilter: {
        key: "gen_ai.response.finish_reason",
        mode: "Any",
        task: {
          Assertion: {
            id: "nested_trace_finish_reason",
            context_path: null,
            item_context_path: null,
            operator: "Equals",
            expected_value: "stop",
            description: "Finish reason should be the standard stop token",
            depends_on: [],
            task_type: "Assertion",
            condition: true,
          },
        },
      },
    },
    operator: "Contains",
    expected_value: "stop",
    description: "Trace attribute filters should support nested assertion tasks",
    depends_on: ["trace_span_attribute_provider"],
    task_type: "TraceAssertion",
    condition: true,
  },
  {
    id: "trace_attribute_filter_agent",
    assertion: {
      AttributeFilter: {
        key: "tool.name",
        mode: "All",
        task: {
          AgentAssertion: {
            id: "nested_trace_tool_name",
            assertion: {
              ToolCalled: { name: "fetch_kb_answer" },
            },
            operator: "Equals",
            expected_value: true,
            description: "Every tool.name attribute should map to the expected tool",
            depends_on: [],
            task_type: "AgentAssertion",
            condition: true,
            provider: Provider.OpenAI,
            context_path: null,
          },
        },
      },
    },
    operator: "Contains",
    expected_value: "fetch_kb_answer",
    description: "Trace attribute filters should also support nested agent assertions",
    depends_on: ["trace_span_exists_tool"],
    task_type: "TraceAssertion",
    condition: true,
  },
];

const agentTasks: AgentAssertionTask[] = [
  {
    id: "agent_tool_called_classify",
    assertion: {
      ToolCalled: {
        name: "classify_intent",
      },
    },
    operator: "Equals",
    expected_value: true,
    description: "Intent classifier tool should be invoked during orchestration",
    depends_on: ["check_response_format"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.tools",
  },
  {
    id: "agent_tool_not_called_fallback",
    assertion: {
      ToolNotCalled: {
        name: "fallback_answer",
      },
    },
    operator: "Equals",
    expected_value: true,
    description: "Fallback tool should not be used for normal knowledge-base requests",
    depends_on: ["agent_tool_called_classify"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.tools",
  },
  {
    id: "agent_tool_called_with_args",
    assertion: {
      ToolCalledWithArgs: {
        name: "fetch_kb_answer",
        arguments: {
          query: "return policy for electronics",
          customer_id: "customer_7842",
        },
      },
    },
    operator: "Equals",
    expected_value: {
      query: "return policy for electronics",
      customer_id: "customer_7842",
    },
    description: "Knowledge-base tool should be invoked with the expected arguments",
    depends_on: ["agent_tool_called_classify"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.tools",
  },
  {
    id: "agent_tool_call_sequence",
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
    context_path: "response.tools",
  },
  {
    id: "agent_tool_call_count",
    assertion: {
      ToolCallCount: {
        name: null,
      },
    },
    operator: "GreaterThanOrEqual",
    expected_value: 2,
    description: "The workflow should perform at least two tool calls",
    depends_on: ["agent_tool_call_sequence"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.tools",
  },
  {
    id: "agent_tool_argument_customer_id",
    assertion: {
      ToolArgument: {
        name: "fetch_kb_answer",
        argument_key: "customer_id",
      },
    },
    operator: "Equals",
    expected_value: "customer_7842",
    description: "The customer ID argument should flow through to the tool call",
    depends_on: ["agent_tool_called_with_args"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.tools",
  },
  {
    id: "agent_tool_result_fetch",
    assertion: {
      ToolResult: {
        name: "fetch_kb_answer",
      },
    },
    operator: "Contains",
    expected_value: "30 days",
    description: "Tool result payload should contain the expected return-policy snippet",
    depends_on: ["agent_tool_called_with_args"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.tools",
  },
  {
    id: "agent_response_content",
    assertion: {
      ResponseContent: {},
    },
    operator: "Contains",
    expected_value: "30 days",
    description: "Final response text should mention the return-policy answer",
    depends_on: ["check_response_text_not_empty"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.text",
  },
  {
    id: "agent_response_model",
    assertion: {
      ResponseModel: {},
    },
    operator: "Equals",
    expected_value: "gpt-4o",
    description: "Rendered response metadata should expose the correct model name",
    depends_on: ["check_response_format"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.metadata.model",
  },
  {
    id: "agent_response_finish_reason",
    assertion: {
      ResponseFinishReason: {},
    },
    operator: "Equals",
    expected_value: "stop",
    description: "The response should complete with the standard stop reason",
    depends_on: ["check_response_format"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.metadata.finish_reason",
  },
  {
    id: "agent_response_input_tokens",
    assertion: {
      ResponseInputTokens: {},
    },
    operator: "GreaterThan",
    expected_value: 200,
    description: "Prompt token count should exceed the minimum expected size",
    depends_on: ["agent_response_model"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.metadata.usage.input_tokens",
  },
  {
    id: "agent_response_output_tokens",
    assertion: {
      ResponseOutputTokens: {},
    },
    operator: "GreaterThan",
    expected_value: 100,
    description: "Completion token count should exceed the minimum expected size",
    depends_on: ["agent_response_model"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.metadata.usage.output_tokens",
  },
  {
    id: "agent_response_total_tokens",
    assertion: {
      ResponseTotalTokens: {},
    },
    operator: "GreaterThan",
    expected_value: 300,
    description: "Total token count should include both prompt and completion usage",
    depends_on: ["agent_response_input_tokens", "agent_response_output_tokens"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.metadata.usage.total_tokens",
  },
  {
    id: "agent_response_field_intent",
    assertion: {
      ResponseField: {
        path: "response.intent",
      },
    },
    operator: "Equals",
    expected_value: "faq",
    description: "Response field assertions should be able to reach nested response keys",
    depends_on: ["check_intent_label"],
    task_type: "AgentAssertion",
    condition: true,
    provider: Provider.OpenAI,
    context_path: "response.intent",
  },
];

const assertionTasksObj: AssertionTasks = {
  assertion: assertionTasks,
  judge: judgeTasks,
  trace: traceTasks,
  agent: agentTasks,
};

const allMockTasks: MockDefinitionTask[] = [
  ...assertionTasks,
  ...judgeTasks,
  ...traceTasks,
  ...agentTasks,
];

const mockStageTaskIds: string[][] = [
  assertionTasks.map((task) => task.id),
  judgeTasks.map((task) => task.id),
  traceTasks.map((task) => task.id),
  agentTasks.map((task) => task.id),
];

const mockStageByTaskId = new Map<string, number>(
  mockStageTaskIds.flatMap((taskIds, stageIndex) =>
    taskIds.map((taskId) => [taskId, stageIndex] as const),
  ),
);

const failureScenarios: string[][] = [
  [],
  ["check_confidence_score", "trace_error_count"],
  ["judge_response_quality", "agent_response_finish_reason"],
  [
    "trace_attribute_filter_agent",
    "agent_tool_called_with_args",
    "agent_response_field_intent",
  ],
  ["trace_service_count", "agent_tool_not_called_fallback"],
  [
    "trace_span_duration_tool",
    "agent_response_total_tokens",
    "check_response_text_not_empty",
  ],
];

const forcedPassedTaskIds = new Set<string>([
  "judge_response_quality_success",
]);

const forcedFailedTaskIds = new Set<string>([
  "judge_response_quality_failure",
]);

/**
 * Subset of tasks flagged as conditional in dev mocks.
 * This keeps TaskDetailView themes varied (conditional / passed / failed)
 * instead of every task rendering as conditional.
 */
const conditionalMockTaskIds = new Set<string>([
  "check_response_format",
  "judge_response_quality",
  "trace_span_sequence_core",
  "trace_attribute_filter_agent",
  "agent_tool_called_search",
  "agent_response_field_intent",
]);

function isMockTraceTask(task: MockDefinitionTask): task is TraceAssertionTask {
  return task.task_type === "TraceAssertion";
}

function isMockAgentTask(task: MockDefinitionTask): task is AgentAssertionTask {
  return task.task_type === "AgentAssertion";
}

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
    task_ids: allMockTasks.map((task) => task.id),
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

function buildEvalRecord(index: number, entityUid = "mock-eval-uid-0001"): EvalRecord {
  const createdAt = iso(-(index + 1) * 3 * 60_000);
  const status = RECORD_STATUSES[index % RECORD_STATUSES.length];
  const isProcessed = status === Status.Processed || status === Status.Failed;
  const recordUid = `${entityUid}-rec-${String(index + 1).padStart(4, "0")}`;

  return {
    record_id: `rec-${String(index + 1).padStart(4, "0")}`,
    created_at: createdAt,
    uid: recordUid,
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
    entity_uid: entityUid,
    status,
    entity_type: EntityType.Agent,
  };
}

function buildEvalRecords(entityUid = "mock-eval-uid-0001"): EvalRecord[] {
  return Array.from({ length: 10 }, (_, i) => buildEvalRecord(i, entityUid));
}

// ── Workflow results ──────────────────────────────────────────────────────────

function buildExecutionPlan(): ExecutionPlan {
  const nodes: Record<string, ExecutionNode> = {};

  for (const task of allMockTasks) {
    nodes[task.id] = {
      id: task.id,
      stage: mockStageByTaskId.get(task.id) ?? 0,
      parents: [...task.depends_on],
      children: [],
    };
  }

  for (const task of allMockTasks) {
    for (const parentId of task.depends_on) {
      if (nodes[parentId]) {
        nodes[parentId].children.push(task.id);
      }
    }
  }

  return {
    stages: mockStageTaskIds.map((stageTaskIds) => [...stageTaskIds]),
    nodes,
  };
}

function buildWorkflowResult(index: number, entityUid = "mock-eval-uid-0001"): AgentEvalWorkflowResult {
  const scenarioFailedTaskIds = new Set(
    failureScenarios[index % failureScenarios.length] ?? [],
  );
  for (const taskId of forcedFailedTaskIds) {
    scenarioFailedTaskIds.add(taskId);
  }

  const failedTasks = scenarioFailedTaskIds.size;
  const totalTasks = allMockTasks.length;
  const passedTasks = totalTasks - failedTasks;
  const passRate = parseFloat((passedTasks / totalTasks).toFixed(2));

  return {
    id: 2000 + index,
    record_uid: `${entityUid}-rec-${String(index + 1).padStart(4, "0")}`,
    entity_id: 42,
    entity_uid: entityUid,
    created_at: iso(-(index + 1) * 3 * 60_000 + 2_000),
    total_tasks: totalTasks,
    passed_tasks: passedTasks,
    failed_tasks: failedTasks,
    pass_rate: passRate,
    duration_ms: 800 + index * 50,
    execution_plan: buildExecutionPlan(),
  };
}

function buildWorkflowResults(entityUid = "mock-eval-uid-0001"): AgentEvalWorkflowResult[] {
  return Array.from({ length: 8 }, (_, i) => buildWorkflowResult(i, entityUid));
}

// ── Eval task results ─────────────────────────────────────────────────────────

/** Extract numeric index from record_uid like "rec-0004" → 4. */
function recordIndex(record_uid: string): number {
  const match = record_uid.match(/(\d+)$/);
  return match ? parseInt(match[1], 10) : 0;
}

/**
 * Builds a realistic EvalTaskResult[] for a given workflow's record_uid.
 * Mirrors the full task catalog defined in buildMockAgentEvalProfile() / buildExecutionPlan().
 */
export function buildMockEvalTasks(record_uid: string): EvalTaskResult[] {
  const idx = recordIndex(record_uid);
  const baseMs = NOW - (idx + 1) * 3 * 60_000 + 2_000;
  const createdAt = new Date(baseMs).toISOString();
  const failedTaskIds = new Set(
    failureScenarios[idx % failureScenarios.length] ?? [],
  );

  return allMockTasks.map((task, taskIndex) => {
    const passed = forcedPassedTaskIds.has(task.id)
      ? true
      : forcedFailedTaskIds.has(task.id)
        ? false
        : !failedTaskIds.has(task.id);
    const { actual, value, message } = getMockTaskOutcome(task, passed);
    const startTime = new Date(baseMs + taskIndex * 110).toISOString();
    const endTime = new Date(baseMs + taskIndex * 110 + 80).toISOString();

    return {
      created_at: createdAt,
      start_time: startTime,
      end_time: endTime,
      record_uid,
      entity_id: 42,
      entity_uid: "mock-eval-uid-0001",
      task_id: task.id,
      task_type: task.task_type,
      passed,
      value,
      assertion: getMockAssertionPayload(task),
      operator: task.operator,
      expected: task.expected_value,
      actual,
      message,
      condition: conditionalMockTaskIds.has(task.id),
      stage: mockStageByTaskId.get(task.id) ?? 0,
    };
  });
}

function getMockAssertionPayload(task: MockDefinitionTask): EvalTaskResult["assertion"] {
  if (isMockTraceTask(task)) {
    return { TraceAssertion: task.assertion };
  }

  if (isMockAgentTask(task)) {
    return { AgentAssertion: task.assertion };
  }

  return { FieldPath: "context_path" in task ? task.context_path : null };
}

function getMockTaskOutcome(
  task: MockDefinitionTask,
  passed: boolean,
): Pick<EvalTaskResult, "actual" | "value" | "message"> {
  switch (task.id) {
    case "check_response_format":
      return {
        actual: passed ? true : "```not-json```",
        value: passed ? 1 : 0,
        message: passed
          ? "Response is valid JSON"
          : "Response payload is not valid JSON",
      };
    case "check_intent_label":
      return {
        actual: passed ? "faq" : "unknown",
        value: passed ? 1 : 0,
        message: passed
          ? "Intent label is one of the known categories"
          : "Intent label is not part of the approved taxonomy",
      };
    case "check_confidence_score":
      return {
        actual: passed ? 0.82 : 0.42,
        value: passed ? 0.82 : 0.42,
        message: passed
          ? "Confidence score exceeds the minimum threshold"
          : "Confidence score is below the minimum threshold",
      };
    case "check_response_text_not_empty":
      return {
        actual: passed
          ? "Customers can return electronics within 30 days of purchase."
          : "",
        value: passed ? 1 : 0,
        message: passed
          ? "Assistant returned a non-empty answer"
          : "Assistant returned an empty response body",
      };
    case "judge_response_quality":
      return {
        actual: passed ? 4 : 2,
        value: passed ? 4 : 2,
        message: passed
          ? "LLM judge score meets the quality bar"
          : "LLM judge score fell below the quality bar",
      };
    case "judge_response_quality_success":
      return {
        actual: 5,
        value: 5,
        message: "LLM judge success mock scored above threshold",
      };
    case "judge_response_quality_failure":
      return {
        actual: 2,
        value: 2,
        message: "LLM judge failure mock scored below threshold",
      };
    case "trace_span_sequence_core":
      return {
        actual: passed
          ? [
              "orchestrate_request",
              "classify_intent",
              "fetch_kb_answer",
              "compose_response",
            ]
          : ["orchestrate_request", "fetch_kb_answer", "compose_response"],
        value: passed ? 1 : 0,
        message: passed
          ? "Core spans were emitted in the expected order"
          : "Trace span order deviated from the expected workflow",
      };
    case "trace_span_set_required":
      return {
        actual: passed
          ? ["classify_intent", "fetch_kb_answer", "compose_response"]
          : ["classify_intent", "compose_response"],
        value: passed ? 1 : 0,
        message: passed
          ? "All required workflow spans were present"
          : "One or more required workflow spans were missing",
      };
    case "trace_span_count_llm":
      return {
        actual: passed ? 3 : 1,
        value: passed ? 3 : 1,
        message: passed
          ? "LLM span count meets the expected minimum"
          : "Too few LLM spans were recorded",
      };
    case "trace_span_exists_tool":
      return {
        actual: passed,
        value: passed ? 1 : 0,
        message: passed
          ? "Tool invocation span exists in the trace"
          : "Expected tool span was not found in the trace",
      };
    case "trace_span_attribute_provider":
      return {
        actual: passed ? "gpt-4o" : "claude-sonnet",
        value: passed ? 1 : 0,
        message: passed
          ? "LLM span exposes the expected provider model"
          : "LLM span exposes the wrong provider model",
      };
    case "trace_span_duration_tool":
      return {
        actual: passed ? 640 : 1850,
        value: passed ? 640 : 1850,
        message: passed
          ? "Tool span duration stayed within budget"
          : "Tool span duration exceeded the latency budget",
      };
    case "trace_span_aggregation_tokens":
      return {
        actual: passed ? 1420 : 2890,
        value: passed ? 1420 : 2890,
        message: passed
          ? "Average token aggregation is within the budget"
          : "Average token aggregation exceeds the budget",
      };
    case "trace_duration_total":
      return {
        actual: passed ? 1820 : 6320,
        value: passed ? 1820 : 6320,
        message: passed
          ? "End-to-end trace duration is within budget"
          : "End-to-end trace duration exceeded the budget",
      };
    case "trace_span_count_total":
      return {
        actual: passed ? 11 : 4,
        value: passed ? 11 : 4,
        message: passed
          ? "Trace emitted the expected number of spans"
          : "Trace emitted too few spans",
      };
    case "trace_error_count":
      return {
        actual: passed ? 0 : 2,
        value: passed ? 0 : 2,
        message: passed
          ? "No error spans were recorded"
          : "Trace contains unexpected error spans",
      };
    case "trace_service_count":
      return {
        actual: passed ? 3 : 1,
        value: passed ? 3 : 1,
        message: passed
          ? "Trace covers multiple services as expected"
          : "Trace did not traverse enough services",
      };
    case "trace_max_depth":
      return {
        actual: passed ? 3 : 7,
        value: passed ? 3 : 7,
        message: passed
          ? "Trace nesting depth is within the readability target"
          : "Trace nesting depth is deeper than expected",
      };
    case "trace_attribute_workflow":
      return {
        actual: passed ? "agent-eval-workflow" : "chat-session",
        value: passed ? 1 : 0,
        message: passed
          ? "Trace attribute contains the expected workflow name"
          : "Trace attribute contains the wrong workflow name",
      };
    case "trace_attribute_filter_assertion":
      return {
        actual: passed ? ["stop", "stop"] : ["length", "content_filter"],
        value: passed ? 1 : 0,
        message: passed
          ? "Attribute filter assertion matched the finish reason values"
          : "Attribute filter assertion found unexpected finish reasons",
      };
    case "trace_attribute_filter_agent":
      return {
        actual: passed ? ["fetch_kb_answer", "fetch_kb_answer"] : ["fallback_answer"],
        value: passed ? 1 : 0,
        message: passed
          ? "Nested agent assertion matched the filtered tool attributes"
          : "Nested agent assertion did not match the filtered tool attributes",
      };
    case "agent_tool_called_classify":
      return {
        actual: passed,
        value: passed ? 1 : 0,
        message: passed
          ? "Intent classification tool was called"
          : "Intent classification tool was not called",
      };
    case "agent_tool_not_called_fallback":
      return {
        actual: passed ? false : true,
        value: passed ? 1 : 0,
        message: passed
          ? "Fallback tool was correctly skipped"
          : "Fallback tool was called unexpectedly",
      };
    case "agent_tool_called_with_args":
      return {
        actual: passed
          ? {
              query: "return policy for electronics",
              customer_id: "customer_7842",
            }
          : {
              query: "shipping policy",
              customer_id: "customer_7842",
            },
        value: passed ? 1 : 0,
        message: passed
          ? "Tool arguments matched the expected request payload"
          : "Tool arguments did not match the expected request payload",
      };
    case "agent_tool_call_sequence":
      return {
        actual: passed
          ? ["classify_intent", "fetch_kb_answer"]
          : ["fetch_kb_answer", "classify_intent"],
        value: passed ? 1 : 0,
        message: passed
          ? "Tool calls occurred in the expected sequence"
          : "Tool call ordering deviated from the expected sequence",
      };
    case "agent_tool_call_count":
      return {
        actual: passed ? 3 : 1,
        value: passed ? 3 : 1,
        message: passed
          ? "Workflow executed enough tool calls"
          : "Workflow executed too few tool calls",
      };
    case "agent_tool_argument_customer_id":
      return {
        actual: passed ? "customer_7842" : "customer_0000",
        value: passed ? 1 : 0,
        message: passed
          ? "Customer ID argument propagated correctly"
          : "Customer ID argument did not propagate correctly",
      };
    case "agent_tool_result_fetch":
      return {
        actual: passed
          ? "Return window: 30 days for electronics"
          : "No matching policy article found",
        value: passed ? 1 : 0,
        message: passed
          ? "Tool result contained the expected policy text"
          : "Tool result did not contain the expected policy text",
      };
    case "agent_response_content":
      return {
        actual: passed
          ? "Customers can return electronics within 30 days of purchase."
          : "I am not sure about that policy.",
        value: passed ? 1 : 0,
        message: passed
          ? "Response content contains the expected answer"
          : "Response content did not contain the expected answer",
      };
    case "agent_response_model":
      return {
        actual: passed ? "gpt-4o" : "gpt-4o-mini",
        value: passed ? 1 : 0,
        message: passed
          ? "Response metadata reports the expected model"
          : "Response metadata reports the wrong model",
      };
    case "agent_response_finish_reason":
      return {
        actual: passed ? "stop" : "length",
        value: passed ? 1 : 0,
        message: passed
          ? "Finish reason matched the expected stop token"
          : "Finish reason did not match the expected stop token",
      };
    case "agent_response_input_tokens":
      return {
        actual: passed ? 412 : 120,
        value: passed ? 412 : 120,
        message: passed
          ? "Input token count exceeded the minimum threshold"
          : "Input token count was below the minimum threshold",
      };
    case "agent_response_output_tokens":
      return {
        actual: passed ? 148 : 32,
        value: passed ? 148 : 32,
        message: passed
          ? "Output token count exceeded the minimum threshold"
          : "Output token count was below the minimum threshold",
      };
    case "agent_response_total_tokens":
      return {
        actual: passed ? 560 : 152,
        value: passed ? 560 : 152,
        message: passed
          ? "Total token count exceeded the minimum threshold"
          : "Total token count was below the minimum threshold",
      };
    case "agent_response_field_intent":
      return {
        actual: passed ? "faq" : "unknown",
        value: passed ? 1 : 0,
        message: passed
          ? "Nested response field matched the expected value"
          : "Nested response field did not match the expected value",
      };
    default:
      return {
        actual: passed,
        value: passed ? 1 : 0,
        message: passed ? `${task.id} passed` : `${task.id} failed`,
      };
  }
}

// ── Alerts ────────────────────────────────────────────────────────────────────

function buildDriftAlerts(): DriftAlertPaginationResponse {
  const alert: Alert = {
    created_at: iso(-15 * 60_000),
    entity_name: "pass_rate",
    alert: {
      [DriftType.Spc]: {
        feature: "pass_rate",
        kind: "AllGood",
        zone: "NotApplicable",
      },
      [DriftType.Psi]: {
        feature: "pass_rate",
        drift: 0.04,
        threshold: 0.2,
      },
      [DriftType.Custom]: {
        metric_name: "pass_rate",
        baseline_value: 0.8,
        observed_value: 0.72,
        delta: null,
        alert_threshold: AlertThreshold.Below,
      },
      [DriftType.Agent]: {
        metric_name: "pass_rate",
        baseline_value: 0.8,
        observed_value: 0.72,
        delta: null,
        alert_threshold: AlertThreshold.Below,
      },
    },
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
    items: buildEvalRecords(uid),
    has_next: false,
    has_previous: false,
  };

  const workflows: AgentEvalWorkflowPaginationResponse = {
    items: buildWorkflowResults(uid),
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
    mockMode: true,
  };
}
