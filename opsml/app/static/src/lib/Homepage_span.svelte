<script lang="ts">

  export let header: string;

</script>


<div class="relative col-span-1 flex flex-col items-stretch text-center">
  <h2 class="mb-3 flex items-center justify-center text-lg font-bold 2xl:mb-4 2xl:text-xl text-slate-100">
    {header}
  </h2>
  <div class="relative mb-3 flex flex-col bg-slate-100/50 items-center gap-2.5 rounded-xl shadow-primary-300 shadow-md p-3 backdrop-blur-lg sm:mb-7">
    <slot></slot>
  </div>
</div>