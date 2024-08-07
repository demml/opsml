<!-- src/lib/components/Input.svelte -->
<script>
    export let label = '';
    export let type = 'text';
    export let placeholder = '';
    export let value = '';
    export let required = false;
  </script>
  
  <div class="input-group">
    <label for={label}>{label}</label>
    <input
      type=text
      {placeholder}
      {required}
      id={label}
      bind:value
    />
  </div>
  
  <style>
    .input-group {
      margin-bottom: 1rem;
    }
  
    label {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
      color: #374151;
      margin-bottom: 0.5rem;
    }
  
    input {
      width: 100%;
      padding: 0.75rem 1rem;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      font-size: 1rem;
      color: #111827;
      transition: border-color 0.15s ease-in-out;
    }
  
    input:focus {
      outline: none;
      border-color: #4f46e5;
      box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
  </style>