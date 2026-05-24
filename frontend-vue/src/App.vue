<script setup lang="ts">
import {
  Connection,
  DataAnalysis,
  Expand,
  Files,
  Fold,
  House,
  List,
  Operation,
  Share,
  SetUp,
} from "@element-plus/icons-vue";
import { computed, ref } from "vue";

const sidebarCollapsed = ref(localStorage.getItem("ai-agent-pipeline.sidebar-collapsed") === "true");
const sidebarWidth = computed(() => (sidebarCollapsed.value ? "72px" : "248px"));

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
  localStorage.setItem("ai-agent-pipeline.sidebar-collapsed", String(sidebarCollapsed.value));
}
</script>

<template>
  <el-container class="app-shell">
    <el-aside class="sidebar" :class="{ collapsed: sidebarCollapsed }" :width="sidebarWidth">
      <div class="brand">
        <div class="brand-mark">AI</div>
        <div class="brand-copy">
          <div class="brand-title">Agent Pipeline</div>
          <div class="brand-subtitle">Vue3 Console</div>
        </div>
      </div>

      <el-menu
        router
        class="nav-menu"
        :collapse="sidebarCollapsed"
        :collapse-transition="false"
        :default-active="$route.path"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/runs/new">
          <el-icon><Operation /></el-icon>
          <span>RunConsole</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><List /></el-icon>
          <span>RunHistory</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><Files /></el-icon>
          <span>Reports</span>
        </el-menu-item>
        <el-menu-item index="/models">
          <el-icon><Connection /></el-icon>
          <span>Models</span>
        </el-menu-item>
        <el-menu-item index="/plugins">
          <el-icon><SetUp /></el-icon>
          <span>Plugins</span>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><Share /></el-icon>
          <span>Agents</span>
        </el-menu-item>
        <el-menu-item index="/workflows/templates">
          <el-icon><Operation /></el-icon>
          <span>Workflows</span>
        </el-menu-item>
        <el-menu-item index="/workflows/editor">
          <el-icon><DataAnalysis /></el-icon>
          <span>Workflow Editor</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div class="topbar-left">
          <el-tooltip :content="sidebarCollapsed ? '显示侧边栏' : '隐藏侧边栏'" placement="bottom">
            <el-button
              class="sidebar-toggle"
              :icon="sidebarCollapsed ? Expand : Fold"
              circle
              @click="toggleSidebar"
            />
          </el-tooltip>
          <div>
            <div class="topbar-title">Python Agent Engine Control Plane</div>
            <div class="topbar-subtitle">FastAPI + Vue3 + TypeScript preview</div>
          </div>
        </div>
        <el-tag type="success" effect="plain">
          <el-icon><DataAnalysis /></el-icon>
          v2 Frontend Skeleton
        </el-tag>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
