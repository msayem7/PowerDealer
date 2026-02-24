<template>
  <header class="app-header" role="banner">
    <!-- Mobile Menu Toggle -->
    <button 
      class="mobile-menu-btn"
      @click="layoutStore.toggleMobileMenu"
      :aria-label="layoutStore.isMobileMenuOpen ? 'Close menu' : 'Open menu'"
      :aria-expanded="layoutStore.isMobileMenuOpen"
    >
      <span class="hamburger-icon" :class="{ 'open': layoutStore.isMobileMenuOpen }">
        <span></span>
        <span></span>
        <span></span>
      </span>
    </button>
    
    <!-- Left: Logo and Company Name -->
    <div class="header-left">
      <router-link to="/dashboard" class="logo-link" aria-label="PowerDealer Dashboard">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="currentColor"/>
          </svg>
        </div>
        <span class="company-name">PowerDealer</span>
      </router-link>
    </div>
    
    <!-- Right: Notifications, User Menu, Logout -->
    <div class="header-right">
      <!-- Notification Bell -->
      <div class="header-action">
        <button 
          class="icon-button notification-btn"
          @click="toggleNotifications"
          :aria-label="`Notifications${layoutStore.unreadNotifications > 0 ? ` (${layoutStore.unreadNotifications} unread)` : ''}`"
          :aria-expanded="showNotifications"
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-2 1H8v-6c0-2.48 1.51-4.5 4-4.5s4 2.02 4 4.5v6z" fill="currentColor"/>
          </svg>
          <span v-if="layoutStore.unreadNotifications > 0" class="notification-badge">
            {{ layoutStore.unreadNotifications > 9 ? '9+' : layoutStore.unreadNotifications }}
          </span>
        </button>
        
        <!-- Notification Dropdown Panel -->
        <NotificationPanel 
          v-if="showNotifications"
          @close="showNotifications = false"
          @mark-all-read="layoutStore.markAllAsRead"
        />
      </div>
      
      <!-- User Avatar -->
      <div class="header-action">
        <button 
          class="user-button"
          @click="toggleUserMenu"
          :aria-label="`User menu for ${userName}`"
          :aria-expanded="showUserMenu"
        >
          <div class="user-avatar">
            <span v-if="!userAvatar">{{ userInitials }}</span>
            <img v-else :src="userAvatar" :alt="userName" />
          </div>
          <span class="user-name">{{ userName }}</span>
          <svg class="dropdown-arrow" viewBox="0 0 24 24" fill="none">
            <path d="M7 10l5 5 5-5H7z" fill="currentColor"/>
          </svg>
        </button>
        
        <!-- User Dropdown Menu -->
        <div v-if="showUserMenu" class="user-dropdown" role="menu">
          <div class="dropdown-header">
            <div class="user-avatar large">
              <span v-if="!userAvatar">{{ userInitials }}</span>
              <img v-else :src="userAvatar" :alt="userName" />
            </div>
            <div class="user-info">
              <span class="user-full-name">{{ userName }}</span>
              <span class="user-email">{{ userEmail }}</span>
            </div>
          </div>
          <div class="dropdown-divider"></div>
          <router-link to="/settings" class="dropdown-item" role="menuitem" @click="showUserMenu = false">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor"/>
            </svg>
            Profile Settings
          </router-link>
          <button class="dropdown-item logout-item" role="menuitem" @click="handleLogout">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" fill="currentColor"/>
            </svg>
            Logout
          </button>
        </div>
      </div>
    </div>
    
    <!-- Click outside handler -->
    <div 
      v-if="showUserMenu || showNotifications" 
      class="dropdown-overlay"
      @click="closeDropdowns"
    />
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLayoutStore } from '../../stores/layout'
import NotificationPanel from './NotificationPanel.vue'

const router = useRouter()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()

const showUserMenu = ref(false)
const showNotifications = ref(false)

// Computed properties for user
const userName = computed(() => {
  const user = authStore.user
  if (user?.first_name || user?.last_name) {
    return `${user.first_name} ${user.last_name}`.trim()
  }
  return user?.username || 'User'
})

const userEmail = computed(() => authStore.user?.email || '')

const userInitials = computed(() => {
  const name = userName.value
  if (name === 'User') return 'U'
  const parts = name.split(' ')
  return parts.map(p => p[0]).join('').toUpperCase().slice(0, 2)
})

const userAvatar = computed(() => authStore.user?.avatar || null)

// Toggle functions
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  if (showUserMenu.value) {
    showNotifications.value = false
  }
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    showUserMenu.value = false
  }
}

const closeDropdowns = () => {
  showUserMenu.value = false
  showNotifications.value = false
}

// Logout handler
const handleLogout = () => {
  showUserMenu.value = false
  authStore.logout()
  router.push('/login')
}

// Handle escape key
const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    closeDropdowns()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.app-header {
  grid-area: header;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-height);
  padding: 0 24px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  margin-right: 12px;
}

.hamburger-icon {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 24px;
}

.hamburger-icon span {
  display: block;
  height: 2px;
  background-color: var(--color-text-primary);
  border-radius: 1px;
  transition: all 0.2s;
}

.hamburger-icon.open span:nth-child(1) {
  transform: rotate(45deg) translate(4px, 4px);
}

.hamburger-icon.open span:nth-child(2) {
  opacity: 0;
}

.hamburger-icon.open span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* Logo Section */
.header-left {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: var(--color-text-primary);
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.company-name {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.5px;
}

/* Header Right Section */
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-action {
  position: relative;
}

/* Icon Button (Notification Bell) */
.icon-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.15s;
  position: relative;
}

.icon-button:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.icon-button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.icon-button svg {
  width: 24px;
  height: 24px;
}

/* Notification Badge */
.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: var(--color-danger);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* User Button */
.user-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px 8px 8px;
  border: none;
  background: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  color: var(--color-text-primary);
  transition: all 0.15s;
}

.user-button:hover {
  background-color: var(--color-primary-light);
}

.user-button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  overflow: hidden;
}

.user-avatar.large {
  width: 48px;
  height: 48px;
  font-size: 1rem;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.dropdown-arrow {
  width: 20px;
  height: 20px;
  color: var(--color-text-secondary);
}

/* User Dropdown */
.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 280px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 200;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background-color: var(--color-background);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-full-name {
  font-weight: 600;
  font-size: 0.9rem;
}

.user-email {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--color-border);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  color: var(--color-text-primary);
  font-size: 0.9rem;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.15s;
}

.dropdown-item:hover {
  background-color: var(--color-primary-light);
}

.dropdown-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.dropdown-item svg {
  width: 20px;
  height: 20px;
  color: var(--color-text-secondary);
}

.logout-item:hover {
  background-color: #fee;
  color: var(--color-danger);
}

.logout-item:hover svg {
  color: var(--color-danger);
}

/* Dropdown Overlay */
.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 150;
}

/* Responsive Styles */
@media (max-width: 767px) {
  .app-header {
    padding: 0 16px;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .company-name {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .dropdown-arrow {
    display: none;
  }
  
  .user-dropdown {
    width: calc(100vw - 32px);
    right: -60px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .company-name {
    display: none;
  }
}
</style>
