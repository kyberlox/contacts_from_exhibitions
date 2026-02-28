import axios, {  AxiosError, type AxiosProgressEvent, type AxiosRequestConfig, type AxiosResponse } from 'axios';
import {type  IUsersPassport } from '@/views/contactForm/ContactForm.vue';
import {type IUsersQuestionaire } from '@/views/contactForm/ContactForm.vue';
import { useUserData } from '@/store/userStore';
import { computed } from 'vue';
import { type IPostContacts } from '@/interfaces/IFetchBody';
import { toast } from 'vue3-toastify';

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

interface IBackendError{
    detail:
        {
            type: string,
            loc: string[]
            msg: string,
            input: string,
            ctx: {
                reason: string
            }
        }[]
}


const handleBackendResponse = (data:  AxiosError) => {
    const resp = data.response?.data
    if(resp && (resp as IBackendError).detail?.length && (resp as IBackendError).detail[0].msg){
       return toast((resp as IBackendError).detail[0].msg, { type: 'error', position: 'bottom-right' })
    }
    else if((data as AxiosError).status == 500){
        return toast('Ошибка сервера', { type: 'error', position: 'bottom-right' })
    }
}

export default class Api {
    static async get(url: string, config?: AxiosRequestConfig) {
        return await api.get(url, config)
        .then(resp=>resp.data)
        .catch(e=>{
            handleBackendResponse(e)
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
           .then(resp=>resp.data)
           .catch(e=>{
            handleBackendResponse(e)
        })
}

    static async put(
        url: string,
        data?: IPostContacts
    ) {
        return api.put(url, data)
          .then(resp=>resp.data)
          .catch(e=>{
                handleBackendResponse(e)
        })
    }

    static async delete(url: string) {
        return api.delete(url)
        .then(resp=>resp.data)
        .catch(e=>{
                handleBackendResponse(e)
        })
    }
}