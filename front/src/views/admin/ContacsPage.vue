<template>
<div class="max-w-[1200px] m-auto mt-4">
    <h1>Админ-панель</h1>
    <div class="grid grid-cols-3 mt-2 gap-4">
        <RouterLink :to="{ name: 'contactEdit', params: { id: contact.id } }"
                    v-for="contact in contacts"
                    :key="contact.id"
                    class="relative">
            <CloseIcon class="w-[30px] absolute right-0 hover:scale-[1.08]"
                       @click.stop.capture.prevent="removeContact(contact.id)" />
            <div class="border-1 p-2 border-orange rounded-lg">
                <h2>{{ `ФИО: ` + contact.full_name }}</h2>
                <div>{{ `Должность: ` + contact.position }}</div>
                <div>{{ `Название компании: ` + contact.title }}</div>
                <div>{{ `Название компании: ` + contact.exhibition_title }}</div>
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