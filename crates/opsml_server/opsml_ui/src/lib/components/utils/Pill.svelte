<script lang="ts">

  let {
     key,
     value,
     textSize = "text-base",
     borderColor = "border-primary-700",
     textColor = "text-primary-950",
     bgColor = "bg-primary-100"
   } = $props<{
      key: string;
      value: string;
      textSize: string;
      borderColor?: string;
      textColor?: string;
      bgColor?: string;
   }>();

</script>

<div class="inline-flex items-stretch overflow-hidden rounded-lg border-2 {borderColor} w-fit">
  <div class="border-r border-primary-70 px-2 {textColor} {bgColor} italic flex items-center justify-center {textSize}">{key}</div> 
    <div class="px-1.5 bg-surface-50 border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100 {textColor} flex items-center justify-center {textSize}">
      {value}
    </div>
</div>