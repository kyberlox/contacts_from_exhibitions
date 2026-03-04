import { defineStore } from "pinia";

interface IData{
            isAdmin: boolean,
            created_at: string,
            department: string,
            full_name: string,
            id: number,
            is_admin: boolean,
            position: string,
            updated_at: string
}

export const useUserData = defineStore('userData', {
    state: () => ({
        userId: '',
        key: '',
        // userId: '',
        // key: '',
        data: {
            created_at: '',
            department: '',
            full_name: '',
            id: 0,
            is_admin: false,
            position: '',
            updated_at: ''
        },
    }),

    actions: {
        setUserData(data: IData) {
            this.data = data
        },
    },

    getters: {
        getUserId: (state) => state.userId,
        getKey: (state) => state.key,
        getAdmin: (state) => state.data.is_admin,
        getNeedCatalogRedirect: (state)=> !state.data.id || state.data.id == 0 
    }
});