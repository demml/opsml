<script lang="ts">
  import type { AgentAssertion } from '../task';
  import { Activity, Bot, Hash, MessageSquareText, Wrench } from 'lucide-svelte';

  let { assertion } = $props<{
    assertion: AgentAssertion;
  }>();

  interface AssertionDisplay {
    icon: typeof Activity;
    label: string;
    value: string;
    bgColor: string;
    textColor: string;
    borderColor: string;
  }

  const display = $derived.by((): AssertionDisplay => {
    if ('ToolCalled' in assertion) {
      return buildToolDisplay('Tool Called', assertion.ToolCalled.name);
    }

    if ('ToolNotCalled' in assertion) {
      return buildToolDisplay('Tool Not Called', assertion.ToolNotCalled.name);
    }

    if ('ToolCalledWithArgs' in assertion) {
      const { name, arguments: args } = assertion.ToolCalledWithArgs;
      return buildToolDisplay('Tool Args Match', `${name} ${JSON.stringify(args)}`);
    }

    if ('ToolCallSequence' in assertion) {
      return buildToolDisplay(
        'Tool Sequence',
        assertion.ToolCallSequence.names.join(' → '),
      );
    }

    if ('ToolCallCount' in assertion) {
      return buildMetricDisplay(
        'Tool Call Count',
        assertion.ToolCallCount.name ?? 'all tools',
      );
    }

    if ('ToolArgument' in assertion) {
      const { name, argument_key } = assertion.ToolArgument;
      return buildToolDisplay('Tool Argument', `${name}.${argument_key}`);
    }

    if ('ToolResult' in assertion) {
      return buildToolDisplay('Tool Result', assertion.ToolResult.name);
    }

    if ('ResponseContent' in assertion) {
      return buildResponseDisplay('Response Content', 'response text');
    }

    if ('ResponseModel' in assertion) {
      return buildResponseDisplay('Response Model', 'model name');
    }

    if ('ResponseFinishReason' in assertion) {
      return buildResponseDisplay('Finish Reason', 'completion reason');
    }

    if ('ResponseInputTokens' in assertion) {
      return buildMetricDisplay('Input Tokens', 'prompt token count');
    }

    if ('ResponseOutputTokens' in assertion) {
      return buildMetricDisplay('Output Tokens', 'completion token count');
    }

    if ('ResponseTotalTokens' in assertion) {
      return buildMetricDisplay('Total Tokens', 'total token count');
    }

    if ('ResponseField' in assertion) {
      return buildResponseDisplay('Response Field', assertion.ResponseField.path);
    }

    return {
      icon: Bot,
      label: 'Unknown',
      value: 'Unknown agent assertion type',
      bgColor: 'bg-surface-200',
      textColor: 'text-black',
      borderColor: 'border-black',
    };
  });

  function buildToolDisplay(label: string, value: string): AssertionDisplay {
    return {
      icon: Wrench,
      label,
      value,
      bgColor: 'bg-secondary-100',
      textColor: 'text-secondary-900',
      borderColor: 'border-secondary-800',
    };
  }

  function buildResponseDisplay(label: string, value: string): AssertionDisplay {
    return {
      icon: MessageSquareText,
      label,
      value,
      bgColor: 'bg-primary-100',
      textColor: 'text-primary-900',
      borderColor: 'border-primary-800',
    };
  }

  function buildMetricDisplay(label: string, value: string): AssertionDisplay {
    return {
      icon: Hash,
      label,
      value,
      bgColor: 'bg-tertiary-100',
      textColor: 'text-tertiary-900',
      borderColor: 'border-tertiary-800',
    };
  }

  const IconComponent = $derived(display.icon);
</script>

<div class="inline-flex items-stretch overflow-hidden rounded-lg border-2 {display.borderColor} w-fit shadow-small">
  <div class="border-r-2 {display.borderColor} px-2 py-1 {display.bgColor} {display.textColor} flex items-center gap-1.5">
    <IconComponent class="w-3.5 h-3.5" />
    <span class="text-xs font-bold italic">{display.label}</span>
  </div>
  <div class="px-2 py-1 bg-surface-50 {display.textColor} flex items-center text-xs max-w-xs truncate">
    {display.value}
  </div>
</div>
