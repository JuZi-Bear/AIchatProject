<script setup lang="ts">
import {
  Connection,
  DataAnalysis,
  Files,
  Folder,
  House,
  List,
  Operation,
  Plus,
  Search,
  SetUp,
  Setting,
  Share,
} from "@element-plus/icons-vue";
import { computed, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();
const sidebarCollapsed = ref(localStorage.getItem("ai-agent-pipeline.sidebar-collapsed") === "true");

const navItems = [
  { path: "/", label: "Dashboard", icon: House },
  { path: "/runs/new", label: "Run", icon: Operation },
  { path: "/workflows/templates", label: "Workflow", icon: Operation },
  { path: "/workflows/editor", label: "Editor", icon: DataAnalysis },
  { path: "/reports", label: "Artifacts", icon: Files },
  { path: "/history", label: "History", icon: List },
  { path: "/models", label: "Models", icon: Connection },
  { path: "/workspace", label: "Workspace", icon: Folder },
  { path: "/plugins", label: "Plugins", icon: SetUp },
  { path: "/agents", label: "Agents", icon: Share },
];

const activeTitle = computed(() => navItems.find((item) => item.path === route.path)?.label || "Workspace");
const isRunWorkbench = computed(() => route.path === "/runs/new");

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem("ai-agent-pipeline.sidebar-collapsed", String(sidebarCollapsed.value));
}

function isActive(path: string) {
  if (path === "/") {
    return route.path === "/";
  }

  return route.path === path || route.path.startsWith(`${path}/`);
}
</script>

<template>
  <section class="codex-app-shell" :class="{ 'is-collapsed': sidebarCollapsed, 'is-workbench-route': isRunWorkbench }">
    <aside v-if="!isRunWorkbench" class="codex-global-sidebar">
      <button class="sidebar-icon-button new-chat-button" type="button" title="新对话" @click="$router.push('/runs/new')">
        <el-icon><Plus /></el-icon>
        <span>新对话</span>
      </button>

      <button class="sidebar-search" type="button" title="搜索">
        <el-icon><Search /></el-icon>
        <span>搜索</span>
        <kbd>Ctrl+G</kbd>
      </button>

      <nav class="codex-nav" aria-label="main navigation">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          class="codex-nav-item"
          :class="{ active: isActive(item.path) }"
          :to="item.path"
          :title="item.label"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-spacer" />

      <button class="sidebar-icon-button settings-button" type="button" title="设置" @click="$router.push('/workspace')">
        <el-icon><Setting /></el-icon>
        <span>设置</span>
      </button>
    </aside>

    <main class="codex-main-shell">
      <header v-if="!isRunWorkbench" class="codex-route-header">
        <button
          class="sidebar-collapse-button"
          type="button"
          :title="sidebarCollapsed ? '显示侧边栏' : '隐藏侧边栏'"
          @click="toggleSidebar"
        >
          <span />
          <span />
          <span />
        </button>
        <div>
          <div class="codex-route-title">{{ activeTitle }}</div>
          <div class="codex-route-subtitle">Run -> Tools -> Artifacts -> Replay</div>
        </div>
        <el-tag class="codex-version-tag" type="success" effect="plain">v2 Codex-style</el-tag>
      </header>

      <section class="codex-route-body">
        <router-view />
      </section>
    </main>
  </section>
</template>
