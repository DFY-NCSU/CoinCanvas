<template>
	<el-config-provider :locale="en">
		<router-view />
	</el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus';
import zhCn from 'element-plus/es/locale/lang/zh-cn';
import { useThemeStore } from './store/theme';

const theme = useThemeStore();
theme.initTheme();
</script>
<style>
@import './assets/css/main.css';
</style>
