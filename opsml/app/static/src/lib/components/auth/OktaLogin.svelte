<script>
    import { onMount } from 'svelte';
    import { OktaSignIn } from '@okta/okta-signin-widget';
    import { get } from "svelte/store";
    import { authStore } from '$lib/scripts/auth/newAuthStore';
  
    let widgetContainer;
  
    onMount(() => {
      const auth = get(authStore);
      const signIn = new OktaSignIn({
        baseUrl: auth.oktaConfig?.issuer,
        clientId: auth.oktaConfig?.clientId,
        redirectUri: auth.oktaConfig?.redirectUri,
        authParams: {
          issuer: auth.oktaConfig?.issuer + '/oauth2/default',
          responseType: ['token', 'id_token'],
          display: 'page',
          scopes: ['openid', 'profile', 'email']
        }
      });
  
      signIn.renderEl(
        { el: widgetContainer },
        function success(res) {
          if (res.status === 'SUCCESS') {
            res.session.setCookieAndRedirect('http://localhost:8090');
          }
        },
        function error(err) {
          console.error(err);
        }
      );
    });
  </script>
  
  <div bind:this={widgetContainer}></div>