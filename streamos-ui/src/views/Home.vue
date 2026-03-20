<template>
  <div class="home-container">
    <div class="profile-gate">
      <h1 class="logo-title">Stream<span>OS</span></h1>
      <h2 class="gate-subtitle">Who's watching?</h2>
      
      <div class="profiles-list">
        <div v-for="profile in profiles" :key="profile.id" class="profile-item" @click="selectProfile(profile)">
          <div class="profile-icon-wrapper glass">
            <img :src="profile.avatar_url" :alt="profile.username" class="avatar-img" />
          </div>
          <span class="profile-name">{{ profile.username }}</span>
        </div>

        <div class="profile-item add-profile" @click="$router.push('/settings')">
          <div class="profile-icon-wrapper glass add-btn">
            <span class="plus">+</span>
          </div>
          <span class="profile-name">Add Profile</span>
        </div>
      </div>
      
      <button class="manage-profiles" @click="$router.push('/settings')">Manage Profiles</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const profiles = ref([])
const API_BASE = import.meta.env.VITE_API_BASE

const fetchProfiles = async () => {
  try {
    const res = await fetch(`${API_BASE}/profiles`)
    profiles.value = await res.json()
  } catch (err) {
    console.error('Failed to fetch profiles:', err)
  }
}

onMounted(fetchProfiles)

const selectProfile = (profile) => {
  localStorage.setItem('profile_id', profile.id)
  localStorage.setItem('profile_name', profile.username)
  localStorage.setItem('profile_category', profile.age_category)
  router.push('/library')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-liquid);
}

.profile-gate {
  text-align: center;
  max-width: 90%;
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.logo-title {
  font-size: 5rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 0;
  text-shadow: 0 0 20px rgba(255,255,255,0.2);
}

.logo-title span {
  color: var(--neon-cyan);
}

.gate-subtitle {
  font-size: 2.5rem;
  color: #fff;
  margin-bottom: 50px;
  font-weight: 300;
  opacity: 0.9;
}

.profiles-list {
  display: flex;
  justify-content: center;
  gap: 4vw;
  margin-bottom: 80px;
}

.profile-item {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 160px;
}

.profile-icon-wrapper {
  width: 140px;
  height: 140px;
  margin-bottom: 15px;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.avatar-img {
  width: 90%;
  height: 90%;
  object-fit: contain;
  filter: drop-shadow(0 5px 15px rgba(0,0,0,0.5));
}

.profile-item:hover .profile-icon-wrapper {
  transform: scale(1.1);
  box-shadow: 0 0 20px var(--neon-cyan);
  border-color: var(--neon-cyan);
}

.add-btn {
  border: 2px dashed rgba(255,255,255,0.2);
}

.plus {
  font-size: 4rem;
  color: rgba(255,255,255,0.3);
  font-weight: 200;
}

.profile-item:hover .plus {
  color: var(--neon-cyan);
}

.profile-name {
  font-size: 1.2rem;
  color: var(--text-muted);
  font-weight: 500;
  transition: color 0.3s;
}

.profile-item:hover .profile-name {
  color: #fff;
}

.manage-profiles {
  background: var(--glass-bg);
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.6);
  padding: 12px 40px;
  font-size: 1rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.manage-profiles:hover {
  background: rgba(255,255,255,0.1);
  border-color: #fff;
  color: #fff;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .logo-title { font-size: 3rem; }
  .gate-subtitle { font-size: 1.5rem; }
  .profile-icon-wrapper { width: 100px; height: 100px; }
  .profiles-list { flex-wrap: wrap; gap: 20px; }
}
</style>
