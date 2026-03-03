<template>
  <div 
    class="app-layout"
    :class="{ 
      'sidebar-collapsed': layoutStore.isSidebarCollapsed,
      'mobile-menu-open': layoutStore.isMobileMenuOpen,
      'no-sidebar': authStore.isCustomer
    }"
  >
    <!-- Global Header -->
    <AppHeader />
    
    <!-- Collapsible Navigation Sidebar (hidden for customer users) -->
    <NavSidebar v-if="!authStore.isCustomer" />
    
    <!-- Main Content Area -->
    <main class="main-content" role="main">
      <!-- Skip to main content link for accessibility -->
      <a href="#main-content" class="skip-link">Skip to main content</a>
      
      <div id="main-content" class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
    
    <!-- Mobile Overlay -->
    <div 
      v-if="layoutStore.isMobileMenuOpen"
      class="mobile-overlay"
      @click="layoutStore.closeMobileMenu"
      aria-hidden="true"
    />
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useLayoutStore } from '../../stores/layout'
import { useAuthStore } from '../../stores/auth'
import AppHeader from './AppHeader.vue'
import NavSidebar from './NavSidebar.vue'

const layoutStore = useLayoutStore()
const authStore = useAuthStore()

// Handle responsive sidebar on window resize
const handleResize = () => {
  const width = window.innerWidth
  
  if (width < 768) {
    // Mobile: force collapsed
    if (!layoutStore.isSidebarCollapsed) {
      layoutStore.setSidebarCollapsed(true)
    }
  } else if (width >= 768 && width < 1024) {
    // Tablet: collapsed by default
    if (!layoutStore.isSidebarCollapsed) {
      layoutStore.setSidebarCollapsed(true)
    }
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style>
/* CSS Custom Properties */
:root {
  --header-height: 64px;
  --sidebar-width-expanded: 240px;
  --sidebar-width-collapsed: 64px;
  
  --color-primary: #1976d2;
  --color-primary-dark: #1565c0;
  --color-primary-light: #e3f2fd;
  --color-surface: #ffffff;
  --color-background: #f5f5f5;
  --color-text-primary: #212121;
  --color-text-secondary: #757575;
  --color-border: #e0e0e0;
  --color-active-bg: #e3f2fd;
  --color-active-border: #1976d2;
  --color-danger: #dc3545;
  --color-danger-hover: #c82333;
  
  --transition-duration: 200ms;
  --transition-timing: ease-in-out;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
}

/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
    Cantarell, 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

/* App Layout */
.app-layout {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main";
  grid-template-columns: var(--sidebar-width-expanded) 1fr;
  grid-template-rows: var(--header-height) 1fr;
  min-height: 100vh;
  transition: grid-template-columns var(--transition-duration) var(--transition-timing);
}

/* Collapsed Sidebar State */
.app-layout.sidebar-collapsed {
  grid-template-columns: var(--sidebar-width-collapsed) 1fr;
}

/* No Sidebar State (for customer users) */
.app-layout.no-sidebar {
  grid-template-columns: 0 1fr;
}

.app-layout.no-sidebar.sidebar-collapsed {
  grid-template-columns: 0 1fr;
}

/* Main Content Area */
.main-content {
  grid-area: main;
  overflow-y: auto;
  background-color: var(--color-background);
}

.content-wrapper {
  padding: 24px;
  min-height: calc(100vh - var(--header-height));
}

/* Skip Link for Accessibility */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary);
  color: white;
  padding: 8px 16px;
  z-index: 1000;
  text-decoration: none;
  border-radius: 0 0 4px 0;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}

/* Mobile Overlay */
.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 90;
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Styles */
@media (max-width: 767px) {
  .app-layout {
    grid-template-columns: 0 1fr;
  }
  
  .app-layout.sidebar-collapsed {
    grid-template-columns: 0 1fr;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .mobile-overlay {
    display: block;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .app-layout {
    grid-template-columns: var(--sidebar-width-collapsed) 1fr;
  }
  
  .app-layout:not(.sidebar-collapsed) {
    grid-template-columns: var(--sidebar-width-expanded) 1fr;
  }
}
</style>
