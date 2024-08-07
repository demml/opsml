<!-- src/lib/components/Button.svelte -->
<script lang="ts">
    export let type = 'button';
</script>
  
  <button type=button>
    <slot></slot>
  </button>
  
  <style>
    button {
      width: 100%;
      background-color: #4f46e5;
      color: white;
      font-weight: 600;
      padding: 0.75rem 1rem;
      border: none;
      border-radius: 0.375rem;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.15s ease-in-out;
    }
  
    button:hover {
      background-color: #4338ca;
    }
  
    button:focus {
      outline: none;
      box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.5);
    }
  </style>