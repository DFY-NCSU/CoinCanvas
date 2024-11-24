<template>
    <div>
        <TableSearch :query="query" :options="searchOpt" :search="handleSearch" />
        <div class="container">
            <TableCustom :columns="columns" :tableData="tableData" :total="page.total" :viewFunc="handleView"
                :delFunc="handleDelete" :page-change="changePage" :editFunc="handleEdit">
                <template #toolbarBtn>
                    <el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">New</el-button>
                </template>
            </TableCustom>

        </div>
        <el-dialog :title="isEdit ? 'Edit' : 'New'" v-model="visible" width="700px" destroy-on-close
            :close-on-click-modal="false" @close="closeDialog">
            <TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData" />
        </el-dialog>
        <el-dialog title="See Details" v-model="visible1" width="700px" destroy-on-close>
            <TableDetail :data="viewData"></TableDetail>
        </el-dialog>
    </div>
</template>

<script setup lang="ts" name="system-user">
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { CirclePlusFilled } from '@element-plus/icons-vue';
import { User } from '@/types/user';
import { fetchUserData } from '@/api';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import TableSearch from '@/components/table-search.vue';
import { FormOption, FormOptionList } from '@/types/form-option';

// Inquiry Related
const query = reactive({
    name: '',
});
const searchOpt = ref<FormOptionList[]>([
    { type: 'input', label: 'username：', prop: 'name' }
])
const handleSearch = () => {
    changePage(1);
};

// Forms Related
let columns = ref([
    { type: 'index', label: 'ID', width: 55, align: 'center' },
    { prop: 'name', label: 'Username', width: 55, align: 'center' },
    { prop: 'phone', label: 'Phone' },
    { prop: 'role', label: 'Role' },
    { prop: 'operator', label: 'Operator', width: 250 },
])
const page = reactive({
    index: 1,
    size: 10,
    total: 0,
})
const tableData = ref<User[]>([]);
const getData = async () => {
    const res = await fetchUserData()
    tableData.value = res.data.list;
    page.total = res.data.pageTotal;
};
getData();

const changePage = (val: number) => {
    page.index = val;
    getData();
};

// Add/edit popup related
let options = ref<FormOption>({
    labelWidth: '100px',
    span: 12,
    list: [
        { type: 'input', label: 'username', prop: 'name', required: true },
        { type: 'input', label: 'Phone', prop: 'phone', required: true },
        { type: 'input', label: 'Password', prop: 'password', required: true },
        { type: 'input', label: 'Mail', prop: 'email', required: true },
        { type: 'input', label: 'Role', prop: 'role', required: true },
    ]
})
const visible = ref(false);
const isEdit = ref(false);
const rowData = ref({});
const handleEdit = (row: User) => {
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
const handleView = (row: User) => {
    viewData.value.row = { ...row }
    viewData.value.list = [
        {
            prop: 'id',
            label: 'UserID',
        },
        {
            prop: 'name',
            label: 'User Name',
        },
        {
            prop: 'password',
            label: 'Password',
        },
        {
            prop: 'email',
            label: 'Mail',
        },
        {
            prop: 'phone',
            label: 'Phone',
        },
        {
            prop: 'role',
            label: 'Role',
        },
        {
            prop: 'date',
            label: 'Date',
        },
    ]
    visible1.value = true;
};

// Delete the relevant
const handleDelete = (row: User) => {
    ElMessage.success('Delete Successfully');
}
</script>

<style scoped></style>