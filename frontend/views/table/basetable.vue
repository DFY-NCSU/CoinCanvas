<template>
	<div>
		<TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
		<div class="container">
			<TableCustom :columns="columns" :tableData="tableData" :total="page.total" :viewFunc="handleView"
				:delFunc="handleDelete" :editFunc="handleEdit" :refresh="getData" :currentPage="page.index"
				:changePage="changePage">
				<template #toolbarBtn>
					<el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">New</el-button>
				</template>
				<template #money="{ rows }">
					￥{{ rows.money }}
				</template>
				<template #thumb="{ rows }">
					<el-image class="table-td-thumb" :src="rows.thumb" :z-index="10" :preview-src-list="[rows.thumb]"
						preview-teleported>
					</el-image>
				</template>
				<template #state="{ rows }">
					<el-tag :type="rows.state ? 'success' : 'danger'">
						{{ rows.state ? 'Normalcy' : 'Exceptions' }}
					</el-tag>
				</template>
			</TableCustom>

		</div>
		<el-dialog :title="isEdit ? 'Edited' : 'New'" v-model="visible" width="700px" destroy-on-close
			:close-on-click-modal="false" @close="closeDialog">
			<TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData">
				<template #thumb="{ rows }">
					<img class="table-td-thumb" :src="rows.thumb"></img>
				</template>
			</TableEdit>
		</el-dialog>
		<el-dialog title="Check Details" v-model="visible1" width="700px" destroy-on-close>
			<TableDetail :data="viewData">
				<template #thumb="{ rows }">
					<el-image :src="rows.thumb"></el-image>
				</template>
			</TableDetail>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="basetable">
import { ref, reactive } from 'vue';
import { ElMessage, } from 'element-plus';
import { CirclePlusFilled } from '@element-plus/icons-vue';
import { fetchData } from '@/api/index';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import TableSearch from '@/components/table-search.vue';
import { TableItem } from '@/types/table';
import { FormOption, FormOptionList } from '@/types/form-option';

// Inquiry Related
const query = reactive({
	name: '',
});
const searchOpt = ref<FormOptionList[]>([
	{ type: 'input', label: 'Username：', prop: 'name' }
])
const handleSearch = () => {
	changePage(1);
};

// Forms Related
let columns = ref([
	{ type: 'selection' },
	{ type: 'index', label: 'ID', width: 55, align: 'center' },
	{ prop: 'name', label: 'Username' },
	{ prop: 'money', label: 'Money Save' },
	{ prop: 'thumb', label: 'Avatar' },
	{ prop: 'state', label: 'Status' },
	{ prop: 'operator', label: 'Operator', width: 250 },
])
const page = reactive({
	index: 1,
	size: 10,
	total: 200,
})
const tableData = ref<TableItem[]>([]);
const getData = async () => {
	const res = await fetchData()
	tableData.value = res.data.list;
};
getData();

const changePage = (val: number) => {
	page.index = val;
	getData();
};

// Add/edit popup related
let options = ref<FormOption>({
	labelWidth: '100px',
	span: 24,
	list: [
		{ type: 'input', label: 'Account Name', prop: 'name', required: true },
		{ type: 'number', label: 'Money Save', prop: 'money', required: true },
		{ type: 'switch', activeText: 'Normal', inactiveText: 'Exceptions', label: 'Account Status', prop: 'state', required: true },
		{ type: 'upload', label: 'Avatar', prop: 'thumb', required: true },
	]
})
const visible = ref(false);
const isEdit = ref(false);
const rowData = ref({});
const handleEdit = (row: TableItem) => {
	rowData.value = { ...row };
	isEdit.value = true;
	visible.value = true;
};
const updateData = () => {
	closeDialog();
	getData();
};

const closeDialog = () => {
	visible.value = false;
	isEdit.value = false;
};

// View details pop-up related
const visible1 = ref(false);
const viewData = ref({
	row: {},
	list: []
});
const handleView = (row: TableItem) => {
	viewData.value.row = { ...row }
	viewData.value.list = [
		{
			prop: 'id',
			label: 'User ID',
		},
		{
			prop: 'name',
			label: 'User Name',
		},
		{
			prop: 'money',
			label: 'Money Save',
		},
		{
			prop: 'state',
			label: 'Account Status',
		},
		{
			prop: 'thumb',
			label: 'Avatar',
		},
	]
	visible1.value = true;
};

// Delete the relevant
const handleDelete = (row: TableItem) => {
	ElMessage.success('Delete Successfully!');
}
</script>

<style scoped>
.table-td-thumb {
	display: block;
	margin: auto;
	width: 40px;
	height: 40px;
}
</style>
