<script setup lang="ts">
import {
  Connection,
  DataAnalysis,
  Files,
  House,
  List,
  Operation,
  SetUp,
} from "@element-plus/icons-vue";
</script>

<template>
  <el-container class="app-shell">
    <el-aside class="sidebar" width="248px">
      <div class="brand">
        <div class="brand-mark">AI</div>
        <div>
          <div class="brand-title">Agent Pipeline</div>
          <div class="brand-subtitle">Vue3 Console</div>
        </div>
      </div>

      <el-menu router class="nav-menu" :default-active="$route.path">
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
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <div class="topbar-title">Python Agent Engine Control Plane</div>
          <div class="topbar-subtitle">FastAPI + Vue3 + TypeScript preview</div>
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
