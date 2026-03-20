<template>
  <div class="account-settings-container">
    <nav class="settings-nav">
      <h1 class="nav-logo" @click="$router.push('/library')">StreamOS</h1>
      <button class="back-btn glass" @click="$router.push('/library')">Back to Library</button>
    </nav>

    <div class="settings-content-wrapper">
      <div class="settings-card glass">
        <h2 class="settings-title">Account & System Settings</h2>
        
        <div class="setting-section">
          <h3 class="section-subtitle">Media Library</h3>
          <p class="section-desc">Specify the root directory where your media is stored. StreamOS will look for 'kids', 'teen', and 'adult' folders inside.</p>
          
          <div class="input-group">
            <input 
              v-model="mediaDir" 
              type="text" 
              placeholder="e.g. D:\Movies"
              class="settings-input"
            />
            <button @click="updateMediaDir" class="action-btn primary">Update Path</button>
          </div>
        </div>

        <div class="divider"></div>

        <div class="setting-section flex-between">
          <div>
            <h3 class="section-subtitle">Offline Mode (Zero Data)</h3>
            <p class="section-desc">Disable all external API calls. StreamOS will only use local assets and NFO files.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="offlineMode" @change="saveOfflineMode">
            <span class="slider round"></span>
          </label>
        </div>

        <div class="divider"></div>

        <div class="setting-section">
          <h3 class="section-subtitle">System Metadata (TMDB)</h3>
          <p class="section-desc">Add your TMDB API Key to fetch real posters and synopses.</p>
          
          <div class="input-group">
            <input 
              v-model="tmdbKey" 
              type="password" 
              placeholder="Paste TMDB API Key here"
              class="settings-input"
            />
            <button @click="saveTmdbKey" class="action-btn primary">Save Key</button>
          </div>
        </div>

        <div class="divider"></div>

        <div class="divider"></div>

        <div class="setting-section">
          <h3 class="section-subtitle">Scanner Actions</h3>
          <p class="section-desc">Manual library re-scan or metadata refresh from TMDB.</p>
          <div class="button-group">
            <button 
              @click="triggerScan" 
              :disabled="scanning" 
              class="action-btn secondary"
            >
              <span v-if="!scanning">Re-scan Disk</span>
              <span v-else>Scanning Disk...</span>
            </button>

            <button 
              @click="triggerScrape" 
              :disabled="scraping || offlineMode" 
              class="action-btn neon"
              :title="offlineMode ? 'Disabled in Offline Mode' : ''"
            >
              <span v-if="!scraping">Fetch TMDB Metadata</span>
              <span v-else>Scraping TMDB...</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const mediaDir = ref('')
const tmdbKey = ref('')
const scanning = ref(false)
const scraping = ref(false)
const offlineMode = ref(false)
const API_BASE = import.meta.env.VITE_API_BASE

const fetchSettings = async () => {
  try {
    const res = await fetch(`${API_BASE}/settings`)
    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data)) {
        const dirSetting = data.find(s => s.key === 'media_dir')
        if (dirSetting) mediaDir.value = dirSetting.value
        
        const keySetting = data.find(s => s.key === 'tmdb_api_key')
        if (keySetting) tmdbKey.value = keySetting.value

        const offlineSetting = data.find(s => s.key === 'offline_mode')
        if (offlineSetting) offlineMode.value = offlineSetting.value === 'true'
      }
    }
  } catch (err) {
    console.error('Failed to fetch settings:', err)
  }
}

const saveTmdbKey = async () => {
    try {
        const res = await fetch(`${API_BASE}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'tmdb_api_key', value: tmdbKey.value })
        })
        if (res.ok) {
            alert('TMDB API Key saved!')
        }
    } catch (err) {
        alert('Failed to save TMDB key')
    }
}

const saveOfflineMode = async () => {
    try {
        await fetch(`${API_BASE}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'offline_mode', value: offlineMode.value.toString() })
        })
    } catch (err) {
        console.error('Failed to save offline mode:', err)
    }
}

const triggerScrape = async () => {
    if (!tmdbKey.value) {
        alert('Please save a TMDB API key first.')
        return
    }
    scraping.value = true
    try {
        const res = await fetch(`${API_BASE}/scrape`, { method: 'POST' })
        const data = await res.json()
        if (res.ok) {
            alert(data.message || 'Metadata fetch completed!')
        } else {
            alert(data.detail || 'Metadata fetch failed')
        }
    } catch (err) {
        alert('Failed to trigger metadata scrape')
    } finally {
        scraping.value = false
    }
}

const updateMediaDir = async () => {
  try {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: 'media_dir', value: mediaDir.value })
    })
    if (res.ok) {
      alert('Media directory updated successfully!')
    }
  } catch (err) {
    alert('Failed to update media directory')
  }
}

const triggerScan = async () => {
  scanning.value = true
  try {
    const res = await fetch(`${API_BASE}/scan`, { method: 'POST' })
    if (res.ok) {
      const data = await res.json()
      alert(data.message || 'Scan triggered! The library will update shortly.')
    }
  } catch (err) {
    alert('Failed to trigger scan')
  } finally {
    scanning.value = false
  }
}

onMounted(fetchSettings)
</script>

<style scoped>
.account-settings-container {
  min-height: 100vh;
  background: var(--bg-liquid);
  color: #fff;
  font-family: 'Inter', sans-serif;
}

.settings-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 4rem;
}

@media (max-width: 768px) {
  .settings-nav { padding: 1.5rem 1rem; }
  .nav-logo { font-size: 1.8rem !important; }
}

.nav-logo {
  color: var(--netflix-red);
  font-size: 2.5rem;
  font-weight: 800;
  cursor: pointer;
}

.back-btn {
  background: var(--glass-bg);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.1);
  padding: 0.8rem 1.5rem;
  border-radius: var(--radius-main);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255,255,255,0.1);
  transform: translateX(-5px);
}

.settings-content-wrapper {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.settings-card {
  width: 100%;
  max-width: 800px;
  padding: 3rem;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
}

@media (max-width: 768px) {
  .settings-card { padding: 1.5rem; border-radius: 12px; }
  .settings-title { font-size: 1.5rem; margin-bottom: 1.5rem; }
}

.settings-title {
  font-size: 2rem;
  margin-bottom: 2.5rem;
  background: linear-gradient(to right, #fff, var(--text-muted));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.setting-section {
  margin-bottom: 2.5rem;
}

.section-subtitle {
  font-size: 1.25rem;
  color: var(--neon-cyan);
  margin-bottom: 0.5rem;
}

.section-desc {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-bottom: 1.5rem;
}

.input-group {
  display: flex;
  gap: 1rem;
}

@media (max-width: 600px) {
  .input-group { flex-direction: column; }
  .button-group { flex-direction: column; width: 100%; }
  .action-btn { width: 100%; padding: 1rem !important; }
}

.settings-input {
  flex: 1;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 1rem;
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
}

.settings-input:focus {
  outline: none;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
}

.action-btn {
  padding: 0 1.5rem;
  border-radius: 10px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.primary {
  background: var(--netflix-red);
  color: #fff;
}

.action-btn.secondary {
  background: var(--glass-bg);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.1);
  padding: 1rem 2rem;
}

.action-btn:hover:not(:disabled) {
  transform: scale(1.05);
  filter: brightness(1.2);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-group {
    display: flex;
    gap: 1rem;
}

.action-btn.neon {
    background: rgba(0, 255, 255, 0.1);
    color: var(--neon-cyan);
    border: 1px solid var(--neon-cyan);
    padding: 1rem 2rem;
}

.action-btn.neon:hover:not(:disabled) {
    background: var(--neon-cyan);
    color: #000;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
}

.divider {
  height: 1px;
  background: rgba(255,255,255,0.05);
  margin: 2.5rem 0;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Toggle Switch Styles */
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255,255,255,0.1);
  transition: .4s;
  border: 1px solid rgba(255,255,255,0.1);
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
}

input:checked + .slider {
  background-color: var(--neon-cyan);
  border-color: var(--neon-cyan);
}

input:focus + .slider {
  box-shadow: 0 0 1px var(--neon-cyan);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>
