import { defineStore } from "pinia";

export const useUserData = defineStore('userData', {
    state: () => ({
        userId: '23663',
        key: 'session_token_1233',
        // userId: '2366',
        // key: 'session_token_123',
        isAdmin: false
    }),

    actions: {
        setUserData(id: string, key: string){
            this.userId = id;
            this.key = key;
        },
        setAdmin(status: boolean){
            this.isAdmin = status
        }
    },

    getters: {
        getUserId: (state)=> state.userId,
        getKey: (state)=> state.key,
        getAdmin: (state) => state.isAdmin
    }
});