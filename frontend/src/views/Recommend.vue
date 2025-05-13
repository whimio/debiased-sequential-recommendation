<template>
  <el-card class="batch-card" shadow="hover">
    <h3 class="card-header">实时推荐</h3>
    <el-form label-position="top" class="recommend-form" @submit.prevent>
      <el-form-item label="推荐序列">
        <el-input
          v-model="sequenceStr"
          placeholder="请输入以逗号分隔的 item ID，例如：1,2,3"
          clearable
          size="large"
        />
      </el-form-item>
      <el-form-item label="Top K">
        <el-input-number v-model="topK" :min="1" :max="100" size="large" />
      </el-form-item>
      <div class="controls">
        <el-button type="primary" size="large" @click="submit" round>提交</el-button>
      </div>
    </el-form>

    <el-table
      v-if="recs.length"
      :data="tableFormatted"
      style="width: 100%; margin-top: 20px"
      stripe
      border
      size="medium"
    >
      <el-table-column type="index" label="序号" width="80" />
      <el-table-column
        prop="recommendations"
        label="推荐结果"
        :formatter="row => row.recommendations"
      />
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const sequenceStr = ref('')
const topK = ref(10)
const recs = ref([])

const tableFormatted = computed(() => {
  return recs.value.map((r, i) => ({ recommendations: r }))
})

async function submit() {
  if (!sequenceStr.value) {
    ElMessage.warning('请输入推荐序列')
    return
  }
  const seq = sequenceStr.value
    .split(/[\s,]+/)
    .map(s => parseInt(s))
    .filter(n => !isNaN(n))
  try {
    const res = await axios.post('/api/recommend/', {
      sequence: seq,
      top_k: topK.value
    })
    recs.value = res.data.recommendations || []
    ElMessage.success('推荐成功')
  } catch (err) {
    console.error(err)
    ElMessage.error('推荐失败')
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

.recommend-form {
  margin-bottom: 24px;
}

.controls {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
