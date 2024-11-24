<template>
    <div>
        <el-tree
            class="mgb10"
            ref="tree"
            :data="data"
            node-key="id"
            default-expand-all
            show-checkbox
            :default-checked-keys="checkedKeys"
        />
        <el-button type="primary" @click="onSubmit">Save Permission</el-button>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElTree } from 'element-plus';
import { menuData } from '@/components/menu';

const props = defineProps({
    permissOptions: {
        type: Object,
        required: true,
    },
});

const menuObj = ref({});

const getTreeData = (data) => {
    return data.map((item) => {
        const obj: any = {
            id: item.id,
            label: item.title,
        };
        if (item.children) {
            menuObj.value[item.id] = item.children.map((sub) => sub.id);
            obj.children = getTreeData(item.children);
        }
        return obj;
    });
};
const data = getTreeData(menuData);
const checkData = (data: string[]) => {
    return data.filter((item) => {
        return !menuObj.value[item] || data.toString().includes(menuObj.value[item].toString());
    });
};
// Get current privileges
const checkedKeys = ref<string[]>(checkData(props.permissOptions.permiss));

// save authority
const tree = ref<InstanceType<typeof ElTree>>();
const onSubmit = () => {
    // Get selected permissions
    const keys = [...tree.value!.getCheckedKeys(false), ...tree.value!.getHalfCheckedKeys()] as number[];
    console.log(keys);
};
</script>

<style scoped></style>
