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
	<title>FITstagram</title>
</head>
<div class="app pt-10">
  
   <main>
     <!-- <div class="flex justify-center items-center h-screen">
       <h1 class="text-3xl font-bold">Hupsík dupsík, to je tvoje chyba, ne naše (kecám Nejde backend :(, zkus to za chvilku juu?))</h1>
     </div> -->
     <div class="bg-black p-10 rounded-lg text-center ">
      <h1 class="text-2xl text-blue-700">Hello World</h1>
      <p class="text-gray-500">This is a SvelteKit project</p>
  </div>
  
  <slot></slot>
</div>

<style>
</style>
