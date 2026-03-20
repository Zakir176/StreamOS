import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Library from '../views/Library.vue'
import Settings from '../views/Settings.vue'
import AccountSettings from '../views/AccountSettings.vue'

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/library', name: 'Library', component: Library },
    { path: '/movies', name: 'Movies', component: Library },
    { path: '/tv-shows', name: 'TVShows', component: Library },
    { path: '/anime', name: 'Anime', component: Library },
    { path: '/settings', name: 'Settings', component: Settings },
    { path: '/account-settings', name: 'AccountSettings', component: AccountSettings }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
