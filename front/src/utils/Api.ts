import axios, {  type AxiosProgressEvent, type AxiosRequestConfig } from 'axios';
import {type  IUsersPassport } from '@/views/contactForm/ContactForm.vue';
import {type IUsersQuestionaire } from '@/views/contactForm/ContactForm.vue';
import { useUserData } from '@/store/userStore';
import { computed } from 'vue';
import { type IPostContacts } from '@/interfaces/IFetchBody';

const VITE_API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
    baseURL: VITE_API_URL,
    withCredentials: true,
})

// добавляю токен
const key = computed(() => useUserData().getKey);
const userId = computed(() => useUserData().getUserId);

api.interceptors.request.use((config) => {
    config.headers['session_id'] = key.value;
    config.headers['user_id'] = userId.value;
    return config
})

export default class Api {
    static async get(url: string, config?: AxiosRequestConfig) {
        return await api.get(url, config)
        .then(resp=>resp.data)
        .catch(e=>{
           console.error(e)
        })
    }


    static async post(
        url: string,
        data?: (IUsersPassport & {questionaire: IUsersQuestionaire}) | IPostContacts | FormData, 
        config?: AxiosRequestConfig & {
            onUploadProgress?: (progressEvent: AxiosProgressEvent) => void
        }
    ) {
      return api.post(url, data, config)
       .then(resp=>config ? resp : resp.data)
        .catch(e=>{
           console.error(e)
    })
}

    static async put(
        url: string,
        data?: IPostContacts
    ) {
        return (await api.put(url, data))
    }

    static async delete(url: string, data?: number[]) {
        return await api.delete(url, { data })
    }
}