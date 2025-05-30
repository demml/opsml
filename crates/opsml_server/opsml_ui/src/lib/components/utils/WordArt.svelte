<script lang="ts">
  let { text} = $props<{
    text: string;
  }>();
</script>

<div class="rounded-base border-primary-500 border-2 bg-surface-50 pb-4 px-4 items-center">
    <div class="font-bold text-primary-800 text-xl">{text}</div>
</div>