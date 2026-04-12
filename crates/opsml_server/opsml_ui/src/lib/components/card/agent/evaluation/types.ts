/**
 * Shared types for agent evaluation dashboard components.
 * These types are used across both the route layer and the component layer.
 */

import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type { AgentMonitoringPageData } from "$lib/components/scouter/dashboard/utils";
import type {
  AgentEvalProfile,
  EvalRecord,
} from "$lib/components/scouter/agent/types";
import type { AgentEvalWorkflowResult } from "$lib/components/scouter/agent/task";

/**
 * Holds a prompt card together with its monitoring/evaluation data.
 * Produced by the evaluation page loader and consumed by the agent
 * evaluation dashboard components.
 */
export interface AgentPromptEvalData {
  promptCard: PromptCard;
  monitoringData: AgentMonitoringPageData;
}

export type RecordWithAgent = EvalRecord & {
  _agentName: string;
  _evalPath: string;
};
export type WorkflowWithAgent = AgentEvalWorkflowResult & {
  _agentName: string;
  _evalPath: string;
  _profile: AgentEvalProfile;
};

/** Merged pagination state for the agent eval record table. */
export interface AgentRecordPage {
  items: RecordWithAgent[];
  hasNext: boolean;
  hasPrevious: boolean;
}

/** Merged pagination state for the agent eval workflow table. */
export interface AgentWorkflowPage {
  items: WorkflowWithAgent[];
  hasNext: boolean;
  hasPrevious: boolean;
}
