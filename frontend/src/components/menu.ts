import { Menus } from '@/types/menu';

export const menuData: Menus[] = [
    {
        id: '0',
        title: 'System Page',
        index: '/dashboard',
        icon: 'Odometer',
    },
    // {
    //     id: '1',
    //     title: 'System Management',
    //     index: '1',
    //     icon: 'HomeFilled',
    //     children: [
    //         {
    //             id: '11',
    //             pid: '1',
    //             index: '/system-user',
    //             title: 'User Management',
    //         },
    //         {
    //             id: '12',
    //             pid: '1',
    //             index: '/system-role',
    //             title: 'Role Management',
    //         },
    //     ],
    // },
    {
        id: '3',
        title: 'Expenses',
        index: '3',
        icon: 'Calendar',
        children: [
            {
                id: '31',
                pid: '3',
                index: '/table',
                title: 'Base Data',
            },
            {
                id: '32',
                pid: '3',
                index: '/table-editor',
                title: 'Editor Data',
            },
            {
                id: '33',
                pid: '3',
                index: '/import',
                title: 'Import Data',
            },
            {
                id: '34',
                pid: '3',
                index: '/export',
                title: 'Output Data',
            },
        ],
    },
    {
        id: '7',
        icon: 'Brush',
        index: '/theme',
        title: 'Theme',
    },
    {
        id: '6',
        icon: 'DocumentAdd',
        index: '6',
        title: 'Another Page',
        children: [
            {
                id: '61',
                pid: '6',
                index: '/ucenter',
                title: 'Personal Center',
            },
            {
                id: '62',
                pid: '6',
                index: '/login',
                title: 'Login',
            },
            {
                id: '63',
                pid: '6',
                index: '/register',
                title: 'Submit',
            },
            {
                id: '64',
                pid: '6',
                index: '/reset-pwd',
                title: 'Reset Password',
            },
            {
                id: '65',
                pid: '6',
                index: '/403',
                title: '403',
            },
            {
                id: '66',
                pid: '6',
                index: '/404',
                title: '404',
            },
        ],
    },
];
