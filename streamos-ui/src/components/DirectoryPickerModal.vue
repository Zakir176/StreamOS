<template>
  <div v-if="show" class="picker-overlay" @click.self="$emit('close')">
    <div class="picker-modal glass">
      <!-- Modal Header -->
      <div class="picker-header">
        <div class="header-left">
          <div class="folder-header-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
            </svg>
          </div>
          <div>
            <h3 class="picker-title">{{ title || 'Select Media Directory' }}</h3>
            <p class="picker-subtitle">Browse drives and folders on your system</p>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- Quick Locations / Drives Bar -->
      <div class="quick-nav-bar" v-if="quickPaths.length > 0">
        <span class="quick-label">Locations:</span>
        <div class="quick-pills">
          <button 
            v-for="item in quickPaths" 
            :key="item.path" 
            class="quick-pill glass"
            :class="{ active: currentPath === item.path }"
            @click="navigateTo(item.path)"
            :title="item.path"
          >
            {{ item.name }}
          </button>
        </div>
      </div>

      <!-- Path Bar & Navigation Controls -->
      <div class="path-bar-container">
        <button 
          class="nav-btn glass" 
          :disabled="!parentPath || loading" 
          @click="navigateUp"
          title="Go to parent directory"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 19V5M5 12l7-7 7 7"/>
          </svg>
          Up
        </button>
        
        <div class="path-input-wrapper glass">
          <input 
            v-model="inputPath" 
            @keyup.enter="navigateTo(inputPath)"
            placeholder="Type or paste path..."
            class="path-input" 
          />
          <button class="go-btn" @click="navigateTo(inputPath)" title="Navigate to path">
            Go
          </button>
        </div>

        <button class="nav-btn glass refresh-btn" @click="fetchDirectory(currentPath)" title="Refresh folder">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ spinning: loading }">
            <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
      </div>

      <!-- Directory List Body -->
      <div class="picker-body">
        <div v-if="loading" class="picker-status">
          <div class="spinner"></div>
          <span>Loading directories...</span>
        </div>

        <div v-else-if="errorMessage" class="picker-error glass">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
          </svg>
          <div class="error-text">
            <strong>Unable to open directory</strong>
            <p>{{ errorMessage }}</p>
          </div>
          <button class="retry-btn glass" @click="navigateUp" v-if="parentPath">Go Up</button>
        </div>

        <div v-else-if="directories.length === 0" class="picker-empty">
          <div class="empty-icon">📂</div>
          <h4>No Subfolders Here</h4>
          <p>You can still select <code>{{ currentPath }}</code> as your media directory below.</p>
        </div>

        <div v-else class="dir-grid">
          <div 
            v-for="dir in directories" 
            :key="dir.path" 
            class="dir-item glass"
            :class="{ selected: selectedPath === dir.path }"
            @click="selectDir(dir.path)"
            @dblclick="navigateTo(dir.path)"
          >
            <div class="dir-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>
              </svg>
            </div>
            <div class="dir-info">
              <span class="dir-name" :title="dir.name">{{ dir.name }}</span>
              <span v-if="isKnownMediaCategory(dir.name)" class="dir-badge">
                {{ getMediaCategoryLabel(dir.name) }}
              </span>
            </div>
            <button class="open-dir-btn" @click.stop="navigateTo(dir.path)" title="Enter folder">
              →
            </button>
          </div>
        </div>
      </div>

      <!-- Detection / Stats Bar -->
      <div class="stats-bar glass" v-if="currentStats">
        <div class="stats-info">
          <span v-if="currentStats.video_count > 0" class="stat-badge green">
            ✓ {{ currentStats.video_count }} video files found
          </span>
          <span v-if="currentStats.has_media_subfolders" class="stat-badge cyan">
            ✓ Media library subfolders detected
          </span>
          <span v-if="currentStats.video_count === 0 && !currentStats.has_media_subfolders" class="stat-badge neutral">
            Active folder: {{ currentPath }}
          </span>
        </div>
      </div>

      <!-- Footer & Action Buttons -->
      <div class="picker-footer">
        <div class="footer-left">
          <label class="auto-scan-toggle">
            <input type="checkbox" v-model="autoScan" />
            <span>Scan library immediately after selecting</span>
          </label>
        </div>
        <div class="footer-actions">
          <button class="cancel-btn glass" @click="$emit('close')">Cancel</button>
          <button 
            class="select-btn" 
            :disabled="!effectivePath || loading" 
            @click="confirmSelection"
          >
            Select This Directory
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  initialPath: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: 'Select Media Directory'
  }
})

const emit = defineEmits(['close', 'select'])

const API_BASE = import.meta.env.VITE_API_BASE || `http://${window.location.hostname}:8000`

const currentPath = ref('')
const inputPath = ref('')
const parentPath = ref(null)
const selectedPath = ref('')
const directories = ref([])
const quickPaths = ref([])
const currentStats = ref(null)
const loading = ref(false)
const errorMessage = ref('')
const autoScan = ref(true)

const effectivePath = computed(() => {
  return selectedPath.value || currentPath.value
})

const isKnownMediaCategory = (name) => {
  const n = (name || '').toLowerCase()
  return ['movies', 'tv shows', 'anime', 'kids', 'teen', 'adult'].includes(n)
}

const getMediaCategoryLabel = (name) => {
  const n = (name || '').toLowerCase()
  if (n === 'movies') return '🎬 Movies'
  if (n === 'tv shows') return '📺 TV Shows'
  if (n === 'anime') return '🎌 Anime'
  if (n === 'kids') return '👶 Kids'
  if (n === 'teen') return '🍿 Teen'
  if (n === 'adult') return '🔞 Adult'
  return name
}

const fetchDirectory = async (path = '') => {
  loading.value = true
  errorMessage.value = ''
  selectedPath.value = ''
  
  try {
    const url = path ? `${API_BASE}/filesystem/browse?path=${encodeURIComponent(path)}` : `${API_BASE}/filesystem/browse`
    const res = await fetch(url)
    const data = await res.json()
    
    if (res.ok && data.success) {
      currentPath.value = data.current_path
      inputPath.value = data.current_path
      parentPath.value = data.parent_path
      directories.value = data.directories || []
      quickPaths.value = data.quick_paths || []
      currentStats.value = data.stats || null
    } else {
      errorMessage.value = data.error || 'Failed to list directory.'
      if (data.current_path) {
        currentPath.value = data.current_path
        inputPath.value = data.current_path
        parentPath.value = data.parent_path
      }
    }
  } catch (err) {
    console.error('Filesystem browse error:', err)
    errorMessage.value = 'Failed to connect to backend server.'
  } finally {
    loading.value = false
  }
}

const navigateTo = (path) => {
  if (!path) return
  fetchDirectory(path)
}

const navigateUp = () => {
  if (parentPath.value) {
    navigateTo(parentPath.value)
  }
}

const selectDir = (path) => {
  if (selectedPath.value === path) {
    // If already selected, double-click behavior or deselect
    selectedPath.value = ''
  } else {
    selectedPath.value = path
  }
}

const confirmSelection = () => {
  const pathToSelect = effectivePath.value
  if (!pathToSelect) return
  emit('select', { path: pathToSelect, scanNow: autoScan.value })
  emit('close')
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    fetchDirectory(props.initialPath || currentPath.value)
  }
})

onMounted(() => {
  if (props.show) {
    fetchDirectory(props.initialPath)
  }
})
</script>

<style scoped>
.picker-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
  animation: fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.picker-modal {
  width: 100%;
  max-width: 780px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  background: rgba(18, 18, 24, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-main);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(229, 9, 20, 0.15);
  overflow: hidden;
  animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

/* Header */
.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.folder-header-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(229, 9, 20, 0.15);
  border: 1px solid rgba(229, 9, 20, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--netflix-red);
}

.folder-header-icon svg {
  width: 22px;
  height: 22px;
}

.picker-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.01em;
}

.picker-subtitle {
  margin: 2px 0 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.close-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(90deg);
}

/* Quick Nav Bar */
.quick-nav-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  overflow-x: auto;
}

.quick-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  white-space: nowrap;
}

.quick-pills {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}

.quick-pill {
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.quick-pill:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
  color: #fff;
}

.quick-pill.active {
  background: rgba(229, 9, 20, 0.2);
  border-color: var(--netflix-red);
  color: #fff;
}

/* Path Bar */
.path-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn svg {
  width: 16px;
  height: 16px;
}

.nav-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.nav-btn:not(:disabled):hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
}

.path-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  border-radius: 8px;
  padding: 2px 4px 2px 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.path-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 0.85rem;
  font-family: monospace;
  outline: none;
  padding: 6px 0;
}

.go-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.go-btn:hover {
  background: var(--netflix-red);
  border-color: var(--netflix-red);
}

.refresh-btn {
  padding: 8px 10px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Picker Body */
.picker-body {
  flex: 1;
  min-height: 280px;
  max-height: 380px;
  overflow-y: auto;
  padding: 16px 24px;
}

.picker-status {
  height: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: var(--text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--netflix-red);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.picker-error {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: #ff6b6b;
  border-color: rgba(255, 107, 107, 0.3);
}

.picker-error svg {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
}

.error-text strong {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 2px;
}

.error-text p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.8;
}

.retry-btn {
  padding: 6px 14px;
  color: #fff;
  cursor: pointer;
}

.picker-empty {
  height: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
  opacity: 0.7;
}

.picker-empty h4 {
  margin: 0 0 6px;
  font-size: 1.1rem;
  color: #fff;
}

.picker-empty p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.picker-empty code {
  color: var(--neon-cyan);
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
}

/* Directory Grid */
.dir-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}

.dir-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 1, 0.5, 1);
  user-select: none;
}

.dir-item:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.dir-item.selected {
  background: rgba(229, 9, 20, 0.18);
  border-color: var(--netflix-red);
  box-shadow: 0 0 15px rgba(229, 9, 20, 0.25);
}

.dir-icon {
  width: 24px;
  height: 24px;
  color: #fbbf24;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dir-icon svg {
  width: 22px;
  height: 22px;
}

.dir-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dir-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dir-badge {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--neon-cyan);
}

.open-dir-btn {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  width: 26px;
  height: 26px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.open-dir-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* Stats Bar */
.stats-bar {
  padding: 10px 24px;
  background: rgba(0, 0, 0, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stats-info {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stat-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
}

.stat-badge.green {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #4ade80;
}

.stat-badge.cyan {
  background: rgba(0, 255, 255, 0.15);
  border: 1px solid rgba(0, 255, 255, 0.3);
  color: var(--neon-cyan);
}

.stat-badge.neutral {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

/* Footer */
.picker-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  gap: 16px;
  flex-wrap: wrap;
}

.auto-scan-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-muted);
  cursor: pointer;
}

.auto-scan-toggle input {
  accent-color: var(--netflix-red);
  cursor: pointer;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.cancel-btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.select-btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  background: var(--netflix-red);
  color: #fff;
  border: none;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.25, 1, 0.5, 1);
  box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
}

.select-btn:hover:not(:disabled) {
  background: #ff1f2d;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(229, 9, 20, 0.6);
}

.select-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

@media (max-width: 600px) {
  .dir-grid {
    grid-template-columns: 1fr;
  }
  .picker-footer {
    flex-direction: column;
    align-items: stretch;
  }
  .footer-actions {
    justify-content: flex-end;
  }
}
</style>
