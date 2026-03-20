<<<<
<template>
  <div class="video-player" ref="playerContainerRef" @mousemove="handleUserActivity" :class="{ 'ui-hidden': isUiHidden }">
    <!-- Top Bar for Back Button and Title -->
    <div class="player-header">
      <button class="back-btn" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 12H4M4 12L10 18M4 12L10 6" />
        </svg>
      </button>
      <h2 class="video-title" v-if="videoTitle">{{ videoTitle }}</h2>
    </div>

    <!-- The Video Element -->
    <video 
      ref="videoRef" 
      autoplay 
      class="main-video"
      :src="videoSrc"
      @click="togglePlay"
      @dblclick="toggleFullscreen"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onLoadedMetadata"
      @ended="handleVideoEnded"
      @play="isPlaying = true"
      @pause="isPlaying = false"
      @volumechange="onVolumeChange"
    >
      Your browser does not support the video tag.
    </video>

    <!-- Center Play/Pause Overlay indicating state (Briefly flashes on click) -->
    <div class="center-play-indicator" :class="{ 'animate-ping': showPlayIndicator }">
      <svg v-if="isPlaying" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 4h4v16H6zm8 0h4v16h-4z"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="currentColor">
        <path d="M5 3L19 12L5 21V3Z"/>
      </svg>
    </div>

    <!-- Ambient Dynamic Glow (Mood Lighting) -->
    <div class="player-ambient-glow" :class="{ 'glow-playing': isPlaying }"></div>

    <!-- Bottom Floating UI Container -->
    <div class="player-controls-floating" :class="{ 'controls-visible': !isUiHidden }">
      
      <!-- Premium Progress Bar (Scrub-ready) -->
      <div class="progress-wrapper" :class="{ 'scrubbing': hoverPercent !== null }" @click="seek">
        <div class="progress-hit-area" @mousemove="handleProgressHover" @mouseleave="hoverPercent = null">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            <div class="progress-hover-fill" v-if="hoverPercent !== null" :style="{ width: hoverPercent + '%' }"></div>
          </div>
          
          <!-- Visual Scrub Preview -->
          <div 
            class="scrub-preview-modern" 
            v-if="hoverPercent !== null" 
            :style="{ left: hoverPercent + '%' }"
          >
            <div class="scrub-glass-card">
              <img :src="scrubThumbnailUrl" class="scrub-img" @error="handleScrubError" />
              <div class="scrub-timestamp">{{ formatTime((hoverPercent / 100) * duration) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls Glass Cluster -->
      <div class="glass-controls-cluster">
        
        <!-- Left Cluster: Time and Tools -->
        <div class="cluster-section left">
          <div class="time-stat">
            <span class="current">{{ formatTime(currentTime) }}</span>
            <span class="divider">/</span>
            <span class="total">{{ formatTime(duration) }}</span>
          </div>
          
          <div class="playback-speed-selector">
            <button class="speed-toggle" @click="toggleSpeedMenu">
              {{ playbackSpeed }}x
            </button>
            <div class="speed-menu" v-if="showSpeedMenu">
              <button 
                v-for="s in [0.5, 0.75, 1, 1.25, 1.5, 2]" 
                :key="s" 
                @click="setPlaybackSpeed(s)"
                :class="{ active: s === playbackSpeed }"
              >
                {{ s }}x
              </button>
            </div>
          </div>
        </div>

        <!-- Center Cluster: The Main Engine -->
        <div class="cluster-section center">
          <button class="round-btn skip" @click="skip(-10)" title="Back 10s">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.5 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.59 2.91-6.5 6.5-6.5S19 8.41 19 12s-2.91 6.5-6.5 6.5c-1.2 0-2.32-.33-3.29-.9l-1.42 1.42C9.13 20.16 10.73 20.5 12.5 20.5c4.97 0 9-4.03 9-9s-4.03-9-9-9z"/></svg>
            <span class="skip-val">10</span>
          </button>

          <button class="main-play-btn-cinema" @click="togglePlay">
            <svg v-if="isPlaying" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="5" width="4" height="14" rx="1"/>
              <rect x="14" y="5" width="4" height="14" rx="1"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </button>

          <button class="round-btn skip" @click="skip(10)" title="Forward 10s">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.41 7.89L14.5 4l-.07.14V7c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9h-3c0 3.59-2.91 6.5-6.5 6.5S6.5 19.59 6.5 16s2.91-6.5 6.5-6.5v2.89l3.89-3.89z"/></svg>
            <span class="skip-val">10</span>
          </button>
        </div>

        <!-- Right Cluster: Volume and Scale -->
        <div class="cluster-section right">
           <div class="volume-hub">
             <button class="tool-btn" @click="toggleMute">
               <svg v-if="isMuted || volume === 0" viewBox="0 0 24 24" fill="currentColor"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM19 12c0 2.76-1.57 5.16-3.87 6.31l1.1 1.1C19.23 17.9 21 15.15 21 12s-1.77-5.9-4.77-7.41l-1.1 1.1c2.3 1.15 3.87 3.55 3.87 6.31zM3 9v6h4l5 5V4L7 9H3z"/></svg>
               <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
             </button>
             <input type="range" class="vol-slider-mini" min="0" max="1" step="0.05" v-model="volume" @input="setVolume" />
           </div>

           <button class="tool-btn" @click="toggleFullscreen">
             <svg v-if="!isFullscreen" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/></svg>
             <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/></svg>
           </button>
        </div>

      </div>
    </div>

    <!-- Up Next Overlay (Shown when video ends) -->
    <div v-if="showUpNext" class="up-next-overlay">
      <div class="up-next-card">
        <h3>Up Next</h3>
        <h2 class="next-title">{{ nextEpisode?.title }}</h2>
        <div class="next-thumb">
          <img v-if="nextEpisode?.thumbnail_url" :src="`${API_BASE}${nextEpisode.thumbnail_url}?profile_id=${profileId}`" :alt="nextEpisode.title" />
          <div class="countdown-circle">{{ countdown }}</div>
        </div>
        <div class="up-next-actions">
          <button class="btn-play-now" @click="playNext">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 4h12v16H6z" v-if="false"/> <!-- hack just icon -->
              <path d="M5 3L19 12L5 21V3Z" />
            </svg>
            Play Now
          </button>
          <button class="btn-cancel-next" @click="cancelUpNext">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  videoSrc: String,
  videoTitle: String,
  videoId: Number
})

const emit = defineEmits(['close', 'play-next'])

const profileId = ref(localStorage.getItem('profile_id'))
const API_BASE = import.meta.env.VITE_API_BASE

const playerContainerRef = ref(null)
const videoRef = ref(null)
const isPlaying = ref(true)
const currentTime = ref(0)
const savedTime = ref(0) // Safe storage for the initial resume timestamp
const duration = ref(0)
const progressPercent = ref(0)
const hoverPercent = ref(null)
const scrubThumbnailUrl = ref('')
const volume = ref(1)
const isMuted = ref(false)
const isFullscreen = ref(false)

// UI hide timer logic
const isUiHidden = ref(false)
let hideTimer = null
let syncTimer = null
const showPlayIndicator = ref(false)

// Up next logic
const nextEpisode = ref(null)
const showUpNext = ref(false)
const countdown = ref(5)
let countdownTimer = null

// Playback speed logic
const playbackSpeed = ref(1)
const showSpeedMenu = ref(false)

const toggleSpeedMenu = () => {
  showSpeedMenu.value = !showSpeedMenu.value
}

const setPlaybackSpeed = (speed) => {
  playbackSpeed.value = speed
  if (videoRef.value) {
    videoRef.value.playbackRate = speed
  }
  showSpeedMenu.value = false
}

const handleUserActivity = () => {
  isUiHidden.value = false
  showSpeedMenu.value = false
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    if (isPlaying.value) {
      isUiHidden.value = true
    }
  }, 3000)
}

const togglePlay = () => {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play()
  } else {
    videoRef.value.pause()
  }
  
  // Flash center indicator
  showPlayIndicator.value = true
  setTimeout(() => {
    showPlayIndicator.value = false
  }, 500)
}

const skip = (seconds) => {
  if (!videoRef.value) return
  videoRef.value.currentTime += seconds
}

const onTimeUpdate = () => {
  if (!videoRef.value) return
  currentTime.value = videoRef.value.currentTime
  if (duration.value > 0) {
    progressPercent.value = (currentTime.value / duration.value) * 100
  }
}

const onLoadedMetadata = () => {
  if (!videoRef.value) return
  duration.value = videoRef.value.duration
  
  // Now it's safe to seek if we have saved progress
  if (savedTime.value > 0 && savedTime.value < duration.value - 60) {
    videoRef.value.currentTime = savedTime.value
  }
}

const handleProgressHover = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const pos = (e.clientX - rect.left) / rect.width
  hoverPercent.value = pos * 100
  
  // Calculate scrub thumbnail
  const hoverTime = pos * duration.value
  const interval = 10
  const syncTime = Math.floor(hoverTime / interval) * interval
  scrubThumbnailUrl.value = `${API_BASE}/video/${props.videoId}/scrub/${syncTime}`
}

const handleScrubError = (e) => {
  // If thumbnail fails (maybe not generated yet), hide the preview or show fallback
  // e.target.style.display = 'none'
}

const seek = (e) => {
  if (!videoRef.value) return
  const rect = e.currentTarget.getBoundingClientRect()
  const pos = (e.clientX - rect.left) / rect.width
  videoRef.value.currentTime = pos * duration.value
}

const setVolume = () => {
  if (!videoRef.value) return
  videoRef.value.volume = volume.value
  isMuted.value = volume.value === 0
}

const toggleMute = () => {
  if (!videoRef.value) return
  isMuted.value = !isMuted.value
  if (isMuted.value) {
    videoRef.value.volume = 0
  } else {
    videoRef.value.volume = volume.value > 0 ? volume.value : 1
  }
}

const onVolumeChange = () => {
  if (!videoRef.value) return
  volume.value = videoRef.value.volume
  isMuted.value = videoRef.value.muted || videoRef.value.volume === 0
}

const toggleFullscreen = () => {
  const container = playerContainerRef.value
  if (!container) return

  const docFullscreen = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement

  if (!docFullscreen) {
    if (container.requestFullscreen) {
      container.requestFullscreen().catch(err => console.warn(err))
    } else if (container.webkitRequestFullscreen) {
      container.webkitRequestFullscreen()
    } else if (container.mozRequestFullScreen) {
      container.mozRequestFullScreen()
    } else if (container.msRequestFullscreen) {
      container.msRequestFullscreen()
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen()
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen()
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen()
    }
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement)
}

const formatTime = (timeInSeconds) => {
  if (isNaN(timeInSeconds)) return "00:00:00"
  const h = Math.floor(timeInSeconds / 3600)
  const m = Math.floor((timeInSeconds % 3600) / 60).toString().padStart(2, '0')
  const s = Math.floor(timeInSeconds % 60).toString().padStart(2, '0')
  
  if (h > 0) return `${h}:${m}:${s}`
  return `${m}:${s}`
}

const syncProgress = async () => {
  if (!props.videoId || !videoRef.value || videoRef.value.currentTime < 5) return
  
  try {
    await fetch(`${API_BASE}/progress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        profile_id: parseInt(profileId.value),
        video_id: props.videoId,
        current_time: Math.floor(videoRef.value.currentTime),
        duration: Math.floor(videoRef.value.duration)
      })
    })
  } catch (err) {
    console.error('Failed to sync progress:', err)
  }
}

const fetchInitialProgress = async () => {
  if (!props.videoId) return
  try {
    const res = await fetch(`${API_BASE}/progress/${props.videoId}?profile_id=${profileId.value}`)
    const data = await res.json()
    if (data.current_time > 0) {
      savedTime.value = data.current_time
      // Do not try to seek videoRef right here, the metadata hasn't loaded yet.
    }
  } catch (err) {
    console.error('Failed to fetch initial progress:', err)
  }
}

const fetchNextEpisode = async () => {
  if (!props.videoId) return
  try {
    const res = await fetch(`${API_BASE}/next-episode/${props.videoId}`)
    const data = await res.json()
    if (data) {
      nextEpisode.value = data
    }
  } catch (err) {
    console.error('Failed to fetch next episode:', err)
  }
}

const handleVideoEnded = () => {
  isPlaying.value = false
  if (nextEpisode.value) {
    showUpNext.value = true
    countdown.value = 5
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        playNext()
      }
    }, 1000)
  }
}

const playNext = () => {
  clearInterval(countdownTimer)
  emit('play-next', nextEpisode.value)
}

const cancelUpNext = () => {
  clearInterval(countdownTimer)
  showUpNext.value = false
}

const triggerScrubGeneration = async () => {
  if (!props.videoId) return
  try {
    await fetch(`${API_BASE}/video/${props.videoId}/generate-scrub`, { method: 'POST' })
  } catch (err) {
    console.error('Failed to trigger scrub generation:', err)
  }
}

onMounted(() => {
  fetchInitialProgress()
  fetchNextEpisode()
  triggerScrubGeneration()
  
  if (videoRef.value) {
    videoRef.value.play().catch(err => console.warn('Autoplay failed:', err))
  }
  handleUserActivity() // start timer
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  
  // Sync progress every 5 seconds
  syncTimer = setInterval(syncProgress, 5000)
})

onUnmounted(() => {
  syncProgress() // Final sync before unmount
  clearTimeout(hideTimer)
  clearInterval(syncTimer)
  clearInterval(countdownTimer)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<style scoped>
.player-ambient-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.4) 100%);
  pointer-events: none;
  z-index: 2;
  transition: opacity 1s ease;
  opacity: 0;
}

.player-ambient-glow.glow-playing {
  opacity: 1;
}

/* Floating Controls Container */
.player-controls-floating {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  width: min(90vw, 1200px);
  z-index: 100;
  transition: all 0.5s cubic-bezier(0.2, 0, 0, 1);
  opacity: 0;
  pointer-events: none;
}

.player-controls-floating.controls-visible {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
  pointer-events: all;
}

/* Glass Cluster Styling */
.glass-controls-cluster {
  background: rgba(15, 15, 15, 0.4);
  backdrop-filter: blur(25px) saturate(1.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 20px 50px rgba(0,0,0,0.6);
  margin-top: 15px;
}

.cluster-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.cluster-section.center {
  gap: 40px;
}

/* Progress Bar Redesign */
.progress-wrapper {
  width: 100%;
  padding: 10px 0;
  cursor: pointer;
  position: relative;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
  position: relative;
  overflow: visible;
  transition: height 0.3s ease;
}

.scrubbing .progress-track {
  height: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff4d4d, #E50914);
  border-radius: 3px;
  position: relative;
  box-shadow: 0 0 15px rgba(229, 9, 20, 0.4);
}

.progress-hover-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
}

/* Center Cluster Engine */
.main-play-btn-cinema {
  width: 72px;
  height: 72px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.main-play-btn-cinema svg {
  width: 32px;
  height: 32px;
  color: #000;
}

.main-play-btn-cinema:hover {
  transform: scale(1.1);
  box-shadow: 0 15px 40px rgba(255,255,255,0.2);
}

.round-btn {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.round-btn:hover {
  background: rgba(255,255,255,0.15);
  border-color: rgba(255,255,255,0.3);
}

.round-btn svg { width: 22px; height: 22px; }
.skip-val { font-size: 0.6rem; font-weight: 800; margin-top: -2px; }

/* Time Display */
.time-stat {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.5px;
}

.time-stat .divider { opacity: 0.3; margin: 0 8px; }
.time-stat .total { opacity: 0.5; }

/* Speed Selector */
.playback-speed-selector {
  position: relative;
}

.speed-toggle {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  color: #fff;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 800;
  cursor: pointer;
}

.speed-menu {
  position: absolute;
  bottom: 140%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(25, 25, 25, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 60px;
}

.speed-menu button {
  background: none;
  border: none;
  color: #fff;
  padding: 8px;
  font-size: 0.8rem;
  cursor: pointer;
}

.speed-menu button:hover { background: rgba(255,255,255,0.1); }
.speed-menu button.active { color: #E50914; font-weight: bold; }

/* Volume & Fullscreen */
.volume-hub {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.tool-btn:hover { opacity: 1; }
.tool-btn svg { width: 24px; height: 24px; }

.vol-slider-mini {
  width: 80px;
  height: 4px;
}

/* Scrub Modern Tooltip */
.scrub-preview-modern {
  position: absolute;
  bottom: 40px;
  transform: translateX(-50%);
  padding-bottom: 20px;
}

.scrub-glass-card {
  padding: 6px;
  background: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.8);
  text-align: center;
}

.scrub-img {
  width: 220px;
  aspect-ratio: 16/9;
  border-radius: 8px;
  object-fit: cover;
}

.scrub-timestamp {
  font-size: 0.8rem;
  font-weight: 800;
  margin-top: 6px;
  color: #fff;
}

@media (max-width: 768px) {
  .player-controls-floating { width: 96vw; bottom: 20px; }
  .glass-controls-cluster { padding: 10px 15px; border-radius: 16px; }
  .cluster-section.left, .cluster-section.right { display: none; }
  .cluster-section.center { gap: 30px; }
  .main-play-btn-cinema { width: 60px; height: 60px; }
  .main-play-btn-cinema svg { width: 28px; height: 28px; }
  .round-btn { width: 44px; height: 44px; }
  .back-btn { width: 48px; height: 48px; }
  .video-title { font-size: 1rem; }
}

/* Up Next Overlay */
.up-next-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  backdrop-filter: blur(10px);
}

.up-next-card {
  text-align: center;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.up-next-card h3 {
  font-size: 1.2rem;
  font-weight: 500;
  color: #ccc;
  margin: 0;
}

.next-title {
  font-size: 2.5rem;
  margin: 0 0 20px 0;
  font-weight: 700;
}

.next-thumb {
  position: relative;
  width: 300px;
  height: 168px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.next-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.6;
}

.countdown-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  border: 3px solid #E50914;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: bold;
  background: rgba(0,0,0,0.5);
}

.up-next-actions {
  display: flex;
  gap: 20px;
  margin-top: 30px;
}

.btn-play-now {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  color: #000;
  border: none;
  padding: 12px 30px;
  font-size: 1.2rem;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.btn-play-now svg {
  width: 24px;
  height: 24px;
}

.btn-play-now:hover {
  transform: scale(1.05);
  background: #e6e6e6;
}

.btn-cancel-next {
  background: rgba(255,255,255,0.2);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.4);
  padding: 12px 30px;
  font-size: 1.2rem;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel-next:hover {
  background: rgba(255,255,255,0.3);
}
</style>
