<template>
<div class="max-w-[1200px] m-auto mt-4">
    <h1>Админ-панель</h1>
    <div class="grid grid-cols-2 mt-2">
        <RouterLink :to="{ name: 'contactPage', params: { id: event.id } }"
                    v-for="event in events"
                    :key="event.id">
            <div class="border-1 p-2 border-orange rounded-lg">
                <h2>{{ event.title }}</h2>
                <div>{{ event.description }}</div>
                <div>{{ `Дата начала: ` + DateUtil.changeDateToDMY(event.start_date) }}</div>
                <div>{{ `До: ` + DateUtil.changeDateToDMY(event.end_date) }}</div>
            </div>
        </RouterLink>
    </div>
</div>
</template>
<script lang='ts'>
import Api from '@/utils/Api';
import { defineComponent, onMounted, ref } from 'vue';
import DateUtil from '@/utils/DateUtil';

export default defineComponent({
    components: {},
    props: {},
    setup() {
        const events = ref<{
            created_at: string,
            end_date: string,
            description: string,
            id: number,
            preview_file_id: number,
            start_date: string,
            title: string,
            updated_at: string
        }[]>([]);

        onMounted(() => {
            Api.get('exhibitions/')
                .then((data) => events.value = data.items)
        })
        return {
            events,
            DateUtil
        }
    }
});
</script>