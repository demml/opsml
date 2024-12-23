

<script lang="ts">
  export let title: string;
  export let value: string | number;
  export let colspan: string | undefined;
</script>


<div class="inline-flex items-center overflow-hidden rounded-lg border border-darkpurple text-sm w-fit h-fit bg-primary-50 {colspan}">
  <div class="px-2 text-darkpurple bg-primary-50 italic">{title}</div> 
  <div class="flex px-1.5 bg-surface-50 border-l border-darkpurple hover:bg-gradient-to-b from-surface-50 to-surface-100 text-darkpurple">
    {value}
  </div>
</div>



