<template>
  <div class="notification-panel" role="dialog" aria-label="Notifications">
    <div class="panel-header">
      <h3>Notifications</h3>
      <button 
        v-if="layoutStore.unreadNotifications > 0"
        class="mark-all-read"
        @click="$emit('markAllRead')"
      >
        Mark all read
      </button>
    </div>
    
    <div class="panel-content">
      <div v-if="layoutStore.notifications.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" fill="currentColor"/>
        </svg>
        <p>No notifications yet</p>
      </div>
      
      <ul v-else class="notification-list">
        <li 
          v-for="notification in layoutStore.notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-icon" :class="notification.type || 'info'">
            <svg v-if="notification.type === 'success'" viewBox="0 0 24 24" fill="none">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
            </svg>
            <svg v-else-if="notification.type === 'warning'" viewBox="0 0 24 24" fill="none">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" fill="currentColor"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="currentColor"/>
            </svg>
          </div>
          <div class="notification-content">
            <p class="notification-title">{{ notification.title }}</p>
            <p v-if="notification.message" class="notification-message">{{ notification.message }}</p>
            <span class="notification-time">{{ formatTime(notification.timestamp) }}</span>
          </div>
          <span v-if="!notification.read" class="unread-dot" aria-label="Unread"></span>
        </li>
      </ul>
    </div>
    
    <div v-if="layoutStore.notifications.length > 0" class="panel-footer">
      <button class="clear-all" @click="handleClearAll">
        Clear all notifications
      </button>
    </div>
  </div>
</template>

<script setup>
import { useLayoutStore } from '../../stores/layout'

const emit = defineEmits(['close', 'markAllRead'])

const layoutStore = useLayoutStore()

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

const handleNotificationClick = (notification) => {
  layoutStore.markAsRead(notification.id)
  if (notification.action?.path) {
    emit('close')
  }
}

const handleClearAll = () => {
  layoutStore.clearNotifications()
}
</script>

<style scoped>
.notification-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  max-height: 480px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 200;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
}

.panel-header h3 {
  font-size: 1rem;
  font-weight: 600;
}

.mark-all-read {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: 0.8125rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
}

.mark-all-read:hover {
  background-color: var(--color-primary-light);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: var(--color-text-secondary);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.notification-list {
  list-style: none;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.15s;
  position: relative;
}

.notification-item:hover {
  background-color: var(--color-background);
}

.notification-item.unread {
  background-color: var(--color-primary-light);
}

.notification-item.unread:hover {
  background-color: #d1e9fc;
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.info {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.notification-icon.success {
  background-color: #e8f5e9;
  color: #4caf50;
}

.notification-icon.warning {
  background-color: #fff3e0;
  color: #ff9800;
}

.notification-icon svg {
  width: 18px;
  height: 18px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.notification-message {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  flex-shrink: 0;
  margin-top: 6px;
}

.panel-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
}

.clear-all {
  width: 100%;
  padding: 8px;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-sm);
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.clear-all:hover {
  background-color: var(--color-background);
  border-color: var(--color-text-secondary);
}

@media (max-width: 767px) {
  .notification-panel {
    width: calc(100vw - 32px);
    right: -80px;
  }
}
</style>
