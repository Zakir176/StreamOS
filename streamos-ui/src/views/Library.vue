<template>
  <div class="library-container" :style="ambientStyles">
    <!-- Ambient Halo Glow Layer -->
    <div class="ambient-halo-layer"></div>
    <!-- Netflix Nav -->
    <nav class="netflix-nav" :class="{ 'scrolled': isScrolled }">
      <div class="nav-left">
        <h1 class="logo" @click="$router.push('/')">Stream<span>OS</span></h1>
        <ul class="nav-links">
          <li :class="{ active: $route.path === '/library' }" @click="$router.push('/library')">Home</li>
          <li :class="{ active: $route.path === '/tv-shows' }" @click="$router.push('/tv-shows')">TV Shows</li>
          <li :class="{ active: $route.path === '/movies' }" @click="$router.push('/movies')">Movies</li>
          <li :class="{ active: $route.path === '/anime' }" @click="$router.push('/anime')">Anime</li>
        </ul>
      </div>
      <div class="nav-right">
        <div class="search-box glass">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input ref="searchRef" v-model="searchQuery" placeholder="Titles, actors, directors..." class="search-input" />
          <button v-if="searchQuery" class="clear-search" @click="searchQuery = ''">×</button>
        </div>
        <div class="notifications">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 8C18 6.4087 17.3679 4.88258 16.2426 3.75736C15.1174 2.63214 13.5913 2 12 2C10.4087 2 8.88258 2.63214 7.75736 3.75736C6.63214 4.88258 6 6.4087 6 8C6 15 3 17 3 17H21C21 17 18 15 18 8Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.73 21C13.5542 21.3031 13.3019 21.5547 12.9982 21.7295C12.6946 21.9044 12.3504 21.9965 12 21.9965C11.6496 21.9965 11.3054 21.9044 11.0018 21.7295C10.6981 21.5547 10.4458 21.3031 10.27 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="user-profile" @click="toggleDropdown">
          <div class="profile-box glass">
            <img :src="profileAvatar" :alt="profileName" class="nav-avatar" />
          </div>
          <span class="caret" :class="{ 'open': showDropdown }">▼</span>
          
          <!-- Profile Dropdown -->
          <div v-if="showDropdown" class="profile-dropdown glass" @click.stop>
            <div class="dropdown-header">
              <img :src="profileAvatar" :alt="profileName" class="dropdown-avatar" />
              <div class="dropdown-user-info">
                <p class="dropdown-username">{{ profileName }}</p>
                <p class="dropdown-category">{{ profileCategory }}</p>
              </div>
            </div>
            <div class="dropdown-divider"></div>
            <ul class="dropdown-menu">
              <li @click="switchProfile">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 17l5-5-5-5M19.8 12H9M13 22a10 10 0 110-20"/></svg>
                Switch Profile
              </li>
              <li @click="$router.push('/settings')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
                Manage Profiles
              </li>
              <li @click="rescanLibrary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/></svg>
                Rescan Library
              </li>
              <li @click="toggleTheme">
                <svg v-if="currentTheme === 'midnight'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
                Theme: {{ currentTheme === 'midnight' ? 'Midnight' : 'Cinematic' }}
              </li>
              <div class="dropdown-divider"></div>
              <li class="logout" @click="$router.push('/account-settings')">Account & Settings</li>
              <li class="logout" @click="logout">Sign Out of StreamOS</li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
    
    <header 
      class="billboard" 
      v-if="featuredVideo && !isMobile"
      @mouseenter="handleBillboardMouseEnter"
      @mouseleave="handleBillboardMouseLeave"
    >
      <div 
        class="billboard-background" 
        :key="featuredVideo.id"
        :style="{ 
          backgroundImage: `linear-gradient(to right, var(--bg-dark) 0%, transparent 60%), url(${getImageUrl(featuredVideo.backdrop_url || featuredVideo.thumbnail_url)})`,
          '--billboard-color': featuredVideo.dominant_color || 'var(--bg-dark)'
        }"
      >
        <div class="vignette"></div>
        
        <!-- Trailer Peek Overlay -->
        <div v-if="showTrailer" class="trailer-peek-overlay">
           <iframe 
            :src="`${featuredVideo.trailer_url}?autoplay=1&mute=1&controls=0&loop=1&playlist=${featuredVideo.trailer_url.split('/').pop().split('?')[0]}`" 
            frameborder="0" 
            allow="autoplay; encrypted-media" 
            allowfullscreen
          ></iframe>
        </div>
      </div>
      
      <div class="billboard-content-wrapper">
        <div class="billboard-content floating-content" :key="'content-' + featuredVideo.id">
          <div class="billboard-meta">
            <span class="meta-badge trending">🔥 Trending</span>
            <span class="meta-badge new">New</span>
            <span class="meta-badge quality">4K Ultra HD</span>
          </div>
          <h1 class="featured-title">{{ featuredVideo.title }}</h1>
          <p class="featured-desc">
            {{ featuredVideo.description || 'Experience the ultimate streaming experience with StreamOS. Watch all your favorite content in stunning quality.' }}
          </p>
          <div class="billboard-actions">
            <button class="btn-play" @click="openPlayer(featuredVideo.id)">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              Play
            </button>
            <button class="btn-info" @click="handleVideoClick(featuredVideo)">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M11 17h2v-6h-2v6zm1-15C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zM11 9h2V7h-2v2z"/></svg>
              More Info
            </button>
          </div>
        </div>
      </div>

      <!-- Cinematic Next-Up Strip -->
      <div class="billboard-nav-strip">
        <div 
          v-for="(item, index) in billboardItems" 
          :key="'nav-' + index"
          class="nav-strip-item"
          :class="{ active: index === currentBillboardIndex }"
          @click="currentBillboardIndex = index; showTrailer = false"
        >
          <div class="nav-poster-mini shadow-lg">
             <img :src="getImageUrl(item.backdrop_url || item.thumbnail_url)" :alt="item.title" loading="lazy" />
             <div class="nav-timer" v-if="index === currentBillboardIndex"></div>
          </div>
        </div>
      </div>
    </header>
    
    <main class="content">
      <h2 class="library-header">{{ libraryTitle }}</h2>

      <!-- Continue Watching Row (Always Show if exists) -->
      <div v-if="searchQuery && !filteredVideos.all?.length" class="no-results">
        <p>No results found for "{{ searchQuery }}"</p>
        <button class="btn-netflix secondary" @click="searchQuery = ''">Clear Search</button>
      </div>

      <VideoRow 
        v-if="filteredVideos.continue_watching?.length && !searchQuery"
        title="Continue Watching"
        :videos="filteredVideos.continue_watching" 
        :profile-id="profileId"
        :loading="loading"
        :focused-index="getFocusedIndex('Continue Watching')"
        @play="handleVideoClick" 
        @hover="handleHover"
      />

      <VideoRow 
        v-if="showMovies && filteredVideos.movies?.length"
        title="Movies"
        :videos="filteredVideos.movies" 
        :profile-id="profileId"
        :loading="loading"
        :focused-index="getFocusedIndex('Movies')"
        @play="handleVideoClick" 
        @hover="handleHover"
      />

      <VideoRow 
        v-if="showTvShows && filteredVideos.tv_shows?.length"
        title="TV Shows"
        :videos="filteredVideos.tv_shows" 
        :profile-id="profileId"
        :loading="loading"
        :focused-index="getFocusedIndex('TV Shows')"
        @play="handleVideoClick" 
        @hover="handleHover"
      />

      <VideoRow 
        v-if="showAnime && filteredVideos.anime?.length"
        title="Anime"
        :videos="filteredVideos.anime" 
        :profile-id="profileId"
        :loading="loading"
        :focused-index="getFocusedIndex('Anime')"
        @play="handleVideoClick" 
        @hover="handleHover"
      />
      
      <VideoRow 
        v-if="showAll && filteredVideos.all?.length"
        title="Trending Now"
        :videos="filteredVideos.all.slice().reverse()" 
        :profile-id="profileId"
        :loading="loading"
        :focused-index="getFocusedIndex('Trending Now')"
        @play="handleVideoClick" 
        @hover="handleHover"
      />
      
      <VideoRow 
        v-if="showAll && filteredVideos.all?.length"
        title="Recently Added"
        :videos="filteredVideos.all" 
        :profile-id="profileId"
        :loading="loading"
        :focused-index="getFocusedIndex('Recently Added')"
        @play="handleVideoClick" 
        @hover="handleHover"
      />


    </main>
    
    <!-- Show Detail Modal -->
    <div v-if="selectedSeries" class="series-modal-overlay" @click.self="selectedSeries = null">
      <div class="series-modal glass">
        <button class="close-modal" @click="selectedSeries = null">×</button>
        <div class="series-hero" :style="seriesHeroStyle">
          <div class="series-hero-content">
            <h2>{{ selectedSeries.title }}</h2>
            <p>{{ selectedSeries.episodes?.length }} Episodes</p>
            <p v-if="selectedSeries.description" class="series-description">{{ selectedSeries.description }}</p>
            <div class="meta-info">
              <p v-if="selectedSeries.director"><strong>Director:</strong> {{ selectedSeries.director }}</p>
              <p v-if="selectedSeries.cast"><strong>Cast:</strong> 
                <span v-for="(actor, index) in selectedSeries.cast.split(', ')" :key="actor" class="actor-link" @click="searchByActor(actor)">
                  {{ actor }}{{ index < selectedSeries.cast.split(', ').length - 1 ? ', ' : '' }}
                </span>
              </p>
            </div>
            <div v-if="selectedSeries.trailer_url" class="trailer-container">
               <iframe :src="selectedSeries.trailer_url" frameborder="0" allowfullscreen></iframe>
            </div>
          </div>
        </div>
        <div class="episodes-list">
          <h3>Episodes</h3>
          <div 
            v-for="ep in selectedSeries.episodes" 
            :key="ep.id" 
            class="episode-item glass"
            @click="openPlayer(ep.id, ep.title)"
          >
            <div class="ep-thumb">
              <img :src="getImageUrl(ep.thumbnail_url)" :alt="ep.title" />
              <div class="ep-play-btn">
                <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 3L19 12L5 21V3Z"/>
                </svg>
              </div>
            </div>
            <div class="ep-info">
              <span class="ep-badge">S{{ ep.season }}:E{{ ep.episode }}</span>
              <p class="ep-title">{{ ep.title }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Video Detail Modal (Standalone Movies) -->
    <div v-if="selectedVideoDetail" class="series-modal-overlay" @click.self="selectedVideoDetail = null">
      <div class="series-modal glass">
        <button class="close-modal" @click="selectedVideoDetail = null">×</button>
        <div class="series-hero movie-hero" :style="{ backgroundImage: `linear-gradient(to top, rgba(0,0,0,1), transparent), url(${getImageUrl(selectedVideoDetail.backdrop_url || selectedVideoDetail.thumbnail_url)})` }">
          <div class="series-hero-content">
            <h2>{{ selectedVideoDetail.title }}</h2>
            <p v-if="selectedVideoDetail.release_year">{{ selectedVideoDetail.release_year }}</p>
            <p v-if="selectedVideoDetail.description" class="series-description">{{ selectedVideoDetail.description }}</p>
            <div class="meta-info">
              <p v-if="selectedVideoDetail.director"><strong>Director:</strong> {{ selectedVideoDetail.director }}</p>
              <p v-if="selectedVideoDetail.cast"><strong>Cast:</strong> 
                <span v-for="(actor, index) in selectedVideoDetail.cast.split(', ')" :key="actor" class="actor-link" @click="searchByActor(actor)">
                  {{ actor }}{{ index < selectedVideoDetail.cast.split(', ').length - 1 ? ', ' : '' }}
                </span>
              </p>
            </div>
            <div v-if="selectedVideoDetail.trailer_url" class="trailer-container">
               <iframe :src="selectedVideoDetail.trailer_url" frameborder="0" allowfullscreen></iframe>
            </div>
            <div class="modal-actions" style="margin-top: 20px;">
              <button class="btn-netflix" @click="openPlayer(selectedVideoDetail.id, selectedVideoDetail.title); selectedVideoDetail = null">
                <span>▶</span> Play Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="selectedVideoUrl" class="player-overlay" @click.self="closePlayer">
      <div class="player-container glass">
        <VideoPlayer 
          :video-src="selectedVideoUrl" 
          :video-title="selectedVideoTitle" 
          :video-id="selectedVideoId" 
          @close="closePlayer" 
          @play-next="playNextEpisode"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import VideoRow from '../components/VideoRow.vue'
import VideoPlayer from '../components/VideoPlayer.vue'

const router = useRouter()
const route = useRoute()
const API_BASE = import.meta.env.VITE_API_BASE

const getImageUrl = (url, width) => {
  if (!url) return ''
  const baseUrl = url.startsWith('http') ? url : `${API_BASE}${url}`
  const separator = baseUrl.includes('?') ? '&' : '?'
  return width ? `${baseUrl}${separator}w=${width}` : baseUrl
}
const profileId = ref(localStorage.getItem('profile_id'))
const profileName = ref(localStorage.getItem('profile_name') || 'User')
const profileCategory = ref(localStorage.getItem('profile_category') || 'adult')
const videos = ref([])
const loading = ref(true)
const selectedVideoUrl = ref(null)
const selectedVideoId = ref(null)
const selectedVideoTitle = ref(null)
const selectedSeries = ref(null)
const isScrolled = ref(false)
const hideTimer = ref(null)
const isUiHidden = ref(false)
const showDropdown = ref(false)
const isMobile = ref(window.innerWidth <= 768)

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
}
const selectedVideoDetail = ref(null)

const currentTheme = ref(localStorage.getItem('profile_theme') || 'midnight')
const searchQuery = ref('')
const searchRef = ref(null)

// Ambilight Logic
const currentAmbientColor = ref('rgb(20, 20, 20)')
const ambientColorOpacity = ref(0.4)

let colorDebounce = null
const handleHover = (video) => {
  if (colorDebounce) clearTimeout(colorDebounce)
  colorDebounce = setTimeout(() => {
    if (video.dominant_color) {
      currentAmbientColor.value = video.dominant_color
    }
  }, 50)
}

const ambientStyles = computed(() => ({
  '--ambient-glow': currentAmbientColor.value,
  '--ambient-glow-transparent': currentAmbientColor.value.replace('rgb', 'rgba').replace(')', ', 0.3)'),
  '--ambient-accent': currentAmbientColor.value.replace('rgb', 'rgba').replace(')', ', 0.8)')
}))

// Keyboard Navigation
const focusedRowIndex = ref(-1)
const focusedItemIndex = ref(-1)

const visibleRows = computed(() => {
  const rows = []
  if (filteredVideos.value.continue_watching?.length && !searchQuery.value) {
    rows.push({ title: 'Continue Watching', videos: filteredVideos.value.continue_watching })
  }
  if (showMovies.value && filteredVideos.value.movies?.length) {
    rows.push({ title: 'Movies', videos: filteredVideos.value.movies })
  }
  if (showTvShows.value && filteredVideos.value.tv_shows?.length) {
    rows.push({ title: 'TV Shows', videos: filteredVideos.value.tv_shows })
  }
  if (showAnime.value && filteredVideos.value.anime?.length) {
    rows.push({ title: 'Anime', videos: filteredVideos.value.anime })
  }
  if (showAll.value && filteredVideos.value.all?.length) {
    rows.push({ title: 'Trending Now', videos: filteredVideos.value.all.slice().reverse() })
    rows.push({ title: 'Recently Added', videos: filteredVideos.value.all })
  }
  return rows
})

const getFocusedIndex = (title) => {
  const rowIndex = visibleRows.value.findIndex(r => r.title === title)
  return focusedRowIndex.value === rowIndex ? focusedItemIndex.value : -1
}

const handleKeydown = (e) => {
  // If typing in search, only ESC should work for blur
  if (document.activeElement === searchRef.value && e.key !== 'Escape' && e.key !== 'Enter') return

  if (e.key === '/') {
    e.preventDefault()
    searchRef.value.focus()
    focusedRowIndex.value = -1
    focusedItemIndex.value = -1
    return
  }

  if (e.key === 'Escape') {
    if (document.activeElement === searchRef.value) {
      searchRef.value.blur()
    } else if (selectedVideoUrl.value) {
      closePlayer()
    } else if (selectedSeries.value) {
      selectedSeries.value = null
    } else if (selectedVideoDetail.value) {
      selectedVideoDetail.value = null
    } else {
      focusedRowIndex.value = -1
      focusedItemIndex.value = -1
    }
    return
  }

  // Modals handle their own or block
  if (selectedVideoUrl.value || selectedSeries.value || selectedVideoDetail.value) return

  switch (e.key) {
    case 'ArrowRight':
      if (focusedRowIndex.value === -1) {
        focusedRowIndex.value = 0
        focusedItemIndex.value = 0
      } else {
        const row = visibleRows.value[focusedRowIndex.value]
        if (row && focusedItemIndex.value < row.videos.length - 1) {
          focusedItemIndex.value++
        }
      }
      break
    case 'ArrowLeft':
      if (focusedRowIndex.value !== -1 && focusedItemIndex.value > 0) {
        focusedItemIndex.value--
      }
      break
    case 'ArrowDown':
      if (focusedRowIndex.value < visibleRows.value.length - 1) {
        focusedRowIndex.value++
        // Try to keep same index or clamp
        const nextRow = visibleRows.value[focusedRowIndex.value]
        if (focusedItemIndex.value >= nextRow.videos.length) {
          focusedItemIndex.value = nextRow.videos.length - 1
        }
        if (focusedItemIndex.value === -1) focusedItemIndex.value = 0
      }
      break
    case 'ArrowUp':
      if (focusedRowIndex.value > 0) {
        focusedRowIndex.value--
        const prevRow = visibleRows.value[focusedRowIndex.value]
        if (focusedItemIndex.value >= prevRow.videos.length) {
          focusedItemIndex.value = prevRow.videos.length - 1
        }
      } else if (focusedRowIndex.value === 0) {
        focusedRowIndex.value = -1
        focusedItemIndex.value = -1
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
      break
    case 'Enter':
      if (focusedRowIndex.value !== -1 && focusedItemIndex.value !== -1) {
        const item = visibleRows.value[focusedRowIndex.value].videos[focusedItemIndex.value]
        handleVideoClick(item)
      }
      break
    case ' ':
      if (focusedRowIndex.value !== -1 && focusedItemIndex.value !== -1) {
        e.preventDefault()
        const item = visibleRows.value[focusedRowIndex.value].videos[focusedItemIndex.value]
        if (item.type === 'show') {
           handleVideoClick(item)
        } else {
           openPlayer(item.id, item.title)
        }
      }
      break
  }

  // Update Ambilight based on new selection
  if (focusedRowIndex.value !== -1 && focusedItemIndex.value !== -1) {
    const video = visibleRows.value[focusedRowIndex.value].videos[focusedItemIndex.value]
    if (video) handleHover(video)
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
  hideTimer.value = setTimeout(() => {
    isUiHidden.value = true
  }, 3000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
  stopBillboardTimer()
  if (trailerHoverTimer.value) clearTimeout(trailerHoverTimer.value)
  if (hideTimer.value) clearTimeout(hideTimer.value)
})

// Billboard Carousel & Trailer Peek
const currentBillboardIndex = ref(0)
const billboardTimer = ref(null)
const isBillboardHovered = ref(false)
const showTrailer = ref(false)
const trailerHoverTimer = ref(null)
const billboardItems = computed(() => {
  const items = []
  
  // Helper to identify messy filenames that shouldn't pollute the tight mobile UX
  const isMessyFilename = (title) => {
    if (!title) return true
    const messyRegex = /\[.*\]|1080p|720p|AnimePahe|SubsPlease|Erai-raws|HEVC|x265|bluray|WEB-DL/i
    return messyRegex.test(title)
  }

  // Filter lists, explicitly removing messy titles on mobile (unless they have premium backdrops)
  const filterBillboardVids = (vids) => {
      if (!vids) return []
      return vids.filter(v => {
          if (v.backdrop_url) return true // Has premium art, safe to show
          if (isMobile.value && isMessyFilename(v.title)) return false // Hide messy titles on mobile
          return true 
      })
  }

  // Prefer items with backdrops for the billboard
  const validMovies = filterBillboardVids(videos.value.movies || [])
  const validShows = filterBillboardVids(videos.value.tv_shows || [])
  
  const moviesWithBackdrop = validMovies.filter(v => v.backdrop_url)
  const showsWithBackdrop = validShows.filter(v => v.backdrop_url)
  
  if (moviesWithBackdrop.length) items.push(...moviesWithBackdrop.slice(0, 3))
  else if (validMovies.length) items.push(...validMovies.slice(0, 3))
  
  if (showsWithBackdrop.length) items.push(...showsWithBackdrop.slice(0, 2))
  else if (validShows.length) items.push(...validShows.slice(0, 2))
  
  const finalItems = items.length > 0 ? items : (filterBillboardVids(videos.value.all) || [])
  return finalItems.slice(0, 5)
})
const currentBillboard = computed(() => billboardItems.value[currentBillboardIndex.value] || null)

const startBillboardTimer = () => {
    stopBillboardTimer()
    billboardTimer.value = setInterval(() => {
        if (!isBillboardHovered.value) {
            nextBillboardSlide()
        }
    }, 8000) // 8 seconds per slide
}

const stopBillboardTimer = () => {
    if (billboardTimer.value) clearInterval(billboardTimer.value)
}

const nextBillboardSlide = () => {
    if (!billboardItems.value.length) return
    currentBillboardIndex.value = (currentBillboardIndex.value + 1) % billboardItems.value.length
    showTrailer.value = false
}

const handleBillboardMouseEnter = () => {
    isBillboardHovered.value = true
    if (currentBillboard.value?.trailer_url) {
        trailerHoverTimer.value = setTimeout(() => {
            if (isBillboardHovered.value) {
                showTrailer.value = true
            }
        }, 2000) // 2 second delay for peek
    }
}

const handleBillboardMouseLeave = () => {
    isBillboardHovered.value = false
    showTrailer.value = false
    if (trailerHoverTimer.value) clearTimeout(trailerHoverTimer.value)
}

// Watch for library changes to start timer
watch(videos, (newVal) => {
    if (newVal.all?.length && !billboardTimer.value) {
        startBillboardTimer()
    }
}, { immediate: true })

onUnmounted(() => {
    stopBillboardTimer()
    if (trailerHoverTimer.value) clearTimeout(trailerHoverTimer.value)
})

const showMovies = computed(() => route.path === '/library' || route.path === '/movies')
const showTvShows = computed(() => route.path === '/library' || route.path === '/tv-shows')
const showAnime = computed(() => route.path === '/library' || route.path === '/anime')
const showAll = computed(() => route.path === '/library')

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const switchProfile = () => {
  router.push('/')
}

const rescanLibrary = async () => {
  try {
    loading.value = true
    await fetch(`${API_BASE}/scan`, { method: 'POST' })
    const response = await fetch(`${API_BASE}/library?profile_id=${profileId.value}`)
    videos.value = await response.json()
    alert('Library scan completed!')
  } catch (error) {
    console.error('Error rescanning library:', error)
    alert('Failed to rescan library.')
  } finally {
    loading.value = false
    showDropdown.value = false
  }
}

const logout = () => {
  localStorage.clear()
  router.push('/')
}

const featuredVideo = computed(() => currentBillboard.value)
const profiles = ref([])

const profileAvatar = computed(() => {
  const currentProfile = profiles.value.find(p => p.id == profileId.value)
  return currentProfile ? currentProfile.avatar_url : ''
})

const libraryTitle = computed(() => {
  return `${profileCategory.value.toUpperCase()} LIBRARY`
})



const seriesHeroStyle = computed(() => {
  if (!selectedSeries.value) return {}
  const imgUrl = selectedSeries.value.backdrop_url || selectedSeries.value.thumbnail_url
  if (!imgUrl) return {}
  return {
    backgroundImage: `linear-gradient(to top, var(--bg-dark), transparent), url(${getImageUrl(imgUrl)})`
  }
})

const searchByActor = (actor) => {
  searchQuery.value = actor
  selectedSeries.value = null
  selectedVideoDetail.value = null
  // Scroll to search or top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const filteredVideos = computed(() => {
  if (!searchQuery.value) return videos.value
  
  const query = searchQuery.value.toLowerCase()
  const filterGroup = (group) => group?.filter(item => 
    item.title?.toLowerCase().includes(query) || 
    item.cast?.toLowerCase().includes(query) ||
    item.director?.toLowerCase().includes(query)
  ) || []

  return {
    movies: filterGroup(videos.value.movies),
    tv_shows: filterGroup(videos.value.tv_shows),
    anime: filterGroup(videos.value.anime),
    all: filterGroup(videos.value.all),
    continue_watching: videos.value.continue_watching // Usually don't filter this
  }
})

onMounted(async () => {
  window.addEventListener('scroll', handleScroll)
  
  // Fetch profiles for the switcher/avatar
  try {
    const pRes = await fetch(`${API_BASE}/profiles`)
    profiles.value = await pRes.json()
  } catch (err) {
    console.error('Failed to fetch profiles:', err)
  }

  fetchLibrary()
})

const fetchLibrary = async () => {
  try {
    const response = await fetch(`${API_BASE}/library?profile_id=${profileId.value}`)
    const data = await response.json()
    videos.value = data
  } catch (error) {
    console.error('Error fetching library:', error)
  } finally {
    loading.value = false
  }
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20
}

const handleVideoClick = (video) => {
  // Sync keyboard focus to the clicked item
  const rowIndex = visibleRows.value.findIndex(r => r.videos.some(v => v.id === video.id))
  if (rowIndex !== -1) {
    const itemIndex = visibleRows.value[rowIndex].videos.findIndex(v => v.id === video.id)
    focusedRowIndex.value = rowIndex
    focusedItemIndex.value = itemIndex
  }

  if (video?.type === 'show') {
    fetchSeriesDetail(video.id)
  } else {
    // Show detail modal instead of playing directly
    selectedVideoDetail.value = video
  }
}

const fetchSeriesDetail = async (seriesId) => {
  try {
    const response = await fetch(`${API_BASE}/series/${seriesId}?profile_id=${profileId.value}`)
    selectedSeries.value = await response.json()
  } catch (error) {
    console.error('Error fetching series detail:', error)
  }
}

const toggleTheme = async () => {
    const newTheme = currentTheme.value === 'midnight' ? 'cinematic' : 'midnight'
    try {
        const res = await fetch(`${API_BASE}/profiles/${profileId.value}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ theme: newTheme })
        })
        if (res.ok) {
            currentTheme.value = newTheme
            localStorage.setItem('profile_theme', newTheme)
            document.documentElement.setAttribute('data-theme', newTheme)
        }
    } catch (err) {
        console.error('Failed to toggle theme:', err)
    }
}

const openPlayer = (videoId, title) => {
  selectedVideoTitle.value = title
  selectedVideoId.value = videoId
  selectedVideoUrl.value = `${API_BASE}/stream/${videoId}?profile_id=${profileId.value}`
}

const playNextEpisode = (nextVideo) => {
  if (!nextVideo) {
    closePlayer()
    return
  }
  openPlayer(nextVideo.id, nextVideo.title)
}

const closePlayer = () => {
  selectedVideoUrl.value = null
  selectedVideoId.value = null
  selectedVideoTitle.value = null
  // Refetch library directly after closing to instantly update continue watching row
  fetchLibrary()
}
</script>

<style scoped>
.series-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2500;
  backdrop-filter: blur(15px);
}

.series-modal {
  width: 95%;
  max-width: 1000px;
  max-height: 95vh;
  background: var(--bg-dark);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}

@media (max-width: 600px) {
  .series-modal { width: 100%; height: 100%; max-height: 100vh; border-radius: 0; }
  .series-hero { height: 250px; padding: 20px; }
  .series-hero-content h2 { font-size: 1.8rem; }
  .episodes-list { padding: 20px; }
  .episode-item { flex-direction: column; gap: 10px; }
  .ep-thumb { width: 100%; height: auto; aspect-ratio: 16/9; }
}

.close-modal {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: #fff;
  font-size: 2rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.series-hero {
  height: 400px;
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: 40px;
}

.series-hero-content h2 {
  font-size: 3rem;
  margin: 0;
  text-shadow: 0 2px 10px rgba(0,0,0,0.8);
}

.series-description {
  margin-top: 15px;
  font-size: 1.1rem;
  line-height: 1.5;
  color: #ccc;
  max-width: 600px;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.episodes-list {
  padding: 40px;
}

.episodes-list h3 {
  margin-top: 0;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--netflix-red);
  display: inline-block;
  padding-bottom: 5px;
}

.episode-item {
  display: flex;
  gap: 20px;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.episode-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(10px);
}

.ep-thumb {
  width: 150px;
  aspect-ratio: 16/9;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.ep-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ep-play-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.8);
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

.ep-play-btn svg {
  width: 20px;
  height: 20px;
  margin-left: 3px; /* visually center play triangle */
}

.episode-item:hover .ep-play-btn {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.ep-play-btn:hover {
  background: var(--netflix-red);
  border-color: var(--netflix-red);
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 0 20px var(--netflix-red);
}

.ep-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}

.ep-badge {
  font-size: 0.7rem;
  font-weight: 800;
  color: #fff;
  background: var(--netflix-red);
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  align-self: flex-start;
  letter-spacing: 0.05em;
}

.ep-title {
  font-weight: 600;
  margin: 0;
  color: #e5e5e5;
  font-size: 1.1rem;
}

.ep-meta {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.library-container {
  min-height: 100vh;
  background-color: var(--bg-dark);
  position: relative;
}

.netflix-nav {
  position: fixed;
  top: 0;
  width: 100%;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4vw;
  z-index: 1000; /* Increased z-index */
  transition: background-color 0.4s;
  background-image: linear-gradient(to bottom, rgba(0,0,0,0.7) 10%, rgba(0,0,0,0)); /* Gradient for better logo visibility */
  box-sizing: border-box;
}

.netflix-nav.scrolled {
  background-color: var(--bg-dark);
  background-image: none;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 2vw;
}

.logo {
  color: var(--netflix-red);
  font-size: 1.8rem;
  margin: 0;
  cursor: pointer;
}

.logo span { color: #fff; }

.nav-links {
  display: flex;
  list-style: none;
  gap: 1.2vw;
  margin: 0;
  padding: 0;
}

@media (max-width: 1024px) {
  .nav-links { display: none; } 
  .logo { font-size: 1.4rem; }
}

@media (max-width: 600px) {
  .search-input { width: 100px; }
  .nav-right { gap: 10px; }
}

.nav-links li {
  font-size: 0.85rem;
  color: #e5e5e5;
  cursor: pointer;
  transition: color 0.2s;
}

.nav-links li:hover {
  color: #b3b3b3;
}

.nav-links li.active {
  font-weight: 700;
  color: #fff;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1.5vw;
}

@media (max-width: 768px) {
  .nav-right { gap: 4vw; }
}

.profile-box {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.nav-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nav-icon {
  width: 24px;
  height: 24px;
  color: #fff;
  cursor: pointer;
}

.search-box, .notifications {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
}

.user-profile {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-profile:hover {
  background: rgba(255, 255, 255, 0.1);
}

.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 280px;
  margin-top: 15px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
  z-index: 2000;
  animation: slideDown 0.3s ease-out;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.dropdown-avatar {
  width: 50px;
  height: 50px;
  border-radius: 4px;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
}

.dropdown-username {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: #fff;
}

.dropdown-category {
  font-size: 0.8rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 5px 0;
}

.dropdown-menu {
  list-style: none;
  padding: 10px 0;
  margin: 0;
}

.dropdown-menu li {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.95rem;
  color: #e5e5e5;
  transition: all 0.2s;
}

.dropdown-menu li svg {
  width: 20px;
  height: 20px;
  opacity: 0.7;
}

.dropdown-menu li:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.dropdown-menu li:hover svg {
  opacity: 1;
  color: var(--neon-cyan);
}

.dropdown-menu li.logout {
  font-weight: 600;
  color: #fff;
}

.dropdown-menu li.logout:hover {
  text-decoration: underline;
  background: transparent;
}

.caret {
  font-size: 0.6rem;
  color: #fff;
  transition: transform 0.3s;
}

.caret.open {
  transform: rotate(180deg);
}

/* Billboard Section */
.billboard {
  position: relative;
  height: 56.25vw;
  width: 100%;
  margin-bottom: -12vw; /* Reduced negative margin to push rows down */
}

@media (max-width: 1100px) {
  .billboard { height: 70vw; margin-bottom: -8vw; }
}

@media (max-width: 768px) {
  .billboard { height: 140vw; margin-bottom: 0px; }
  .billboard-background { background-position: center top; }
  
  /* Make vignette stronger at bottom to support centered text */
  .vignette {
    background: linear-gradient(to top, var(--bg-dark) 0%, rgba(0,0,0,0.7) 20%, transparent 60%);
  }
}

.billboard-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center 10%;
  z-index: 1;
  transition: opacity 1.2s ease;
  animation: kenBurns 20s infinite alternate linear;
}

@keyframes kenBurns {
  0% { transform: scale(1) translate(0, 0); }
  50% { transform: scale(1.1) translate(-1%, -1%); }
  100% { transform: scale(1) translate(0, 0); }
}

.billboard-content-wrapper {
  position: absolute;
  top: 25%;
  left: 4vw;
  z-index: 10;
  max-width: 45%;
}

@media (max-width: 768px) {
  .billboard-content-wrapper { 
    top: auto;
    bottom: 25vw;
    left: 0;
    width: 100%;
    max-width: 100%; 
    padding: 0 5vw;
    display: flex;
    flex-direction: column;
    align-items: center; /* Center everything */
    text-align: center;
  }
  .featured-desc { display: none; } /* Hide description to let art breathe */
  
  .billboard-meta { justify-content: center; } /* Center tags */
  
  .btn-play, .btn-info { padding: 12px 24px; font-size: 1.1rem; border-radius: 20px; }
  .billboard-actions { justify-content: center; width: 100%; }
}

.floating-content {
  color: #fff;
  animation: contentFadeIn 1s ease-out;
}

@keyframes contentFadeIn {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}

.billboard-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.meta-badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.meta-badge.trending {
  background: rgba(255, 69, 58, 0.2);
  color: #ff453a;
  border: 1px solid rgba(255, 69, 58, 0.3);
}

.meta-badge.new {
  background: rgba(48, 209, 88, 0.2);
  color: #30d158;
  border: 1px solid rgba(48, 209, 88, 0.3);
}

.meta-badge.quality {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.featured-title {
  font-size: clamp(2.5rem, 10vw, 5rem);
  font-weight: 900;
  margin-bottom: 2vw;
  line-height: 1.1;
  letter-spacing: -1px;
  text-shadow: 0 4px 30px rgba(0,0,0,0.8);
  font-family: 'Outfit', sans-serif;
}

.featured-desc {
  font-size: 1.2rem;
  max-width: 600px;
  color: rgba(255,255,255,0.9);
  text-shadow: 0 2px 10px rgba(0,0,0,0.5);
  margin-bottom: 2.5vw;
  line-height: 1.4;
}

.billboard-actions {
  display: flex;
  gap: 15px;
}

.btn-play, .btn-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-play {
  background: #fff;
  color: #000;
}

.btn-play:hover {
  background: rgba(255,255,255,0.8);
  transform: scale(1.05);
}

.btn-play svg, .btn-info svg {
  width: 24px;
  height: 24px;
}

.btn-info {
  background: rgba(109, 109, 110, 0.7);
  color: #fff;
  backdrop-filter: blur(10px);
}

.btn-info:hover {
  background: rgba(109, 109, 110, 0.5);
  transform: scale(1.05);
}

/* Redesigned Next-Up Strip */
.billboard-nav-strip {
  position: absolute;
  bottom: 10vw;
  right: 4vw;
  display: flex;
  gap: 24px;
  z-index: 20;
}

@media (max-width: 768px) {
  .billboard-nav-strip {
    bottom: 4vw;
    right: 0;
    left: 0;
    padding-left: 50vw; /* Trick to allow scrolling the first item past the edge */
    gap: 15px;
    overflow-x: auto;
    padding-bottom: 15px;
    padding-right: 50vw;
    mask-image: linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%);
    scrollbar-width: none;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
  }
  .billboard-nav-strip::-webkit-scrollbar {
    display: none;
  }
}

.nav-strip-item {
  width: 140px;
  flex: 0 0 auto; /* Prevent shrinking in flex container */
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.25, 1, 0.5, 1);
  opacity: 0.5;
  filter: grayscale(1);
}

@media (max-width: 768px) {
  .nav-strip-item { width: 80px; scroll-snap-align: center; }
  .nav-strip-item.active { width: 140px; }
}

.nav-strip-item:hover {
  opacity: 1;
  transform: translateY(-10px);
  filter: grayscale(0);
}

.nav-strip-item.active {
  width: 200px;
  opacity: 1;
  filter: grayscale(0);
}

.nav-poster-mini {
  aspect-ratio: 16/9;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  background: #111;
  border: 1px solid rgba(255,255,255,0.05);
}

.nav-strip-item.active .nav-poster-mini {
  border: 3px solid #fff;
  box-shadow: 0 10px 40px rgba(0,0,0,0.8);
}

.nav-poster-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nav-timer {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 4px;
  background: #fff;
  width: 100%;
  animation: stripProgress 8s linear;
}

@keyframes stripProgress {
  from { width: 0; }
  to { width: 100%; }
}

.vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to top, var(--bg-dark) 0%, transparent 40%),
              linear-gradient(to right, var(--bg-dark) 0%, rgba(10,10,10,0.4) 40%, transparent 100%);
  z-index: 3;
}

@media (max-width: 768px) {
  .featured-title { font-size: 2rem; }
}

.featured-desc {
  font-size: clamp(1rem, 1.2vw, 1.5rem);
  color: #fff;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.45);
  margin-bottom: 1.5vw;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 768px) {
  .featured-desc { font-size: 0.9rem; margin-bottom: 3vw; }
}

.billboard-actions {
  display: flex;
  gap: 1rem;
}

@media (max-width: 768px) {
  .billboard-actions { justify-content: center; }
}

.library-h.series-description {
  font-size: 1.1rem;
  line-height: 1.6;
  color: var(--text-muted);
  margin-bottom: 20px;
  max-width: 800px;
}

.meta-info {
  margin-bottom: 25px;
  font-size: 0.95rem;
}

.meta-info p {
  margin: 5px 0;
  color: #ccc;
}

.actor-link {
  color: var(--neon-cyan);
  cursor: pointer;
  transition: color 0.2s;
}

.actor-link:hover {
  color: #fff;
  text-decoration: underline;
}

.trailer-container {
  margin-top: 30px;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.1);
  background: #000;
}

.trailer-container iframe {
  width: 100%;
  height: 100%;
}
.library-header {
  font-size: 2.5rem;
  font-weight: 800;
  color: #fff;
  margin-left: 4vw;
  margin-bottom: 20px;
  text-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
  position: relative;
  display: inline-block;
}

.library-header::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 60px;
  height: 4px;
  background: var(--netflix-red);
  box-shadow: 0 0 10px var(--netflix-red);
}

.content {
  position: relative;
  padding-top: 5vw;
  padding-bottom: 100px;
  z-index: 10;
}

@media (max-width: 768px) {
  .content { padding-top: 80px; }
}

.player-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(10px);
}

.player-container {
  width: 100%;
  height: 100%;
  background: #000;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

@media (max-width: 768px) {
  .nav-right { gap: 10px; } /* Tighter gap on mobile */
}

.search-box {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.search-icon {
  width: 18px;
  height: 18px;
  color: #fff;
  opacity: 0.7;
}

.search-input {
  background: transparent;
  border: none;
  color: #fff;
  padding: 0 10px;
  width: 200px;
  font-size: 0.95rem;
  outline: none;
  font-family: inherit;
  transition: width 0.3s;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.clear-search {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0.7;
  padding: 0 4px;
}

.clear-search:hover {
  opacity: 1;
}

@media (max-width: 1000px) {
  .search-input { width: 150px; }
}

@media (max-width: 768px) {
  .search-input { width: 100px; font-size: 0.85rem; } /* Prevent search bar from growing too wide */
  .search-input:focus { width: 130px; }
}
.no-results {
  text-align: center;
  padding: 100px 20px;
  width: 100%;
}

.no-results p {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: var(--text-muted);
}
/* Ambilight Halo Layer */
.ambient-halo-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 50% 30%, var(--ambient-glow-transparent) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
  transition: background 1.5s ease;
  mix-blend-mode: screen;
}

.library-container {
  transition: background 1.5s ease;
  min-height: 100vh;
  background-color: var(--bg-dark);
}

.logo span {
  color: var(--ambient-accent);
  transition: color 1s ease;
  text-shadow: 0 0 15px var(--ambient-accent);
}

.library-header::after {
  background: var(--ambient-accent);
  box-shadow: 0 0 20px var(--ambient-accent);
  transition: all 1s ease;
}

.nav-links li.active {
  color: var(--ambient-accent);
  transition: color 1s ease;
}

.meta-badge.trending {
  background: var(--ambient-accent);
  transition: background 1s ease;
}

.btn-play {
  background: #fff;
  transition: all 0.3s ease;
}

.btn-play:hover {
  background: var(--ambient-accent);
  color: #fff;
  transform: scale(1.05);
  box-shadow: 0 0 30px var(--ambient-accent);
}

.billboard-background {
  transition: background-image 0.8s ease-in-out;
}

/* Ensure row titles react too */
.row-title {
  color: #fff;
  transition: color 1s ease;
}

.video-row:hover .row-title {
  color: var(--ambient-accent);
}
</style>
