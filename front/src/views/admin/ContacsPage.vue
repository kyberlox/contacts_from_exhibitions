<template>
<div class="max-w-[1200px] m-auto mt-6"
     v-if="!isLoading">
    <h1 class="text-2xl font-semibold mb-6">Контакты</h1>
    <!-- Фильтр -->
    <div class="w-full flex justify-start">
        <select @change="handleFilterChange"
                class="w-fit border-amber-600 border-1 p-1 mb-1 rounded-md outline-none">
            <option value="">Все</option>
            <option v-for="(value, index) in allAuthors"
                    :key="'author' + index">
                {{ value }}
            </option>
        </select>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <RouterLink :to="{ name: 'contactEdit', params: { id: contact.id } }"
                    v-for="contact in contacts.filter(e => filterAuthor ? e.author_id == filterAuthor : true)"
                    :key="contact.id"
                    :class="['relative block transition-all duration-300 ease-in-out', 'opacity-100 scale-100']">
            <CloseIcon class="w-7 h-7 absolute -top-2 -right-2 rounded-full p-1 shadow-md cursor-pointer hover:scale-110 z-10 hover:bg-red-100 transition-all"
                       @click.stop.capture.prevent="removeContact(contact.id)" />
            <div
                 class="border border-gray-200 rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition-all duration-200 h-full">
                <div class="text-right text-sm w-full">{{ contact.id }}</div>
                <h2 class="text-lg font-medium mb-2">{{ `ФИО: ` + (contact.full_name || 'не заполнено') }}</h2>
                <h3 class="text-gray-600 mb-1">{{ `Название компании: ` + (contact.title || 'не заполнено') }}</h3>
                <div class="text-gray-600 mb-1">{{ `Должность: ` + (contact.position || 'не заполнено') }}</div>
                <div class="text-gray-600 mb-1">{{ `Выставка: ` + (contact.exhibition_title || 'не заполнено') }}</div>
                <div class="text-black">{{ `Автор: ` + contact.author_id }}</div>
            </div>
        </RouterLink>
    </div>
</div>
<div class="flex max-w-full h-full max-h-[250px] relative items-center justify-center"
     v-else>
    <Loader />
</div>
</template>
<script lang='ts'>
import Api from '@/utils/Api';
import { defineComponent, onMounted, ref } from 'vue';
import CloseIcon from '@/assets/icons/CloseIcon.svg?component';
import DateUtil from '@/utils/DateUtil';
import Loader from '@/components/Loader.vue';

interface IContact {
    "id": number,
    "title": string,
    "full_name": string,
    "position": string,
    "email": string,
    "phone_number": string,
    "city": string,
    "exhibition_title": null | string,
    "created_at": string,
    "author_id": string
}

export default defineComponent({
    components: {
        CloseIcon,
        Loader
    },
    props: {
        id: {
            type: Number,
        }
    },
    setup(props) {
        const contacts = ref<IContact[]>([]);
        const allAuthors = ref<string[]>([]);
        const isLoading = ref(true);
        const filterAuthor = ref<string>('');

        const handleFilterChange = (e: Event) => {
            filterAuthor.value = ((e.target as HTMLInputElement)?.value)
        }

        const contactInit = () => {
            isLoading.value = true;
            Api.get(`contacts/?exhibition_id=${props.id}`)
                .then((data) => {
                    contacts.value = data.items;
                    getAllAuthors(data.items);
                })
                .finally(() => isLoading.value = false)
        }

        const getAllAuthors = (contacts: IContact[]) => {
            contacts.forEach((contact) => {
                if (contact.author_id && !allAuthors.value.includes(contact.author_id)) {
                    allAuthors.value.push(contact.author_id)
                }
            })
        }

        onMounted(() => {
            contactInit()
        })

        const removeContact = (id: number) => {
            Api.delete(`contacts/${id}`)
                .then(() => {
                    contactInit();
                })
        }

        return {
            contacts,
            isLoading,
            allAuthors,
            filterAuthor,
            handleFilterChange,
            removeContact,
            DateUtil
        }
    }
});
</script>