<template>
<div class="max-w-[1200px] m-auto mt-6">
    <h1 class="text-2xl font-semibold mb-6">Контакты</h1>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <RouterLink :to="{ name: 'contactEdit', params: { id: contact.id } }"
                    v-for="contact in contacts"
                    :key="contact.id"
                    class="relative block ">
            <CloseIcon class="w-7 h-7 absolute -top-2 -right-2 rounded-full p-1 shadow-md   cursor-pointer hover:scale-110 z-10"
                       @click.stop.capture.prevent="removeContact(contact.id)" />
            <div
                 class="border border-gray-200 rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition-shadow duration-200">
                <h2 class="text-lg font-medium  mb-2">{{ `ФИО: ` + contact.full_name }}</h2>
                <h3 class="text-gray-600 mb-1">{{ `Название компании: ` + contact.title }}</h3>
                <div class="text-gray-600 mb-1">{{ `Должность: ` + contact.position }}</div>
                <div class="text-gray-600">{{ `Выставка: ` + contact.exhibition_title }}</div>
            </div>
        </RouterLink>
    </div>
</div>
</template>
<script lang='ts'>
import Api from '@/utils/Api';
import { defineComponent, onMounted, ref } from 'vue';
import CloseIcon from '@/assets/icons/CloseIcon.svg?component';
import DateUtil from '@/utils/DateUtil';

export default defineComponent({
    components: {
        CloseIcon
    },
    props: {
        id: {
            type: Number,
        }
    },
    setup(props) {
        const contacts = ref<{
            "id": number,
            "title": string,
            "full_name": string,
            "position": string,
            "email": string,
            "phone_number": string,
            "city": string,
            "exhibition_title": null | string,
            "created_at": string
        }[]>([]);

        const contactInit = () => {
            Api.get(`contacts/?exhibition_id=${props.id}`)
                .then((data) => contacts.value = data.items)
        }

        onMounted(() => {
            contactInit()
        })

        const removeContact = (id: number) => {
            Api.delete(`contacts/${id}`)
                .then(() => contactInit())
        }

        return {
            contacts,
            removeContact,
            DateUtil
        }
    }
});
</script>