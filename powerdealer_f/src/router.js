import { createRouter, createWebHistory } from 'vue-router'
import SignupView from './views/SignupView.vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import { useAuthStore } from './stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/signup',
    component: SignupView,
    meta: { title: 'Sign Up' },
  },
  {
    path: '/login',
    component: LoginView,
    meta: { title: 'Login' },
  },
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { title: 'Dashboard', requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Track if session has been restored
let sessionRestored = false

// Navigation guard for auth
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Restore session if not already done and token exists
  if (!sessionRestored && localStorage.getItem('access_token')) {
    sessionRestored = true
    await authStore.restoreSession()
  }
  
  const isAuthenticated = authStore.isAuthenticated
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/signup') && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
