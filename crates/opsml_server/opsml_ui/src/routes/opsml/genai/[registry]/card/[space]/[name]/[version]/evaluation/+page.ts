export const ssr = false;

import type { PageLoad } from "./$types";
import { DriftType } from "$lib/components/scouter/types";
import {
  getTimeRange,
  loadGenAIData,
  classifyError,
  type GenAIMonitoringPageData,
  type MonitoringErrorKind,
} from "$lib/components/scouter/dashboard/utils";
import { getDriftProfileExists } from "$lib/components/scouter/utils";
import { RegistryType } from "$lib/utils";
import type { PromptCard } from "$lib/components/card/card_interfaces/promptcard";
import type { AgentPromptEvalData } from "$lib/components/card/agent/evaluation/types";
import { dev } from "$app/environment";

export const load: PageLoad = async ({ parent, fetch }) => {
  const parentData = await parent();
  const {
    registryType,
    metadata,
    eval_profile,
    promptCardsWithEval,
    settings,
  } = parentData;

  const timeRange = getTimeRange();

  // ── Agent registry: load evaluation data for each prompt card ──
  if (registryType === RegistryType.Agent) {
    const agentPromptEvals: AgentPromptEvalData[] = await Promise.all(
      promptCardsWithEval.map(async (promptCard) => {
        const profile = promptCard.eval_profile!;

        if (!settings?.scouter_enabled) {
          if (dev) {
            const { getMockGenAIMonitoringPageData } =
              await import("$lib/components/scouter/evaluation/mockData");
            const monitoringData = getMockGenAIMonitoringPageData(
              promptCard.uid,
              registryType,
              timeRange,
            );
            return { promptCard, monitoringData };
          }
          const errorData: Extract<
            GenAIMonitoringPageData,
            { status: "error" }
          > = {
            status: "error",
            uid: promptCard.uid,
            registryType,
            selectedTimeRange: timeRange,
            errorMsg: "Scouter is not enabled.",
            errorKind: "not_enabled",
            profile,
          };
          return { promptCard, monitoringData: errorData };
        }

        const profileExists = await getDriftProfileExists(fetch, {
          name: promptCard.name,
          space: promptCard.space,
          version: promptCard.version,
          drift_type: DriftType.GenAI,
        });

        if (!profileExists) {
          const errorData: Extract<
            GenAIMonitoringPageData,
            { status: "error" }
          > = {
            status: "error",
            uid: promptCard.uid,
            registryType,
            selectedTimeRange: timeRange,
            errorMsg: "No evaluation profile found for this prompt.",
            errorKind: "not_found",
            profile,
          };
          return { promptCard, monitoringData: errorData };
        }

        try {
          const selectedData = await loadGenAIData(fetch, profile, timeRange);
          const monitoringData: Extract<
            GenAIMonitoringPageData,
            { status: "success" }
          > = {
            status: "success",
            profile,
            profileUri: "",
            selectedData,
            uid: promptCard.uid,
            registryType,
            selectedTimeRange: timeRange,
          };
          return { promptCard, monitoringData };
        } catch (err) {
          const message =
            err instanceof Error ? err.message : "Unknown monitoring error";
          console.error(
            `[Agent Eval Load Error] ${promptCard.name}: ${message}`,
            err,
          );
          const errorKind: MonitoringErrorKind = classifyError(err);
          const errorData: Extract<
            GenAIMonitoringPageData,
            { status: "error" }
          > = {
            status: "error",
            uid: promptCard.uid,
            registryType,
            selectedTimeRange: timeRange,
            errorMsg: message,
            errorKind,
            profile,
          };
          return { promptCard, monitoringData: errorData };
        }
      }),
    );

    return {
      registryType,
      metadata,
      driftType: DriftType.GenAI,
      // Agent-specific
      agentPromptEvals,
      // Not used for agents
      monitoringData: undefined,
    };
  }

  // ── Prompt registry: existing single-card evaluation flow ──
  if (!settings?.scouter_enabled) {
    if (dev) {
      const { getMockGenAIMonitoringPageData } =
        await import("$lib/components/scouter/evaluation/mockData");
      return {
        monitoringData: getMockGenAIMonitoringPageData(metadata.uid, registryType, timeRange),
        driftType: DriftType.GenAI,
        metadata,
        registryType,
        agentPromptEvals: undefined,
      };
    }
    const errorData: Extract<GenAIMonitoringPageData, { status: "error" }> = {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: "Scouter is not enabled.",
      errorKind: "not_found",
      profile: eval_profile,
    };
    return {
      monitoringData: errorData,
      driftType: DriftType.GenAI,
      metadata,
      registryType,
      agentPromptEvals: undefined,
    };
  }

  // check if profile exists before attempting to load data, if show not found screen
  let profileExists = await getDriftProfileExists(fetch, {
    name: metadata.name,
    space: metadata.space,
    version: metadata.version,
    drift_type: DriftType.GenAI,
  });

  if (!profileExists) {
    const errorData: Extract<GenAIMonitoringPageData, { status: "error" }> = {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: "No evaluation profile found for this card.",
      errorKind: "not_found",
      profile: eval_profile,
    };

    return {
      monitoringData: errorData,
      driftType: DriftType.GenAI,
      metadata,
      registryType,
      agentPromptEvals: undefined,
    };
  }

  try {
    const selectedData = await loadGenAIData(fetch, eval_profile, timeRange);

    const monitoringData: Extract<
      GenAIMonitoringPageData,
      { status: "success" }
    > = {
      status: "success",
      profile: eval_profile,
      profileUri: "",
      selectedData,
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
    };

    return {
      monitoringData,
      metadata,
      driftType: DriftType.GenAI,
      registryType,
      agentPromptEvals: undefined,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Unknown monitoring error";
    console.error(`[Monitoring Load Error]: ${message}`, err);

    const errorKind: MonitoringErrorKind = classifyError(err);

    const errorData: Extract<GenAIMonitoringPageData, { status: "error" }> = {
      status: "error",
      uid: metadata.uid,
      registryType,
      selectedTimeRange: timeRange,
      errorMsg: message,
      errorKind,
      profile: eval_profile,
    };

    return {
      monitoringData: errorData,
      driftType: DriftType.GenAI,
      metadata,
      registryType,
      agentPromptEvals: undefined,
    };
  }
};
