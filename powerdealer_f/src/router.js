import { createRouter, createWebHistory } from 'vue-router'
import SignupView from './views/SignupView.vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import CustomersView from './views/CustomersView.vue'
import CustomerCreateView from './views/CustomerCreateView.vue'
import CustomerEditView from './views/CustomerEditView.vue'
import TradingView from './views/TradingView.vue'
import ProjectionView from './views/ProjectionView.vue'
import CustomerDashboardView from './views/CustomerDashboardView.vue'
import AppLayout from './components/layout/AppLayout.vue'
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
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        component: DashboardView,
        meta: { title: 'Dashboard' },
      },
      {
        path: 'customers',
        component: CustomersView,
        meta: { title: 'Customers' },
      },
      {
        path: 'customers/create',
        component: CustomerCreateView,
        meta: { title: 'Add Customer' },
      },
      {
        path: 'customers/:mprn/edit',
        component: CustomerEditView,
        meta: { title: 'Edit Customer' },
      },
      {
        path: 'transactions',
        component: CustomersView,
        meta: { title: 'Transactions' },
      },
      {
        path: 'transactions/trading',
        component: TradingView,
        meta: { title: 'Trading', requiresAuth: true },
      },
      {
        path: 'transactions/projection',
        component: ProjectionView,
        meta: { title: 'Cost Projection', requiresAuth: true },
      },
      {
        path: 'customer-dashboard',
        component: CustomerDashboardView,
        meta: { title: 'My Dashboard', requiresAuth: true },
      },
      {
        path: 'analytics',
        component: DashboardView,
        meta: { title: 'Analytics' },
      },
      {
        path: 'settings',
        component: DashboardView,
        meta: { title: 'Settings' },
      },
      {
        path: 'help',
        component: DashboardView,
        meta: { title: 'Help' },
      },
    ],
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
    // Redirect to appropriate dashboard based on user role
    if (authStore.isCustomer) {
      next('/customer-dashboard')
    } else {
      next('/dashboard')
    }
  } else {
    next()
  }
})

export default router
