/**
 * Shared types for agent evaluation dashboard components.
 * These types are used across both the route layer and the component layer.
 */

import type { PromptCard } from '$lib/components/card/card_interfaces/promptcard';
import type { GenAIMonitoringPageData } from '$lib/components/scouter/dashboard/utils';

/**
 * Holds a prompt card together with its monitoring/evaluation data.
 * Produced by the evaluation page loader and consumed by the agent
 * evaluation dashboard components.
 */
export interface AgentPromptEvalData {
  promptCard: PromptCard;
  monitoringData: GenAIMonitoringPageData;
}
