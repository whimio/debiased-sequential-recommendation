<template>
  <el-card class="batch-card" shadow="hover">
    <h3 class="card-header">批量推荐</h3>
    <el-upload
      class="upload-demo"
      v-model:file-list="fileList"
      :action="null"
      :auto-upload="false"
      :before-upload="beforeUpload"
      accept=".txt"
      drag
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">拖拽 .txt 文件到此处，或点击上传</div>
      <div class="el-upload__tip" slot="tip">每行一个序列，空格或逗号分隔</div>
    </el-upload>

    <div class="controls">
      <el-input-number v-model="topK" :min="1" label="Top K" size="large" />
      <el-button
        :disabled="!fileList.length"
        :loading="loading"
        type="primary"
        @click="submit"
        size="large"
        round
      >
        提交
      </el-button>
    </div>

    <el-table
      v-if="results.length"
      :data="results"
      style="width: 100%; margin-top: 20px"
      stripe
      border
      size="medium"
    >
      <el-table-column prop="line_index" label="行号" width="80" />
      <el-table-column
        prop="recommendations"
        label="推荐结果"
        :formatter="row => row.recommendations.join(', ')"
      />
    </el-table>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const fileList = ref([])
const topK = ref(10)
const results = ref([])
const loading = ref(false)

function beforeUpload(file) {
  return false
}

async function submit() {
  if (!fileList.value.length) {
    return ElMessage.warning('请先选择 .txt 文件')
  }
  loading.value = true
  const form = new FormData()
  form.append('file', fileList.value[0].raw)
  form.append('top_k', topK.value)
  try {
    const res = await axios.post('/api/recommend/', form)
    results.value = res.data.batch_recommendations || []
  } catch (err) {
    console.error(err)
    ElMessage.error('请求失败，请检查网络或后端日志')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.batch-card {
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

.upload-demo {
  margin-bottom: 20px;
  border: 2px dashed #d9d9d9;
  padding: 20px;
  border-radius: 12px;
  background: #fafcff;
}

.controls {
  display: flex;
  gap: 16px;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  flex-wrap: wrap;
}
</style>

