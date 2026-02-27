import { defineStore } from "pinia";

export const useUserData = defineStore('userData', {
    state: () => ({
        userId: '2366',
        key: 'session_token_123'
    }),

    actions: {
        setAdmin(id: string, key: string){
            this.userId = id;
            this.key = key;
        }
    },

    getters: {
        getUserId: (state)=> state.userId,
        getKey: (state)=> state.key
    }
});