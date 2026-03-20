<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  const theme = localStorage.getItem('profile_theme') || 'midnight'
  document.documentElement.setAttribute('data-theme', theme)
})
</script>

<style>
/* Global styles are in assets/styles.css */
</style>
