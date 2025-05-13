<template>
  <el-card class="eval-card" shadow="hover">
    <h3 class="card-header">{{ metrics ? '当前去偏模型指标' : '上传测试文件' }}</h3>

    <el-table
      v-if="metrics"
      :data="recallNdgcTable"
      style="width: 100%; margin-top: 20px"
      border
      stripe
      size="medium"
    >
      <el-table-column prop="k" label="K 值" width="80" />
      <el-table-column prop="recall" label="Recall" />
      <el-table-column prop="ndcg" label="NDCG" />
    </el-table>

    <el-upload
      class="upload-area"
      v-model:file-list="fileList"
      :action="null"
      :auto-upload="false"
      :before-upload="onBeforeUpload"
      accept=".txt"
      drag
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">拖拽 .txt 文件到此处，或点击上传</div>
      <div class="el-upload__tip">每行一个序列，空格或逗号分隔</div>
    </el-upload>

    <div class="controls">
      <el-button
        type="primary"
        size="large"
        :disabled="!fileList.length || loading"
        :loading="loading"
        @click="onEvaluate"
        round
      >
        开始评估
      </el-button>
    </div>

    <el-alert
      v-if="error"
      class="error-alert"
      :title="error"
      type="error"
      show-icon
      center
    />



    <!-- 图表区 -->
    <el-row v-if="metrics" :gutter="20" class="charts-row">
      <el-col
        v-for="(refEl, idx) in chartRefs"
        :key="idx"
        :xs="24"
        :sm="24"
        :md="24"
        :lg="24"
      >
        <el-card shadow="always" class="chart-card">
          <h3 class="chart-title">{{ chartTitles[idx] }}</h3>
          <canvas :ref="refEl"></canvas>
        </el-card>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'
import { useUserStore } from '@/stores/user.js'

const fileList = ref([])
const loading  = ref(false)
const error    = ref('')
const metrics  = ref(null)

const recallChart   = ref(null)
const ndcgChart     = ref(null)
const coverageChart = ref(null)
const chartRefs     = [recallChart, ndcgChart, coverageChart]
const chartTitles   = ['Recall 对比', 'NDCG 对比', 'Coverage 对比']

const recallNdgcTable = computed(() => {
  if (!metrics.value) return []
  const deb = metrics.value.debiased
  return [5, 10, 20].map(k => ({
    k,
    recall: deb[k]?.recall?.toFixed(4) ?? '-',
    ndcg: deb[k]?.ndcg?.toFixed(4) ?? '-'
  }))
})

function onBeforeUpload(file) {
  fileList.value = [file]
  error.value = ''
  return false
}

async function onEvaluate() {
  if (!fileList.value.length) return
  loading.value = true
  error.value   = ''

  const entry  = fileList.value[0]
  const rawFile = entry.raw instanceof File ? entry.raw : entry

  const form = new FormData()
  form.append('file', rawFile)

  const token = useUserStore().token
  try {
    const resp = await axios.post('/api/evaluate/', form, {
      headers: { Authorization: `Bearer ${token}` }
    })
    metrics.value = resp.data
    await nextTick()
    renderAllCharts()
  } catch (err) {
    console.error(err)
    error.value = '评估失败，请检查文件格式或登录状态'
  } finally {
    loading.value = false
  }
}

function renderAllCharts() {
  const ks  = Object.keys(metrics.value.debiased).map(k => Number(k))
  const deb = metrics.value.debiased
  const bi  = metrics.value.biased

  function drawChart(refEl, key) {
    const dataDeb = ks.map(k => deb[k][key])
    const dataBi  = ks.map(k => bi[k][key])
    return new Chart(refEl, {
      type: 'line',
      data: {
        labels: ks,
        datasets: [
          { label: '去偏',   data: dataDeb, tension: 0.3 },
          { label: '不去偏', data: dataBi,  tension: 0.3 }
        ]
      },
      options: {
        responsive: true,
        scales: {
          x: { title: { display: true, text: 'K 值' } },
          y: { title: { display: true, text: key.toUpperCase() } }
        },
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        }
      }
    })
  }

  chartRefs.forEach(r => {
    if (r.value && r.value._chart) {
      r.value._chart.destroy()
    }
  })

  recallChart.value._chart   = drawChart(recallChart.value,   'recall')
  ndcgChart.value._chart     = drawChart(ndcgChart.value,     'ndcg')
  coverageChart.value._chart = drawChart(coverageChart.value, 'coverage')
}
</script>

<style scoped>
.eval-card {
  max-width: 960px;
  margin: 40px auto;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background-color: #fff;
  box-sizing: border-box;
}

.card-header {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #409eff;
  text-align: center;
}

/* 上传区域统一风格 */
.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  background: #fafcff;
  text-align: center;
  padding: 40px 0;
  margin-bottom: 20px;
}

/* 去除 el-upload 默认边框 */
:deep(.el-upload) {
  border: none !important;
  background-color: transparent !important;
  padding: 0 !important;
}

:deep(.el-upload-dragger) {
  border: none !important;
  background-color: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}

:deep(.el-upload-dragger > div) {
  padding: 0 !important;
  margin: 0 !important;
}

:deep(.el-upload-dragger i) {
  font-size: 32px;
  color: #409eff;
  display: block;
  margin-bottom: 12px;
}

:deep(.el-upload__text),
:deep(.el-upload__tip) {
  font-size: 14px;
  color: #666;
  margin: 0;
  padding: 0;
}

.controls {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.error-alert {
  margin-top: 16px;
}

.charts-row {
  margin-top: 20px;
  flex-direction: column;
}

.chart-card {
  padding: 1rem;
  border-radius: 8px;
  height: 100%;
  margin-bottom: 1rem;
}

.chart-title {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  color: #303133;
  text-align: center;
}
</style>
