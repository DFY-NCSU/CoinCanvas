<template>
    <div>
        <div class="container">
            <div class="handle-box">
                <el-button type="primary" @click="exportXlsx">Export Excel</el-button>
            </div>
            <el-table :data="tableData" border class="table" header-cell-class-name="table-header">
                <el-table-column prop="id" label="ID" width="55" align="center"></el-table-column>
                <el-table-column prop="name" label="Username"></el-table-column>
                <el-table-column prop="sno" label="Money Save"></el-table-column>
                <el-table-column prop="class" label="Goal Setting"></el-table-column>
                <el-table-column prop="age" label="Age"></el-table-column>
            </el-table>
        </div>
    </div>
</template>

<script setup lang="ts" name="export">
import { ref } from 'vue';
import * as XLSX from 'xlsx';

interface TableItem {
    id: number;
    name: string;
    sno: string;
    class: string;
    age: string;
}

const tableData = ref<TableItem[]>([]);
// Get Data from database(you need to add connection here
const getData = () => {
    tableData.value = [
        {
            id: 1,
            name: '1',
            sno: '1',
            class: '1',
            age: '1',
        },
        {
            id: 2,
            name: '2',
            sno: '2',
            class: '2',
            age: '9',
        },
    ];
};
getData();

const list = [['ID', 'Name', 'Money Save', 'Goal Setting', 'Age']];
const exportXlsx = () => {
    tableData.value.map((item: any, i: number) => {
        const arr: any[] = [i + 1];
        arr.push(...[item.name, item.sno, item.class, item.age, item.sex]);
        list.push(arr);
    });
    let WorkSheet = XLSX.utils.aoa_to_sheet(list);
    let new_workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(new_workbook, WorkSheet, 'First Page');
    XLSX.writeFile(new_workbook, `Excel.xlsx`);
};
</script>

<style scoped>
.handle-box {
    margin-bottom: 20px;
}

.handle-select {
    width: 120px;
}

.handle-input {
    width: 300px;
}

.table {
    width: 100%;
    font-size: 14px;
}

.red {
    color: #f56c6c;
}

.table-td-thumb {
    display: block;
    margin: auto;
    width: 40px;
    height: 40px;
}
</style>
