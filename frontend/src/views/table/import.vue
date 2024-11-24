<template>
    <div>
        <div class="container">
            <div class="handle-box">
                <el-upload action="#" :limit="1" accept=".xlsx, .xls" :show-file-list="false"
                    :before-upload="beforeUpload" :http-request="handleMany">
                    <el-button class="mr10" type="success">Import</el-button>
                </el-upload>
                <el-link href="/template.xlsx" target="_blank">Download Template</el-link>
            </div>
            <el-table :data="tableData" border class="table" header-cell-class-name="table-header">
                <el-table-column prop="id" label="ID" width="55" align="center"></el-table-column>
                <el-table-column prop="name" label="Username"></el-table-column>
                <el-table-column prop="sno" label="MoneySave"></el-table-column>
                <el-table-column prop="class" label="GoalSetting"></el-table-column>
                <el-table-column prop="age" label="Age"></el-table-column>
            </el-table>
        </div>
    </div>
</template>

<script setup lang="ts" name="import">
import { UploadProps } from 'element-plus';
import { ref, reactive } from 'vue';
import * as XLSX from 'xlsx';

interface TableItem {
    id: number;
    name: string;
    sno: string;
    class: string;
    age: string;
}

const tableData = ref<TableItem[]>([]);
// 获取表格数据
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

const importList = ref<any>([]);
const beforeUpload: UploadProps['beforeUpload'] = async (rawFile) => {
    importList.value = await analysisExcel(rawFile);
    return true;
};
const analysisExcel = (file: any) => {
    return new Promise(function (resolve, reject) {
        const reader = new FileReader();
        reader.onload = function (e: any) {
            const data = e.target.result;
            let datajson = XLSX.read(data, {
                type: 'binary',
            });

            const sheetName = datajson.SheetNames[0];
            const result = XLSX.utils.sheet_to_json(datajson.Sheets[sheetName]);
            resolve(result);
        };
        reader.readAsBinaryString(file);
    });
};

const handleMany = async () => {
    // The data is passed to the server to get the latest list, here is just an example, do not do requests
    const list = importList.value.map((item: any, index: number) => {
        return {
            id: index,
            name: item['Name'],
            sno: item['MoneySave'],
            class: item['GoalSetting'],
            age: item['Age'],
        };
    });
    tableData.value.push(...list);
};
</script>

<style scoped>
.handle-box {
    display: flex;
    margin-bottom: 20px;
}

.table {
    width: 100%;
    font-size: 14px;
}
</style>
