<script lang="ts">
  import { goto } from "$app/navigation";
  import logo from "$lib/images/opsml-logo-medium.webp";
  import { UiPaths } from "$lib/components/api/routes";
  import { userStore } from "$lib/components/user/user.svelte";
  import CodeModal from "$lib/components/card/CodeModal.svelte";


  async function gotoLogin() {
    goto(UiPaths.LOGIN);
  }

  let copied = $state(false);
  let timeoutId: number = 0;
  let codes = $state(userStore.recovery_codes);
  let usageCode = `export OPSML_USERNAME={{username}}
export OPSML_PASSWORD={{password}}
`;

  function formatExtraBody(body: any): string {
      return JSON.stringify(body, null, 2);
  }

  async function copyToClipboard() {
      try {
        await navigator.clipboard.writeText(formatExtraBody(userStore.recovery_codes));
        copied = true;
        
        // Reset the copied state after 2 seconds
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          copied = false;
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text:', err);
      }
    }


</script>

<div class="pt-20 border-gray-100 col-span-full flex-1 pb-16 md:pb-0 items-center">
  

  <div class="z-10 mx-auto rounded-2xl bg-surface-50 border-black border-2 shadow p-4 md:w-md md:px-5">

    <img alt="OpsML logo" class="mx-auto -mt-12 mb-3 w-20" src={logo}>
    <h1 class="pt-1 text-center text-lg font-bold text-primary-800">Welcome to OpsML!</h1>

    <div class="mb-8 grid grid-cols-1 gap-3">
      <div>
        <p class="text-left text-primary-500 text-smd">You have successfully registered as a new user!</p>
        <p class="text-left text-primary-500 text-smd">Your username is: <span class="font-bold">{userStore.username}</span></p>


        <div class="flex flex-row pb-2 justify-between items-center pt-2">
          <h2 class="text-lg font-bold text-black my-auto">Usage</h2>
            <CodeModal 
            code={usageCode} 
            language="bash" 
            message="Set the following environment variables to use your profile"
            display="SDK Usage"
          />
        </div>

        
        <div class="flex flex-row pb-3 justify-between items-center">
          <h2 class="text-lg font-bold text-black my-auto">Recovery Codes</h2>
          <button class="btn text-smd bg-primary-500 text-black shadow shadow-hover border-black border-2 my-auto" onclick={copyToClipboard} disabled={copied}>
            {copied ? 'Copied 👍' : 'Copy'}
          </button>
        </div>

        <p class="mb-1 text-black text-left overflow-x-scroll text-smd">These codes are used to recover your account in case you lose access to your password. Please save them securely.</p>

        
        <div class="flex flex-col gap-2">
          <div>
            <div class="rounded-lg border-2 border-black overflow-y-scroll bg-slate-100 max-h-[600px]">
              <ul class="list-disc pl-6 py-2 text-sm">
                {#each codes as code}
                  <li class="text-black">{code}</li>
                {/each}
              </ul>
            </div>
          </div>
        </div>
      </div>

      <p class="text-center text-black text-smd">When you are ready, click the button below to navigate back to the login screen</p>

    </div>

    <div class="grid justify-items-center">
      <button type="submit" class="btn text-smd bg-primary-500 rounded-lg md:w-72 justify-self-center text-black mb-2 ring-offset-white  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 border-black border-2 border-border shadow transition-all hover:translate-x-[4px] hover:translate-y-[4px] hover:shadow-none" onclick={gotoLogin}>
        Login
      </button>

    </div>
  </div>
</div>