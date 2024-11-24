<template>
	<div class="container">
		<TableCustom :columns="columns" :tableData="tableData" :hasToolbar="false" :hasPagination="false">
			<template #name="{ rows }">
				<el-input v-if="rows.editing" v-model="rows.name"></el-input>
				<span v-else>{{ rows.name }}</span>
			</template>
			<template #password="{ rows }">
				<el-input v-if="rows.editing" v-model="rows.password"></el-input>
				<span v-else>{{ rows.password }}</span>
			</template>
			<template #email="{ rows }">
				<el-input v-if="rows.editing" v-model="rows.email"></el-input>
				<span v-else>{{ rows.email }}</span>
			</template>
			<template #role="{ rows }">
				<el-select v-if="rows.editing" v-model="rows.role">
					<el-option label="Admin" value="Admin"></el-option>
					<el-option label="User" value="Normal User"></el-option>
				</el-select>
				<span v-else>{{ rows.role }}</span>
			</template>
			<template #operator="{ rows, index }">
				<template v-if="!rows.editing">
					<el-button type="primary" size="small" :icon="Edit" @click="handleEdit(rows)">
						Edit
					</el-button>
					<el-button type="danger" size="small" :icon="Delete" @click="">
						Delete
					</el-button>
				</template>
				<template v-else>
					<el-button type="success" size="small" :icon="Select" @click="rows.editing = false">
						Save
					</el-button>
					<el-button type="default" size="small" :icon="CloseBold" @click="handleCancel(rows, index)">
						Cancel
					</el-button>
				</template>
			</template>
		</TableCustom>
	</div>
</template>

<script setup lang="ts" name="table-editor">
import { ref } from 'vue';
import { Delete, Edit, CloseBold, Select } from '@element-plus/icons-vue';
import TableCustom from '@/components/table-custom.vue';
import { fetchUserData } from '@/api/index';

let columns = ref([
	{ type: 'index', label: 'ID', width: 55, align: 'center' },
	{ prop: 'name', label: 'Username' },
	{ prop: 'password', label: 'Password' },
	{ prop: 'email', label: 'Email' },
	{ prop: 'role', label: 'Role' },
	{ prop: 'operator', label: 'Operator', width: 180 },
])
const tableData = ref([]);
const getData = async () => {
	const res = await fetchUserData();
	tableData.value = res.data.list;
};
getData();

const rowData = ref({})

const handleEdit = (row) => {
	rowData.value = { ...row };
	row.editing = true;
};

const handleCancel = (row, index) => {
	row.editing = false;
	tableData.value[index] = { ...rowData.value };
};
</script>

<style scoped></style>
