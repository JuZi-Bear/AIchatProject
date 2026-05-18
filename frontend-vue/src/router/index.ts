import { createRouter, createWebHistory } from "vue-router";

import Agents from "@/views/Agents.vue";
import Dashboard from "@/views/Dashboard.vue";
import Models from "@/views/Models.vue";
import Plugins from "@/views/Plugins.vue";
import Reports from "@/views/Reports.vue";
import RunConsole from "@/views/RunConsole.vue";
import RunHistory from "@/views/RunHistory.vue";
import WorkflowEditor from "@/views/WorkflowEditor.vue";
import WorkflowTemplates from "@/views/WorkflowTemplates.vue";
import WorkflowReplay from "@/views/WorkflowReplay.vue";

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
      path: "/replay/:platformRunId",
      name: "workflow-replay",
      component: WorkflowReplay,
    },
    {
      path: "/workflows/templates",
      name: "workflow-templates",
      component: WorkflowTemplates,
    },
    {
      path: "/workflows/editor",
      name: "workflow-editor",
      component: WorkflowEditor,
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
    {
      path: "/agents",
      name: "agents",
      component: Agents,
    },
  ],
});

export default router;
