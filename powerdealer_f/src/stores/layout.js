import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLayoutStore = defineStore('layout', () => {
  // Sidebar state
  const isSidebarCollapsed = ref(false)
  const isMobileMenuOpen = ref(false)
  
  // Notification state
  const unreadNotifications = ref(0)
  const notifications = ref([])
  
  // Initialize from localStorage
  const loadFromStorage = () => {
    try {
      const saved = localStorage.getItem('layout_preference')
      if (saved) {
        const prefs = JSON.parse(saved)
        isSidebarCollapsed.value = prefs.sidebarCollapsed ?? false
      }
    } catch (e) {
      console.warn('Failed to load layout preferences:', e)
    }
  }
  
  // Save to localStorage
  const saveToStorage = () => {
    try {
      localStorage.setItem('layout_preference', JSON.stringify({
        sidebarCollapsed: isSidebarCollapsed.value,
        lastUpdated: new Date().toISOString()
      }))
    } catch (e) {
      console.warn('Failed to save layout preferences:', e)
    }
  }
  
  // Toggle sidebar collapsed state
  const toggleSidebar = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
    saveToStorage()
  }
  
  // Set sidebar collapsed state
  const setSidebarCollapsed = (collapsed) => {
    isSidebarCollapsed.value = collapsed
    saveToStorage()
  }
  
  // Toggle mobile menu
  const toggleMobileMenu = () => {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
  }
  
  // Close mobile menu
  const closeMobileMenu = () => {
    isMobileMenuOpen.value = false
  }
  
  // Add a notification
  const addNotification = (notification) => {
    notifications.value.unshift({
      id: Date.now(),
      timestamp: new Date().toISOString(),
      read: false,
      ...notification
    })
    unreadNotifications.value++
  }
  
  // Mark notification as read
  const markAsRead = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification && !notification.read) {
      notification.read = true
      unreadNotifications.value = Math.max(0, unreadNotifications.value - 1)
    }
  }
  
  // Mark all as read
  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
    unreadNotifications.value = 0
  }
  
  // Clear all notifications
  const clearNotifications = () => {
    notifications.value = []
    unreadNotifications.value = 0
  }
  
  // Initialize on store creation
  loadFromStorage()
  
  return {
    // State
    isSidebarCollapsed,
    isMobileMenuOpen,
    unreadNotifications,
    notifications,
    
    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    toggleMobileMenu,
    closeMobileMenu,
    loadFromStorage,
    saveToStorage,
    addNotification,
    markAsRead,
    markAllAsRead,
    clearNotifications
  }
})
