<script lang="ts">
 
  let { 
     key, 
     value
   } = $props<{
      key: string;
      value: string;
   }>();

</script>

<div class="inline-flex items-stretch overflow-hidden rounded-lg border-2 border-primary-700 w-fit">
  <div class="border-r border-primary-70 px-2 text-primary-950 bg-primary-100 italic flex items-center justify-center">{key}</div> 
    <div class="px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 text-primary-950 flex items-center justify-center">
      {value}
    </div>
</div>