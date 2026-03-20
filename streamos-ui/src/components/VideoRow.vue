<template>
  <div class="video-row">
    <h2 class="row-title">{{ title }}</h2>
    
    <div class="row-container">
      <!-- Skeleton Loader -->
      <div v-if="loading" class="row-content skeleton-row">
        <div v-for="i in 6" :key="i" class="video-card skeleton-card">
          <div class="video-card-inner">
            <div class="thumbnail-wrapper skeleton-shimmer"></div>
            <div class="video-info">
              <div class="skeleton-text skeleton-shimmer title"></div>
              <div class="skeleton-text skeleton-shimmer meta"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!videos || videos.length === 0" class="row-empty">No videos found for this category.</div>
      <div v-else class="row-content" ref="rowRef">
        <div 
          v-for="(video, index) in videos" 
          :key="video.id" 
          class="video-card glass" 
          :class="{ 'focused': index === focusedIndex }"
          @click="$emit('play', video)"
          @mouseenter="emit('hover', video)"
        >
          <div class="video-card-inner">
            <div class="thumbnail-wrapper">
              <img 
                :src="`${API_BASE}${video.backdrop_url || video.thumbnail_url}`" 
                :alt="video.title"
                class="thumbnail"
                @error="onImgError"
                @load="onImgLoad(video.id)"
                loading="lazy"
                :class="{ 'loaded': loadedImgs[video.id] }"
              />
              <div class="video-card-overlay">
                <div class="play-btn-center">
                  <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5 3L19 12L5 21V3Z"/>
                  </svg>
                </div>
              </div>
              
              <!-- Progress Bar -->
              <div v-if="video.current_time && video.duration" class="video-progress-container">
                <div class="video-progress-fill" :style="{ width: (video.current_time / video.duration * 100) + '%' }"></div>
              </div>
            </div>
            <div class="video-info">
              <p class="video-show">
                <span v-if="video.type === 'show'">
                  {{ video.title }}
                </span>
                <span v-else-if="video.show_name">
                  {{ video.show_name }}
                </span>
                <span v-else>
                  {{ video.title }}
                </span>
              </p>

              <p v-if="video.type === 'episode' && video.season" class="video-episode-title">
                <span class="video-badge">S{{ video.season }}:E{{ video.episode }}</span>
                <span class="video-ep-name">{{ video.title }}</span>
              </p>
              <p v-else-if="video.release_year" class="video-meta">
                {{ video.release_year }} <span class="dot">•</span> Movie
              </p>
              <p v-else-if="video.type === 'show'" class="video-meta">
                {{ video.episodes_count }} Episodes
              </p>

              <!-- Expanded Hover Info -->
              <div class="hover-info">
                 <div class="meta-row">
                    <span class="match-score">98% Match</span>
                    <span class="age-badge">13+</span>
                    <span class="duration" v-if="video.duration">{{ Math.floor(video.duration / 60) }}m</span>
                 </div>
                 <div class="tag-row">
                    <span>Exciting</span>
                    <span class="dot">•</span>
                    <span>Cinematic</span>
                 </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE

const props = defineProps({
  title: String,
  videos: Array,
  profileId: [String, Number],
  loading: Boolean,
  focusedIndex: Number
})

const emit = defineEmits(['play', 'hover'])

const rowRef = ref(null)

const loadedImgs = ref({})
const onImgLoad = (id) => {
  loadedImgs.value[id] = true
}

const onImgError = (e) => {
  e.target.src = 'https://placehold.co/600x400/1e293b/f8fafc?text=No+Thumbnail'
}

import { watch, nextTick } from 'vue'
watch(() => props.focusedIndex, async (newIndex) => {
  if (newIndex !== undefined && newIndex !== -1 && rowRef.value) {
    await nextTick()
    const card = rowRef.value.children[newIndex]
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
    }
  }
})
</script>

<style scoped>
.video-row {
  margin-bottom: 3vw;
  padding: 0 4vw;
  position: relative;
  z-index: 5; /* Ensure rows are below nav but above billboard background */
}

@media (max-width: 1100px) {
  .video-row { padding: 0 4vw; }
}

@media (max-width: 768px) {
  .video-row { padding: 0 4vw; margin-bottom: 20px; }
}

.row-title {
  font-size: 1.4vw;
  color: #e5e5e5;
  font-weight: 700;
  margin-bottom: 0.5em;
  transition: color 0.2s;
}

@media (max-width: 1100px) {
  .row-title { font-size: 1.5rem; }
}

@media (max-width: 600px) {
  .row-title { font-size: 1.1rem; margin-bottom: 0.3em; }
}

.row-container {
  position: relative;
  overflow: visible;
}

.row-content {
  display: flex;
  gap: 0.5vw;
  overflow-x: scroll;
  overflow-y: visible;
  padding: 1vw 0;
  scrollbar-width: none;
}

.row-content::-webkit-scrollbar {
  display: none;
}

.row-loading, .row-empty {
  padding: 2vw 0;
  color: #666;
  font-style: italic;
}

/* Skeleton Shimmer Styles */
.skeleton-row {
  overflow: hidden !important;
}

.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-text {
  height: 12px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-text.title { width: 80%; height: 16px; }
.skeleton-text.meta { width: 40%; }

.video-card {
  flex: 0 0 16.666%; /* Default 6 per row */
  min-width: 0;
  position: relative;
  cursor: pointer;
  transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  transform-origin: center;
  z-index: 1;
}

@media (max-width: 1400px) {
  .video-card { flex: 0 0 20%; } /* 5 per row */
}

@media (max-width: 1100px) {
  .video-card { flex: 0 0 25%; } /* 4 per row */
}

@media (max-width: 800px) {
  .video-card { flex: 0 0 33.333%; } /* 3 per row */
}

@media (max-width: 500px) {
  .video-card { flex: 0 0 48%; } /* 2 per row approx */
}

.video-card:hover, .video-card.focused {
  transform: scale(1.1);
  z-index: 10;
}

.video-card.focused {
  outline: 3px solid var(--neon-cyan);
  box-shadow: 0 0 20px var(--neon-cyan);
}

.video-card-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.thumbnail-wrapper {
  position: relative;
  aspect-ratio: 16/9;
  border-radius: var(--radius-main);
  overflow: hidden;
  background: #1a1a1a;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.video-card:hover .thumbnail-wrapper {
  box-shadow: 0 8px 15px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.1);
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.6s ease, transform 0.5s ease;
  opacity: 0; /* Hidden until loaded for blur-up effect */
}

.thumbnail.loaded {
  opacity: 1;
}

.video-card:hover .thumbnail {
  transform: scale(1.05);
}

/* Hover Info Expansion */
.hover-info {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: all 0.3s ease;
  padding-top: 0;
}

.video-card:hover .hover-info, .video-card.focused .hover-info {
  max-height: 100px;
  opacity: 1;
  padding-top: 8px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.75rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.match-score { color: #46d369; }
.age-badge { 
  border: 1px solid rgba(255,255,255,0.4);
  padding: 0 4px;
  font-size: 0.65rem;
}

.tag-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  color: #fff;
}

.video-card-overlay {
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
  transition: opacity 0.3s;
}

.video-card:hover .video-card-overlay, .video-card.focused .video-card-overlay {
  opacity: 1;
}

/* On mobile, usually better to keep it simpler OR always show some info if not hovered */
@media (max-width: 768px) {
  .video-card:hover, .video-card.focused {
    transform: none; /* Scaling on mobile can be messy if items are close */
  }
}

.play-btn-center {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  transform: scale(0.8) translateY(10px);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
  box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

.play-btn-center svg {
  width: 24px;
  height: 24px;
  margin-left: 4px; /* visually center play triangle */
}

.video-card:hover .play-btn-center, .video-card.focused .play-btn-center {
  opacity: 1;
  transform: scale(1) translateY(0);
}

.play-btn-center:hover {
  background: var(--netflix-red);
  border-color: var(--netflix-red);
  transform: translate(-50%, -50%) scale(1.1);
  box-shadow: 0 0 20px var(--netflix-red);
}

.video-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 4px;
}

.video-show {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.02em;
}

.video-meta {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 500;
  color: #a3a3a3;
  letter-spacing: 0.03em;
}

.video-episode-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.video-badge {
  font-size: 0.65rem;
  font-weight: 700;
  color: #fff;
  background: var(--netflix-red);
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.video-ep-name {
  font-size: 0.8rem;
  font-weight: 500;
  color: #a3a3a3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dot {
  padding: 0 0.25rem;
}

.video-progress-container {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  z-index: 5;
}

.video-progress-fill {
  height: 100%;
  background: var(--netflix-red);
  box-shadow: 0 0 10px var(--netflix-red);
}
</style>
