<template>
  <div class="layout-container">
    <!-- 左侧菜单栏 -->
    <div class="sidebar">
      <el-menu
        :default-active="activeMenu"
        @select="onSelect"
        router
        class="el-menu-vertical-demo"
      >
        <el-menu-item index="home">首页</el-menu-item>
        <el-menu-item index="recommend">实时推荐</el-menu-item>
        <el-menu-item index="batch">批量推荐</el-menu-item>
        <el-menu-item index="eval">模型评估</el-menu-item>
        <el-menu-item index="logout">登出</el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧主区域 -->
    <div class="main-content">
      <div class="header">
        欢迎, {{ userStore.username || '用户' }}
      </div>
      <div class="main-body">
<div class="content-wrapper">
  <!-- 仅在 /home 显示项目介绍卡片 -->
  <el-card v-if="route.name === 'home'" class="intro-card" shadow="hover">
    <template #header>
      <div class="card-header">
         项目介绍：去偏推荐系统
      </div>
    </template>
    <div class="intro-content">
  <p>
    本项目旨在构建一个<strong>去偏的序列推荐系统</strong>，解决推荐系统中由于历史点击行为存在曝光偏差（Exposure Bias）而导致的效果失真问题。
  </p>
  <p>
    我们使用了 <strong>Tenrec 数据集中的 QB-video 子集</strong>，构建用户-商品的点击序列，并采用 <strong>分布式鲁棒优化（DRO, Distributionally Robust Optimization）</strong> 策略进行去偏建模，提升模型对真实用户偏好的捕捉能力。
  </p>
  <p>
    推荐系统的效果评估主要通过以下两个指标：
    <ul style="margin-left: 1em;">
      <li><strong>Recall@K</strong>：衡量推荐列表中被用户实际点击的项目比例，代表<strong>推荐命中率</strong>。</li>
      <li><strong>NDCG@K</strong>（归一化折损累计增益）：综合考虑推荐顺序和点击行为，衡量<strong>排序质量</strong>。</li>
    </ul>
  </p>
  <p>
    本系统使用 <strong>Django + Vue 3</strong> 实现，前后端分离，支持上传用户行为进行个性化推荐、模型评估和可视化展示。
  </p>
  <p>
    所有代码、模型与说明文档均已开源，托管于 GitHub：
    <a href="https://github.com/whimio/debiased-sequential-recommendation" target="_blank">
      github.com/whimio/debiased-sequential-recommendation
    </a>
  </p>
</div>
  </el-card>

  <!-- 始终显示路由页面 -->
  <router-view />
</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.js'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => {
  if (route.name === 'home') return 'home'
  if (route.name === 'recommend') return 'recommend'
  if (route.name === 'batch') return 'batch'
  if (route.name === 'eval') return 'eval'
  return ''
})

function onSelect(key) {
  if (key === 'logout') {
    userStore.logout()
    router.push({ name: 'login' })
  } else {
    router.push({ name: key })
  }
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden; /* 防止横向滚动 */
}

.sidebar {
  width: 20%;
  min-width: 200px;
  background-color: #ffffff;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.05);
  padding: 20px 0;
}

.main-content {
  width: 80%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom right, #e6f3ff, #f8fbff);
}

.header {
  height: 64px;
  line-height: 64px;
  padding: 0 30px;
  font-size: 18px;
  color: #333;
  background-color: #ffffff;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.04);
}

.main-body {
  flex: 1;
  overflow-y: auto;
  padding: 40px 24px;
  box-sizing: border-box;
}

.content-wrapper {
  max-width: 960px;
  margin: 0 auto;
  min-height: 60vh;
  width: 100%;
  box-sizing: border-box;
}
.intro-card {
  margin-bottom: 30px;
  background-color: #fafdff;
  border: 1px solid #d0e6f8;
  border-radius: 12px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.intro-content p {
  font-size: 15px;
  line-height: 1.8;
  color: #444;
  margin: 8px 0;
}
</style>
