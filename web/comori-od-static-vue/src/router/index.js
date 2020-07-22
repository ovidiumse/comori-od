import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Article from '../views/Article.vue'

Vue.use(VueRouter)

  const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/search/:q',
    name: 'Search',
    component: Search,
  },
  {
    path: '/article/:id',
    name: 'Article',
    component: Article,
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

const scrollableElementId = 'content' // You should change this
const scrollPositions = Object.create(null)

router.beforeEach((to, from, next) => {
  let element = document.getElementById(scrollableElementId)
  if (element !== null) {
    let routeName = from.name + from.params['q'];
    scrollPositions[routeName] = element.scrollTop;
    console.log("Saved scroll position " + element.scrollTop + " for " + routeName);
  }

  next()
})

router.afterEach((to, from) => {
  from;
  let routeName = to.name + to.params['q'];
  let element = document.getElementById(scrollableElementId)
  if (element !== null && routeName in scrollPositions) {
    console.log("Scrolling to position " + scrollPositions[routeName] + " for " + routeName);
    setTimeout(() => element.scrollTop = scrollPositions[routeName], 50)
  }
})

export default router
