<template>
<div class="max-w-[1200px] m-auto mt-6 px-4"
     v-if="!isLoading">
    <h1 class="text-2xl font-semibold text-gray-800 mb-6">Выставки</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <RouterLink :to="{ name: 'contactPage', params: { id: event.id } }"
                    v-for="event in events"
                    :key="event.id"
                    class="block group">
            <div
                 class="border border-gray-200 rounded-xl p-5 transition-all duration-300 hover:shadow-lg hover:border-brand-orange">
                <h2
                    class="text-xl font-semibold text-gray-800 mb-2 group-hover:text-brand-orange transition-colors duration-300">
                    {{ event.title || 'не заполнено' }}</h2>
                <p class="text-gray-600 mb-4">{{ event.description || 'не заполнено' }}</p>
                <div class="text-sm text-gray-500">
                    <div v-if="event.start_date"
                         class="mb-1">{{ `Дата начала: ` + DateUtil.changeDateToDMY(event.start_date) }}</div>
                    <div v-if="event.end_date">{{ `До: ` + DateUtil.changeDateToDMY(event.end_date) }}</div>
                </div>
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
import DateUtil from '@/utils/DateUtil';
import Loader from '@/components/Loader.vue';

export default defineComponent({
    components: {
        Loader
    },
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
        const isLoading = ref(true);

        onMounted(() => {
            isLoading.value = true;
            Api.get('exhibitions/')
                .then((data) => events.value = data.items)
                .finally(() => isLoading.value = false)
        })
        return {
            events,
            isLoading,
            DateUtil
        }
    }
});
</script>