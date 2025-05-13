<template>
  <el-card class="chart-card" shadow="never">
    <div class="chart-header">
      <h4>{{ title }}</h4>
    </div>
    <canvas ref="canvasRef" class="chart-canvas" />
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const props = defineProps({
  title: String
})

const canvasRef = ref(null)

onMounted(() => {
  const ctx = canvasRef.value.getContext('2d')
  ctx.fillStyle = '#f4f4f4'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  ctx.fillStyle = '#666'
  ctx.font = '14px sans-serif'
  ctx.fillText('图表将在此处显示', 20, 40)
})
</script>

<style scoped>
.chart-card {
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  background-color: #fff;
  box-sizing: border-box;
}

.chart-header {
  margin-bottom: 16px;
  text-align: center;
}

.chart-header h4 {
  margin: 0;
  font-size: 18px;
  color: #409eff;
}

.chart-canvas {
  width: 100%;
  height: 300px;
  background-color: #fdfdfd;
  border-radius: 8px;
  border: 1px solid #eee;
}
</style>
