<template>
    <div>
        <div class="container">
            <TableCustom :columns="columns" :tableData="menuData" row-key="index" :has-pagination="false"
                :viewFunc="handleView" :delFunc="handleDelete" :editFunc="handleEdit">
                <template #toolbarBtn>
                    <el-button type="warning" :icon="CirclePlusFilled" @click="visible = true">New</el-button>
                </template>
                <template #icon="{ rows }">
                    <el-icon>
                        <component :is="rows.icon"></component>
                    </el-icon>
                </template>
            </TableCustom>

        </div>
        <el-dialog :title="isEdit ? 'Edit' : 'Add'" v-model="visible" width="700px" destroy-on-close
            :close-on-click-modal="false" @close="closeDialog">
            <TableEdit :form-data="rowData" :options="options" :edit="isEdit" :update="updateData">
                <template #parent>
                    <el-cascader v-model="rowData.pid" :options="cascaderOptions" :props="{ checkStrictly: true }"
                        clearable />
                </template>
            </TableEdit>
        </el-dialog>
        <el-dialog title="See Details" v-model="visible1" width="700px" destroy-on-close>
            <TableDetail :data="viewData">
                <template #icon="{ rows }">
                    <el-icon>
                        <component :is="rows.icon"></component>
                    </el-icon>
                </template>
            </TableDetail>
        </el-dialog>
    </div>
</template>

<script setup lang="ts" name="system-menu">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { CirclePlusFilled } from '@element-plus/icons-vue';
import { Menus } from '@/types/menu';
import TableCustom from '@/components/table-custom.vue';
import TableDetail from '@/components/table-detail.vue';
import { FormOption } from '@/types/form-option';
import { menuData } from '@/components/menu';

// Forms Related
let columns = ref([
    { prop: 'title', label: 'Title', align: 'left' },
    { prop: 'icon', label: 'Icon' },
    { prop: 'index', label: 'Router Index' },
    { prop: 'permiss', label: 'Permission' },
    { prop: 'operator', label: 'Operator', width: 250 },
])

const getOptions = (data: any) => {
    return data.map(item => {
        const a: any = {
            label: item.title,
            value: item.id,
        }
        if (item.children) {
            a.children = getOptions(item.children)
        }
        return a
    })
}
const cascaderOptions = ref(getOptions(menuData));


// Add/edit popup related
let options = ref<FormOption>({
    labelWidth: '100px',
    span: 12,
    list: [
        { type: 'input', label: 'Title', prop: 'title', required: true },
        { type: 'input', label: 'Router Index', prop: 'index', required: true },
        { type: 'input', label: 'Icon', prop: 'icon' },
        { type: 'input', label: 'Permission', prop: 'permiss' },
        { type: 'parent', label: 'Operator', prop: 'parent' },
    ]
})
const visible = ref(false);
const isEdit = ref(false);
const rowData = ref<any>({});
const handleEdit = (row: Menus) => {
    rowData.value = { ...row };
    isEdit.value = true;
    visible.value = true;
};
const updateData = () => {
    closeDialog();
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
const handleView = (row: Menus) => {
    viewData.value.row = { ...row }
    viewData.value.list = [
        {
            prop: 'id',
            label: 'MenuID',
        },
        {
            prop: 'pid',
            label: 'Parent MenuID',
        },
        {
            prop: 'title',
            label: 'Menu Name',
        },
        {
            prop: 'index',
            label: 'Router Index',
        },
        {
            prop: 'permiss',
            label: 'Permission Label',
        },
        {
            prop: 'icon',
            label: 'Icon',
        },
    ]
    visible1.value = true;
};

// Delete the relevant
const handleDelete = (row: Menus) => {
    ElMessage.success('Delete Successfully');
}
</script>

<style scoped></style>