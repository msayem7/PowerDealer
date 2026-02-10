import { createRouter, createWebHistory } from 'vue-router'
import SignupView from './views/SignupView.vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'

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

// Navigation guard for auth
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/signup') && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
