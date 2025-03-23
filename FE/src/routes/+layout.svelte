<script lang="ts">
  import "../app.css"
  import api from "$lib/axios.config"
  import { onDestroy, onMount } from "svelte"
  import { page } from '$app/stores';
  import { goto } from "$app/navigation"
  let serverStarted = false
  let serverError = false
  let intervalId: number

  

</script>
<head>
	<title>Mapovač 3000</title>
</head>
<div class="app pt-10">
  
   <main>
  
  <slot></slot>
</div>

<style>
</style>
