<script lang="ts">
  import type { TraceAssertion, SpanFilter } from '../task';
  import { Activity, Filter, Hash, Clock, Database } from 'lucide-svelte';

  let { assertion } = $props<{
    assertion: TraceAssertion;
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
    if ('SpanSequence' in assertion) {
      return {
        icon: Activity,
        label: 'Span Sequence',
        value: assertion.SpanSequence.span_names.join(' → '),
        bgColor: 'bg-tertiary-100',
        textColor: 'text-tertiary-900',
        borderColor: 'border-tertiary-800'
      };
    }

    if ('SpanSet' in assertion) {
      return {
        icon: Database,
        label: 'Span Set',
        value: assertion.SpanSet.span_names.join(', '),
        bgColor: 'bg-tertiary-100',
        textColor: 'text-tertiary-900',
        borderColor: 'border-tertiary-800'
      };
    }

    if ('SpanCount' in assertion) {
      return {
        icon: Hash,
        label: 'Span Count',
        value: formatSpanFilter(assertion.SpanCount.filter),
        bgColor: 'bg-primary-100',
        textColor: 'text-primary-900',
        borderColor: 'border-primary-800'
      };
    }

    if ('SpanExists' in assertion) {
      return {
        icon: Filter,
        label: 'Span Exists',
        value: formatSpanFilter(assertion.SpanExists.filter),
        bgColor: 'bg-primary-100',
        textColor: 'text-primary-900',
        borderColor: 'border-primary-800'
      };
    }

    if ('SpanAttribute' in assertion) {
      const filter = formatSpanFilter(assertion.SpanAttribute.filter);
      return {
        icon: Database,
        label: 'Span Attribute',
        value: `${assertion.SpanAttribute.attribute_key} (${filter})`,
        bgColor: 'bg-primary-100',
        textColor: 'text-primary-900',
        borderColor: 'border-primary-800'
      };
    }

    if ('SpanDuration' in assertion) {
      return {
        icon: Clock,
        label: 'Span Duration',
        value: formatSpanFilter(assertion.SpanDuration.filter),
        bgColor: 'bg-primary-100',
        textColor: 'text-primary-900',
        borderColor: 'border-primary-800'
      };
    }

    if ('SpanAggregation' in assertion) {
      const agg = assertion.SpanAggregation;
      const filter = formatSpanFilter(agg.filter);
      return {
        icon: Activity,
        label: 'Span Aggregation',
        value: `${agg.aggregation}(${agg.attribute_key}) [${filter}]`,
        bgColor: 'bg-secondary-100',
        textColor: 'text-secondary-900',
        borderColor: 'border-secondary-800'
      };
    }

    if ('TraceDuration' in assertion) {
      return {
        icon: Clock,
        label: 'Trace Duration',
        value: 'Total trace execution time',
        bgColor: 'bg-secondary-100',
        textColor: 'text-secondary-900',
        borderColor: 'border-secondary-800'
      };
    }

    if ('TraceSpanCount' in assertion) {
      return {
        icon: Hash,
        label: 'Trace Span Count',
        value: 'Total spans in trace',
        bgColor: 'bg-secondary-100',
        textColor: 'text-secondary-900',
        borderColor: 'border-secondary-800'
      };
    }

    if ('TraceErrorCount' in assertion) {
      return {
        icon: Activity,
        label: 'Trace Error Count',
        value: 'Total error spans',
        bgColor: 'bg-error-100',
        textColor: 'text-error-900',
        borderColor: 'border-error-800'
      };
    }

    if ('TraceServiceCount' in assertion) {
      return {
        icon: Database,
        label: 'Trace Service Count',
        value: 'Unique services',
        bgColor: 'bg-secondary-100',
        textColor: 'text-secondary-900',
        borderColor: 'border-secondary-800'
      };
    }

    if ('TraceMaxDepth' in assertion) {
      return {
        icon: Activity,
        label: 'Trace Max Depth',
        value: 'Maximum nesting level',
        bgColor: 'bg-secondary-100',
        textColor: 'text-secondary-900',
        borderColor: 'border-secondary-800'
      };
    }

    if ('TraceAttribute' in assertion) {
      return {
        icon: Database,
        label: 'Trace Attribute',
        value: assertion.TraceAttribute.attribute_key,
        bgColor: 'bg-secondary-100',
        textColor: 'text-secondary-900',
        borderColor: 'border-secondary-800'
      };
    }

    return {
      icon: Activity,
      label: 'Unknown',
      value: 'Unknown assertion type',
      bgColor: 'bg-surface-200',
      textColor: 'text-gray-900',
      borderColor: 'border-black'
    };
  });

  function formatSpanFilter(filter: SpanFilter): string {
    if ('ByName' in filter) return `name="${filter.ByName.name}"`;
    if ('ByNamePattern' in filter) return `pattern="${filter.ByNamePattern.pattern}"`;
    if ('WithAttribute' in filter) return `has ${filter.WithAttribute.key}`;
    if ('WithAttributeValue' in filter) return `${filter.WithAttributeValue.key}=${JSON.stringify(filter.WithAttributeValue.value)}`;
    if ('WithStatus' in filter) return `status="${filter.WithStatus.status}"`;
    if ('WithDuration' in filter) {
      const dur = filter.WithDuration;
      if (dur.min_ms !== undefined && dur.max_ms !== undefined) {
        return `${dur.min_ms}ms-${dur.max_ms}ms`;
      }
      if (dur.min_ms !== undefined) return `≥${dur.min_ms}ms`;
      if (dur.max_ms !== undefined) return `≤${dur.max_ms}ms`;
    }
    if ('Sequence' in filter) return `sequence: ${filter.Sequence.names.join(' → ')}`;
    if ('And' in filter) return `AND(${filter.And.filters.length} filters)`;
    if ('Or' in filter) return `OR(${filter.Or.filters.length} filters)`;
    return 'unknown filter';
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