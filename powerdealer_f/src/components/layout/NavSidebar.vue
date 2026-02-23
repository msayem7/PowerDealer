<template>
  <aside 
    class="nav-sidebar"
    :class="{ 
      'collapsed': layoutStore.isSidebarCollapsed,
      'mobile-open': layoutStore.isMobileMenuOpen 
    }"
    role="navigation"
    aria-label="Main navigation"
  >
    <!-- Toggle Button -->
    <button 
      class="sidebar-toggle"
      @click="layoutStore.toggleSidebar"
      :aria-label="layoutStore.isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
    >
      <svg viewBox="0 0 24 24" fill="none" class="toggle-icon">
        <path 
          d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12l4.58-4.59z" 
          fill="currentColor"
          :class="{ 'rotated': layoutStore.isSidebarCollapsed }"
        />
      </svg>
    </button>
    
    <!-- Navigation Container -->
    <nav class="sidebar-nav">
      <!-- Primary Navigation Group -->
      <div class="nav-group">
        <span 
          v-if="!layoutStore.isSidebarCollapsed" 
          class="nav-group-title"
        >
          Primary
        </span>
        
        <ul class="nav-list" role="menubar">
          <!-- Dashboard -->
          <li role="none">
            <router-link 
              to="/dashboard" 
              class="nav-item"
              :class="{ 'active': isActiveRoute('/dashboard') }"
              role="menuitem"
              :aria-current="isActiveRoute('/dashboard') ? 'page' : undefined"
              @click="handleNavClick"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="currentColor"/>
                </svg>
              </span>
              <span v-if="!layoutStore.isSidebarCollapsed" class="nav-label">Dashboard</span>
            </router-link>
          </li>
          
          <!-- Transactions (with sub-items) -->
          <li role="none" class="nav-item-group-container">
            <button 
              class="nav-item"
              :class="{ 
                'active': isActiveRoute('/transactions') || isActiveRoute('/customers'),
                'expanded': transactionsExpanded 
              }"
              role="menuitem"
              :aria-expanded="transactionsExpanded"
              :aria-haspopup="true"
              @click="toggleTransactions"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" fill="currentColor"/>
                </svg>
              </span>
              <span v-if="!layoutStore.isSidebarCollapsed" class="nav-label">Transactions</span>
              <svg 
                v-if="!layoutStore.isSidebarCollapsed" 
                viewBox="0 0 24 24" 
                class="nav-arrow"
                :class="{ 'rotated': transactionsExpanded }"
              >
                <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" fill="currentColor"/>
              </svg>
            </button>
            
            <!-- Sub-items -->
            <ul 
              v-if="transactionsExpanded && !layoutStore.isSidebarCollapsed" 
              class="nav-sublist"
              role="menu"
            >
              <li role="none">
                <router-link 
                  to="/transactions" 
                  class="nav-subitem"
                  :class="{ 'active': isActiveRoute('/transactions') }"
                  role="menuitem"
                  :aria-current="isActiveRoute('/transactions') ? 'page' : undefined"
                  @click="handleNavClick"
                >
                  All Transactions
                </router-link>
              </li>
              <li role="none">
                <router-link 
                  to="/customers" 
                  class="nav-subitem"
                  :class="{ 'active': isActiveRoute('/customers') }"
                  role="menuitem"
                  :aria-current="isActiveRoute('/customers') ? 'page' : undefined"
                  @click="handleNavClick"
                >
                  Customers
                </router-link>
              </li>
            </ul>
          </li>
          
          <!-- Analytics -->
          <li role="none">
            <router-link 
              to="/analytics" 
              class="nav-item"
              :class="{ 'active': isActiveRoute('/analytics') }"
              role="menuitem"
              :aria-current="isActiveRoute('/analytics') ? 'page' : undefined"
              @click="handleNavClick"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="currentColor"/>
                </svg>
              </span>
              <span v-if="!layoutStore.isSidebarCollapsed" class="nav-label">Analytics</span>
            </router-link>
          </li>
        </ul>
      </div>
      
      <!-- Divider -->
      <div class="nav-divider"></div>
      
      <!-- Secondary Navigation Group -->
      <div class="nav-group">
        <span 
          v-if="!layoutStore.isSidebarCollapsed" 
          class="nav-group-title"
        >
          Resources
        </span>
        
        <ul class="nav-list" role="menubar">
          <!-- Settings -->
          <li role="none">
            <router-link 
              to="/settings" 
              class="nav-item"
              :class="{ 'active': isActiveRoute('/settings') }"
              role="menuitem"
              :aria-current="isActiveRoute('/settings') ? 'page' : undefined"
              @click="handleNavClick"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" fill="currentColor"/>
                </svg>
              </span>
              <span v-if="!layoutStore.isSidebarCollapsed" class="nav-label">Settings</span>
            </router-link>
          </li>
          
          <!-- Help -->
          <li role="none">
            <router-link 
              to="/help" 
              class="nav-item"
              :class="{ 'active': isActiveRoute('/help') }"
              role="menuitem"
              :aria-current="isActiveRoute('/help') ? 'page' : undefined"
              @click="handleNavClick"
            >
              <span class="nav-icon">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z" fill="currentColor"/>
                </svg>
              </span>
              <span v-if="!layoutStore.isSidebarCollapsed" class="nav-label">Help</span>
            </router-link>
          </li>
        </ul>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useLayoutStore } from '../../stores/layout'

const route = useRoute()
const layoutStore = useLayoutStore()

const transactionsExpanded = ref(true)

const isActiveRoute = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const toggleTransactions = () => {
  transactionsExpanded.value = !transactionsExpanded.value
}

const handleNavClick = () => {
  // Close mobile menu on navigation
  if (window.innerWidth < 768) {
    layoutStore.closeMobileMenu()
  }
}
</script>

<style scoped>
.nav-sidebar {
  grid-area: sidebar;
  width: var(--sidebar-width-expanded);
  height: calc(100vh - var(--header-height));
  position: sticky;
  top: var(--header-height);
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width var(--transition-duration) var(--transition-timing);
  z-index: 50;
}

/* Collapsed State */
.nav-sidebar.collapsed {
  width: var(--sidebar-width-collapsed);
}

/* Toggle Button */
.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 48px;
  border: none;
  background: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.15s;
}

.sidebar-toggle:hover {
  background-color: var(--color-background);
  color: var(--color-primary);
}

.sidebar-toggle:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.toggle-icon {
  width: 24px;
  height: 24px;
  transition: transform var(--transition-duration);
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

/* Navigation Container */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
}

/* Navigation Groups */
.nav-group {
  margin-bottom: 8px;
}

.nav-group-title {
  display: block;
  padding: 8px 16px 8px 12px;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-secondary);
}

/* Navigation List */
.nav-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Navigation Item */
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px;
  border: none;
  background: none;
  border-radius: var(--border-radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}

.nav-item:hover {
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.nav-item:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

/* Active State */
.nav-item.active {
  background-color: var(--color-active-bg);
  color: var(--color-primary);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background-color: var(--color-active-border);
  border-radius: 0 2px 2px 0;
}

/* Navigation Icon */
.nav-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

/* Navigation Label */
.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Navigation Arrow */
.nav-arrow {
  width: 20px;
  height: 20px;
  margin-left: auto;
  transition: transform var(--transition-duration);
}

.nav-arrow.rotated {
  transform: rotate(90deg);
}

/* Sub Navigation */
.nav-item-group-container {
  display: flex;
  flex-direction: column;
}

.nav-sublist {
  list-style: none;
  padding-left: 36px;
  margin-top: 4px;
}

.nav-subitem {
  display: block;
  padding: 8px 12px;
  border-radius: var(--border-radius-sm);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 0.8125rem;
  transition: all 0.15s;
}

.nav-subitem:hover {
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.nav-subitem.active {
  background-color: var(--color-active-bg);
  color: var(--color-primary);
  font-weight: 500;
}

/* Divider */
.nav-divider {
  height: 1px;
  background-color: var(--color-border);
  margin: 8px 16px;
}

/* Collapsed State Adjustments */
.nav-sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px 8px;
}

.nav-sidebar.collapsed .nav-item.active::before {
  left: 0;
  width: 3px;
  height: 20px;
}

/* Mobile Styles */
@media (max-width: 767px) {
  .nav-sidebar {
    position: fixed;
    top: var(--header-height);
    left: 0;
    width: 280px;
    height: calc(100vh - var(--header-height));
    transform: translateX(-100%);
    transition: transform var(--transition-duration) var(--transition-timing);
    z-index: 95;
  }
  
  .nav-sidebar.collapsed {
    width: 280px;
  }
  
  .nav-sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .sidebar-toggle {
    display: none;
  }
}
</style>
