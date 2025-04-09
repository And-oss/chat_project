<template>
  <div id="app" class="h-screen flex flex-col">
    <main class="flex-1 flex">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts"></script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #36393f;
  color: white;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
</style>