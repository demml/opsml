import { describe, expect, it } from "vitest";
import type { AgentEvalProfile } from "$lib/components/scouter/agent/types";
import type {
  EvalTaskResult,
  AssertionTask,
  TraceAssertionTask,
  AgentAssertionTask,
  LLMJudgeTask,
} from "$lib/components/scouter/agent/task";
import {
  getAssertion,
  isTraceAssertionValue,
  isAgentAssertionValue,
} from "$lib/components/scouter/agent/task";
import { AgentEvalProfileHelper } from "$lib/components/scouter/agent/utils";

function makeBaseResult(): Omit<EvalTaskResult, "assertion"> {
  return {
    created_at: "2026-01-01T00:00:00Z",
    start_time: "2026-01-01T00:00:00Z",
    end_time: "2026-01-01T00:00:01Z",
    record_uid: "uid-1",
    entity_id: 1,
    task_id: "task-1",
    task_type: "Assertion",
    passed: true,
    value: 1.0,
    operator: "Equals",
    expected: "foo",
    actual: "foo",
    message: "ok",
    entity_uid: "e-uid-1",
    condition: true,
    stage: 0,
  };
}

function makeProfile(): AgentEvalProfile {
  const assertionTask: AssertionTask = {
    id: "a-1",
    context_path: "$.field",
    item_context_path: null,
    operator: "Equals",
    expected_value: 42,
    description: null,
    depends_on: [],
    task_type: "Assertion",
    condition: true,
  };
  const traceTask: TraceAssertionTask = {
    id: "t-1",
    assertion: { TraceDuration: {} },
    operator: "LessThan",
    expected_value: 500,
    description: null,
    depends_on: [],
    task_type: "TraceAssertion",
    condition: true,
  };
  const agentTask: AgentAssertionTask = {
    id: "ag-1",
    assertion: { ToolCalled: { name: "my_tool" } },
    operator: "Equals",
    expected_value: true,
    description: null,
    depends_on: [],
    task_type: "AgentAssertion",
    condition: true,
    provider: null,
    context_path: null,
  };
  const judgeTask: LLMJudgeTask = {
    id: "j-1",
    prompt: { provider: "OpenAI", model: "gpt-4o", messages: [] } as any,
    context_path: null,
    expected_value: "pass",
    operator: "Equals",
    task_type: "LLMJudge",
    depends_on: [],
    max_retries: null,
    condition: true,
    description: null,
  };

  return {
    tasks: {
      assertion: [assertionTask],
      trace: [traceTask],
      agent: [agentTask],
      judge: [judgeTask],
    },
  } as unknown as AgentEvalProfile;
}

describe("getAssertion", () => {
  it("returns FieldPath value for FieldPath assertion", () => {
    const result: EvalTaskResult = {
      ...makeBaseResult(),
      assertion: { FieldPath: "$.response" },
    };
    expect(getAssertion(result)).toBe("$.response");
  });

  it("returns null for FieldPath: null", () => {
    const result: EvalTaskResult = {
      ...makeBaseResult(),
      assertion: { FieldPath: null },
    };
    expect(getAssertion(result)).toBeNull();
  });

  it("returns TraceAssertion object for trace assertion", () => {
    const result: EvalTaskResult = {
      ...makeBaseResult(),
      assertion: { TraceAssertion: { TraceDuration: {} } },
    };
    const assertion = getAssertion(result);
    expect(assertion).toEqual({ TraceDuration: {} });
  });

  it("returns AgentAssertion object for agent assertion", () => {
    const result: EvalTaskResult = {
      ...makeBaseResult(),
      assertion: { AgentAssertion: { ToolCalled: { name: "my_tool" } } },
    };
    const assertion = getAssertion(result);
    expect(assertion).toEqual({ ToolCalled: { name: "my_tool" } });
  });

  it("throws on invalid assertion variant", () => {
    const result: EvalTaskResult = {
      ...makeBaseResult(),
      assertion: { Unknown: "bad" } as any,
    };
    expect(() => getAssertion(result)).toThrow("Invalid Assertion variant");
  });
});

describe("isTraceAssertionValue", () => {
  it("returns true for TraceDuration", () => {
    expect(isTraceAssertionValue({ TraceDuration: {} })).toBe(true);
  });

  it("returns true for SpanSequence", () => {
    expect(isTraceAssertionValue({ SpanSequence: { span_names: ["a"] } })).toBe(true);
  });

  it("returns false for null", () => {
    expect(isTraceAssertionValue(null)).toBe(false);
  });

  it("returns false for string", () => {
    expect(isTraceAssertionValue("$.field")).toBe(false);
  });

  it("returns false for AgentAssertion keys", () => {
    expect(isTraceAssertionValue({ ToolCalled: { name: "x" } })).toBe(false);
  });
});

describe("isAgentAssertionValue", () => {
  it("returns true for ToolCalled", () => {
    expect(isAgentAssertionValue({ ToolCalled: { name: "x" } })).toBe(true);
  });

  it("returns true for ResponseContent", () => {
    expect(isAgentAssertionValue({ ResponseContent: {} })).toBe(true);
  });

  it("returns false for null", () => {
    expect(isAgentAssertionValue(null)).toBe(false);
  });

  it("returns false for string", () => {
    expect(isAgentAssertionValue("$.field")).toBe(false);
  });

  it("returns false for TraceAssertion keys", () => {
    expect(isAgentAssertionValue({ TraceDuration: {} })).toBe(false);
  });
});

describe("AgentEvalProfileHelper", () => {
  const profile = makeProfile();

  it("returns assertion task by id", () => {
    const task = AgentEvalProfileHelper.getAssertionById(profile, "a-1");
    expect(task).not.toBeNull();
    expect(task!.id).toBe("a-1");
  });

  it("returns null for unknown assertion id", () => {
    expect(AgentEvalProfileHelper.getAssertionById(profile, "missing")).toBeNull();
  });

  it("returns trace assertion task by id", () => {
    const task = AgentEvalProfileHelper.getTraceAssertionById(profile, "t-1");
    expect(task).not.toBeNull();
    expect(task!.task_type).toBe("TraceAssertion");
  });

  it("handles missing tasks.trace gracefully", () => {
    const noTrace = { ...profile, tasks: { ...profile.tasks, trace: undefined } } as unknown as AgentEvalProfile;
    expect(AgentEvalProfileHelper.getTraceAssertionById(noTrace, "t-1")).toBeNull();
  });

  it("returns agent assertion task by id", () => {
    const task = AgentEvalProfileHelper.getAgentAssertionById(profile, "ag-1");
    expect(task).not.toBeNull();
    expect(task!.task_type).toBe("AgentAssertion");
  });

  it("handles missing tasks.agent gracefully", () => {
    const noAgent = { ...profile, tasks: { ...profile.tasks, agent: undefined } } as unknown as AgentEvalProfile;
    expect(AgentEvalProfileHelper.getAgentAssertionById(noAgent, "ag-1")).toBeNull();
  });

  it("returns LLM judge task by id", () => {
    const task = AgentEvalProfileHelper.getLLMJudgeById(profile, "j-1");
    expect(task).not.toBeNull();
    expect(task!.id).toBe("j-1");
  });
});
