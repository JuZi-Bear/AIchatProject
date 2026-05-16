import { createRouter, createWebHistory } from "vue-router";

import Dashboard from "@/views/Dashboard.vue";
import Models from "@/views/Models.vue";
import Plugins from "@/views/Plugins.vue";
import Reports from "@/views/Reports.vue";
import RunConsole from "@/views/RunConsole.vue";
import RunHistory from "@/views/RunHistory.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: Dashboard,
    },
    {
      path: "/runs/new",
      name: "run-console",
      component: RunConsole,
    },
    {
      path: "/runs",
      redirect: "/history",
    },
    {
      path: "/history",
      name: "run-history",
      component: RunHistory,
    },
    {
      path: "/reports",
      name: "reports",
      component: Reports,
    },
    {
      path: "/models",
      name: "models",
      component: Models,
    },
    {
      path: "/plugins",
      name: "plugins",
      component: Plugins,
    },
  ],
});

export default router;
