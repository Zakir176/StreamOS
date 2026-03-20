<template>
  <div class="settings-container">
    <nav class="netflix-nav glass">
      <div class="nav-left">
        <h1 class="logo" @click="$router.push('/library')">Stream<span>OS</span></h1>
      </div>
      <div class="nav-right">
        <button class="done-btn glass" @click="$router.push('/library')">Done</button>
      </div>
    </nav>

    <main class="settings-content">
      <h1 class="page-title">Manage Profiles</h1>
      
      <div class="profiles-grid">
        <div v-for="profile in profiles" :key="profile.id" class="profile-card" @click="selectProfile(profile)">
          <div class="profile-avatar-wrapper glass">
            <img :src="profile.avatar_url" :alt="profile.username" class="avatar-img" />
            <div class="edit-overlay" @click.stop="editProfile(profile)">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M18.5 2.5C18.8978 2.10217 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10217 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10217 21.5 5.5L11 16L7 17L8 13L18.5 2.5Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
          <p class="role-badge" :class="profile.age_category">{{ profile.age_category }}</p>
          <p class="profile-name">{{ profile.username }}</p>
          <button class="delete-btn" @click.stop="confirmDelete(profile)">✕</button>
        </div>

        <div class="add-profile-card glass" @click="showAddModal = true">
          <div class="add-icon">+</div>
          <p>Add Profile</p>
        </div>
      </div>

      <div class="system-settings-section glass">
        <h2 class="section-title">Library Settings</h2>
        <div class="setting-item">
          <label>Media Library Path</label>
          <div class="path-input-group">
            <input v-model="mediaDir" placeholder="e.g. C:\Movies" class="settings-input glass" />
            <button @click="saveMediaDir" class="save-btn small">Save Path</button>
          </div>
          <p class="setting-hint">This is where StreamOS will look for video files.</p>
        </div>
        
        <div class="setting-actions">
          <button @click="triggerScan" :disabled="scanning" class="scan-btn glass">
            {{ scanning ? 'Scanning...' : 'Scan Library Now' }}
          </button>
        </div>
      </div>
    </main>

    <!-- Modal for Adding Profile -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal glass">
        <h2 class="modal-title">Create Profile</h2>
        <div class="input-group">
          <label>Username</label>
          <input v-model="newProfile.username" placeholder="Enter name" class="modal-input glass" />
        </div>
        <div class="input-group">
          <label>Age Category</label>
          <select v-model="newProfile.age_category" class="modal-select glass">
            <option value="child">Child (Kids Safe)</option>
            <option value="teen">Teen (Mild content)</option>
            <option value="adult">Adult (All Access)</option>
          </select>
        </div>
        <div class="input-group">
          <label>UI Theme</label>
          <div class="theme-selector">
            <button 
              class="theme-btn midnight" 
              :class="{ active: newProfile.theme === 'midnight' }"
              @click="newProfile.theme = 'midnight'"
            >Midnight</button>
            <button 
              class="theme-btn cinematic" 
              :class="{ active: newProfile.theme === 'cinematic' }"
              @click="newProfile.theme = 'cinematic'"
            >Cinematic</button>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="saveProfile" class="save-btn">Create</button>
          <button @click="showAddModal = false" class="cancel-btn glass">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Modal for Editing Profile -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal glass">
        <h2 class="modal-title">Edit Profile</h2>
        
        <div class="edit-avatar-section">
          <div class="profile-avatar-wrapper glass small-avatar">
            <img :src="editingProfile.avatar_url" class="avatar-img" />
          </div>
          <button @click="randomizeAvatar" class="random-btn glass">Change Avatar</button>
        </div>

        <div class="input-group">
          <label>Username</label>
          <input v-model="editingProfile.username" placeholder="Enter name" class="modal-input glass" />
        </div>
        
        <div class="input-group">
          <label>UI Theme</label>
          <div class="theme-selector">
            <button 
              class="theme-btn midnight" 
              :class="{ active: editingProfile.theme === 'midnight' }"
              @click="editingProfile.theme = 'midnight'"
            >Midnight</button>
            <button 
              class="theme-btn cinematic" 
              :class="{ active: editingProfile.theme === 'cinematic' }"
              @click="editingProfile.theme = 'cinematic'"
            >Cinematic</button>
          </div>
        </div>

        <div class="input-group">
          <label>Age Category</label>
          <select v-model="editingProfile.age_category" class="modal-select glass">
            <option value="child">Child (Kids Safe)</option>
            <option value="teen">Teen (Mild content)</option>
            <option value="adult">Adult (All Access)</option>
          </select>
        </div>

        <div class="modal-actions">
          <button @click="updateProfile" class="save-btn">Save Changes</button>
          <button @click="showEditModal = false" class="cancel-btn glass">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const profiles = ref([])
const showAddModal = ref(false)
const newProfile = ref({ username: '', age_category: 'adult', theme: 'midnight' })
const mediaDir = ref('')
const scanning = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE

const fetchSettings = async () => {
  try {
    const res = await fetch(`${API_BASE}/settings/media_dir`)
    if (res.ok) {
      const data = await res.json()
      mediaDir.value = data.value
    }
  } catch (err) {
    console.error('Fetch settings failed:', err)
  }
}

const saveMediaDir = async () => {
  try {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: 'media_dir', value: mediaDir.value })
    })
    if (res.ok) {
      alert('Media path saved successfully!')
    }
  } catch (err) {
    console.error('Save media path failed:', err)
    alert('Failed to save media path.')
  }
}

const triggerScan = async () => {
  try {
    scanning.value = true
    const res = await fetch(`${API_BASE}/scan`, { method: 'POST' })
    if (res.ok) {
      const data = await res.json()
      alert(data.message || 'Library scan completed!')
    }
  } catch (err) {
    console.error('Scan failed:', err)
    alert('Failed to trigger scan.')
  } finally {
    scanning.value = false
  }
}

const editingProfile = ref(null)
const showEditModal = ref(false)

const selectProfile = (profile) => {
  localStorage.setItem('profile_id', profile.id)
  localStorage.setItem('profile_name', profile.username)
  localStorage.setItem('profile_category', profile.age_category)
  localStorage.setItem('profile_category', profile.age_category)
  const theme = profile.theme || 'midnight'
  localStorage.setItem('profile_theme', theme)
  document.documentElement.setAttribute('data-theme', theme)
  router.push('/library')
}

const editProfile = (profile) => {
  editingProfile.value = { ...profile }
  showEditModal.value = true
}

const randomizeAvatar = () => {
  const seeds = ['Felix', 'Molly', 'Simba', 'Lola', 'Buster', 'Pepper', 'Willow', 'Rex', 'Shadow', 'Luna']
  const randomSeed = seeds[Math.floor(Math.random() * seeds.length)]
  const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${randomSeed}&backgroundColor=b6e3f4`
  
  if (editingProfile.value) {
    editingProfile.value.avatar_url = avatarUrl
  } else {
    newProfile.value.avatar_url = avatarUrl
  }
}

const updateProfile = async () => {
  if (!editingProfile.value.username) return
  
  try {
    const res = await fetch(`${API_BASE}/profiles/${editingProfile.value.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editingProfile.value)
    })
    
    if (res.ok) {
        showEditModal.value = false
        // Update local storage if currently active profile updated
        if (localStorage.getItem('profile_id') == editingProfile.value.id) {
            localStorage.setItem('profile_name', editingProfile.value.username)
            localStorage.setItem('profile_theme', editingProfile.value.theme)
            document.documentElement.setAttribute('data-theme', editingProfile.value.theme)
        }
        await fetchProfiles()
    }
  } catch (err) {
    console.error('Update profile failed:', err)
  }
}

const fetchProfiles = async () => {
  try {
    const res = await fetch(`${API_BASE}/profiles`)
    profiles.value = await res.json()
  } catch (err) {
    console.error('Fetch profiles failed:', err)
  }
}

const saveProfile = async () => {
  if (!newProfile.value.username) return
  
  const seeds = ['Felix', 'Molly', 'Simba', 'Lola', 'Buster', 'Pepper']
  const randomSeed = seeds[Math.floor(Math.random() * seeds.length)]
  const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${randomSeed}&backgroundColor=b6e3f4`

  try {
    await fetch(`${API_BASE}/profile/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...newProfile.value, avatar_url: avatarUrl })
    })
    
    newProfile.value = { username: '', age_category: 'adult', theme: 'midnight' }
    showAddModal.value = false
    await fetchProfiles()
  } catch (err) {
    console.error('Create profile failed:', err)
  }
}

const confirmDelete = async (profile) => {
  if (confirm(`Delete profile "${profile.username}"?`)) {
    try {
      await fetch(`${API_BASE}/profiles/${profile.id}`, { method: 'DELETE' })
      await fetchProfiles()
    } catch (err) {
      console.error('Delete profile failed:', err)
    }
  }
}

onMounted(() => {
  fetchProfiles()
  fetchSettings()
})
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: var(--bg-liquid);
  color: #fff;
}

.netflix-nav {
  position: fixed;
  top: 0;
  width: 100%;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4vw;
  z-index: 1000;
  box-sizing: border-box;
}

.settings-content {
  padding: 120px 6vw 5vw;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 3rem;
  text-align: center;
}

.profiles-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 3rem;
  justify-content: center;
}

.profile-card {
  position: relative;
  text-align: center;
  width: 180px;
  transition: transform 0.3s;
}

.profile-avatar-wrapper {
  width: 180px;
  height: 180px;
  margin-bottom: 15px;
  transition: transform 0.3s, box-shadow 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-img {
  width: 85%;
  height: 85%;
  object-fit: contain;
}

.profile-card:hover .profile-avatar-wrapper {
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--neon-cyan);
  border-color: var(--neon-cyan);
}

.edit-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
  border-radius: var(--radius-main);
}

.profile-card:hover .edit-overlay {
  opacity: 1;
}

.profile-name {
  font-size: 1.4rem;
  font-weight: 600;
  margin: 10px 0;
}

.role-badge {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 4px 12px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 5px;
}

.role-badge.child { background: #4CAF50; color: #fff; }
.role-badge.teen { background: #FF9800; color: #fff; }
.role-badge.adult { background: var(--netflix-red); color: #fff; }

.delete-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: var(--netflix-red);
  border: none;
  color: #fff;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.2s;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
  z-index: 20;
}

.profile-card:hover .delete-btn {
  opacity: 1;
}

.add-profile-card {
  width: 180px;
  height: 180px;
  border: 2px dashed rgba(255,255,255,0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255,255,255,0.4);
  transition: all 0.3s;
}

.add-profile-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.system-settings-section {
  margin-top: 5rem;
  padding: 2.5rem;
  border-radius: 1rem;
  text-align: left;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 2rem;
  color: var(--neon-cyan);
}

.setting-item {
  margin-bottom: 2rem;
}

.setting-item label {
  display: block;
  margin-bottom: 0.8rem;
  font-weight: 600;
  color: #ccc;
}

.path-input-group {
  display: flex;
  gap: 1rem;
}

.settings-input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.5rem;
  color: white;
  font-size: 1rem;
}

.save-btn.small {
  padding: 0.8rem 1.5rem;
  font-size: 0.9rem;
}

.setting-hint {
  margin-top: 0.5rem;
  font-size: 0.85rem;
  color: #888;
}

.scan-btn {
  width: 100%;
  padding: 1.2rem;
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
  border: 2px solid var(--neon-cyan);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(0, 243, 255, 0.1);
}

.scan-btn:hover:not(:disabled) {
  background: var(--neon-cyan);
  color: #000;
  box-shadow: 0 0 20px rgba(0, 243, 255, 0.4);
}

.scan-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.done-btn {
  background: var(--glass-bg);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.2);
  padding: 10px 30px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.done-btn:hover {
  background: #fff;
  color: #000;
}

/* Modals */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(15px);
}

.modal {
  padding: 50px;
  width: 450px;
  border: 1px solid rgba(255,255,255,0.1);
}

.modal-title {
  font-size: 2.5rem;
  margin-bottom: 30px;
  text-align: center;
}

.input-group {
  margin-bottom: 25px;
}

.input-group label {
  display: block;
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.modal-input, .modal-select {
  width: 100%;
  padding: 15px;
  font-size: 1rem;
  color: #fff;
  transition: border-color 0.3s;
}

.modal-input:focus, .modal-select:focus {
  border-color: var(--neon-cyan);
  outline: none;
}

.modal-actions {
  display: flex;
  gap: 15px;
  margin-top: 40px;
}

.save-btn {
  background: var(--netflix-red);
  color: #fff;
  border: none;
  padding: 15px 30px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  flex: 2;
  border-radius: 4px;
  box-shadow: 0 0 15px var(--netflix-red);
  transition: transform 0.2s;
}

.save-btn:hover {
  transform: translateY(-2px);
}

.cancel-btn {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 15px 20px;
  cursor: pointer;
  flex: 1;
}

.edit-avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.small-avatar {
  width: 100px !important;
  height: 100px !important;
  margin-bottom: 0 !important;
}

.random-btn {
  padding: 8px 16px;
  font-size: 0.9rem;
  border-radius: 20px;
  cursor: pointer;
  border: 1px solid var(--neon-cyan);
  color: var(--neon-cyan);
}

.theme-selector {
  display: flex;
  gap: 10px;
}

.theme-btn {
  flex: 1;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.theme-btn.active {
  border-color: var(--neon-cyan);
  background: rgba(0, 255, 255, 0.1);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
}

.theme-btn.midnight:hover { background: #1a1a1a; }
.theme-btn.cinematic:hover { background: #0f172a; }

@media (max-width: 768px) {
  .page-title { font-size: 2.5rem; }
  .profile-card, .profile-avatar-wrapper, .add-profile-card { width: 140px; height: 140px; }
  .modal { width: 90%; padding: 30px; }
}
</style>
