<template>
    <div>
        <TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
        <div class="container">

            <TableCustom :columns="columns" :tableData="tableData" :total="page.total" :viewFunc="handleView"
                :delFunc="handleDelete" :page-change="changePage" :editFunc="handleEdit">
                <template #toolbarBtn>
                    <el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">New</el-button>
                </template>
                <template #status="{ rows }">
                    <el-tag type="success" v-if="rows.status">Use</el-tag>
                    <el-tag type="danger" v-else>Forbidden</el-tag>
                </template>
                <template #permissions="{ rows }">
                    <el-button type="primary" size="small" plain @click="handlePermission(rows)">Managerial</el-button>
                </template>
            </TableCustom>
        </div>
        <el-dialog :title="isEdit ? '编辑' : '新增'" v-model="visible" width="700px" destroy-on-close
            :close-on-click-modal="false" @close="closeDialog">
            <TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData" />
        </el-dialog>
        <el-dialog title="查看详情" v-model="visible1" width="700px" destroy-on-close>
            <TableDetail :data="viewData">
                <template #status="{ rows }">
                    <el-tag type="success" v-if="rows.status">Use</el-tag>
                    <el-tag type="danger" v-else>Forbidden</el-tag>
                </template>
            </TableDetail>
        </el-dialog>
        <el-dialog title="Rights Management" v-model="visible2" width="500px" destroy-on-close>
            <RolePermission :permiss-options="permissOptions" />
        </el-dialog>
    </div>
</template>

<script setup lang="ts" name="system-role">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Role } from '@/types/role';
import { fetchRoleData } from '@/api';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import RolePermission from './role-permission.vue'
import { CirclePlusFilled } from '@element-plus/icons-vue';
import { FormOption, FormOptionList } from '@/types/form-option';

// Inquiry Related
const query = reactive({
    name: '',
});
const searchOpt = ref<FormOptionList[]>([
    { type: 'input', label: 'Role Name：', prop: 'name' }
])
const handleSearch = () => {
    changePage(1);
};

// Forms Related
let columns = ref([
    { type: 'index', label: 'Number', width: 55, align: 'center' },
    { prop: 'name', label: 'Role Name' },
    { prop: 'key', label: 'Role Key' },
    { prop: 'status', label: 'Status' },
    { prop: 'permissions', label: 'Permissions' },
    { prop: 'operator', label: 'Operator', width: 250 },
])
const page = reactive({
    index: 1,
    size: 10,
    total: 0,
})
const tableData = ref<Role[]>([]);
const getData = async () => {
    const res = await fetchRoleData()
    tableData.value = res.data.list;
    page.total = res.data.pageTotal;
};
getData();
const changePage = (val: number) => {
    page.index = val;
    getData();
};

// Add/edit popup related
const options = ref<FormOption>({
    labelWidth: '100px',
    span: 24,
    list: [
        { type: 'input', label: 'Role Name', prop: 'name', required: true },
        { type: 'input', label: 'Role Key', prop: 'key', required: true },
        { type: 'switch', label: 'Status', prop: 'status', required: false, activeText: '启用', inactiveText: '禁用' },
    ]
})
const visible = ref(false);
const isEdit = ref(false);
const rowData = ref({});
const handleEdit = (row: Role) => {
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
    rowData.value = {};
};

// View details pop-up related
const visible1 = ref(false);
const viewData = ref({
    row: {},
    list: [],
    column: 1
});
const handleView = (row: Role) => {
    viewData.value.row = { ...row }
    viewData.value.list = [
        {
            prop: 'id',
            label: 'RoleID',
        },
        {
            prop: 'name',
            label: 'Role Name',
        },
        {
            prop: 'key',
            label: 'Role Key',
        },
        {
            prop: 'status',
            label: 'Role Status',
        },
    ]
    visible1.value = true;
};

// Delete the relevant
const handleDelete = (row: Role) => {
    ElMessage.success('Delete Successfully');
}


// Permission management pop-up related
const visible2 = ref(false);
const permissOptions = ref({})
const handlePermission = (row: Role) => {
    visible2.value = true;
    permissOptions.value = {
        id: row.id,
        permiss: row.permiss
    };
}
</script>

<style scoped></style>