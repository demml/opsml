import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import AgentsTable from "../AgentsTable.svelte";
import type { GenAiAgentActivity } from "../types";

describe("AgentsTable", () => {
  it("renders multiple rows sharing the same agent_name", () => {
    const agents: GenAiAgentActivity[] = [
      {
        agent_name: "responder_agent",
        agent_id: null,
        conversation_id: "conv-1",
        span_count: 3,
        total_input_tokens: 100,
        total_output_tokens: 50,
        last_seen: null,
      },
      {
        agent_name: "responder_agent",
        agent_id: null,
        conversation_id: "conv-2",
        span_count: 7,
        total_input_tokens: 200,
        total_output_tokens: 90,
        last_seen: null,
      },
    ];

    const { getAllByText } = render(AgentsTable, { props: { agents } });
    expect(getAllByText("responder_agent")).toHaveLength(2);
  });
});
