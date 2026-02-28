<template>
<div class="flex flex-col md:flex-row flex-wrap justify-between gap-6 p-4 bg-white rounded-lg shadow-sm">
    <div class="flex flex-col w-full md:w-1/2 lg:w-[500px]">
        <div class="flex flex-col space-y-4">
            <h1 class="text-2xl font-semibold text-gray-800">Памятка стендиста</h1>
            <div class="text-md text-gray-600 bg-red-50 p-4 rounded-lg">
                <p class="font-medium">Внимание!</p>
                <p>Памятка заполняется для каждого посетителя. Все вопросы обязательны для заполнения.</p>
            </div>
            <div class="text-gray-700 p-4 bg-orange-50 rounded-lg border border-amber-100">
                <p class="font-medium mb-2">Загрузка визитной карточки</p>
                <p>Загрузить визитную карточку можно нажав на область визитки и сфотографировав или вручную нажатием на
                    загрузить из галлереи</p>
            </div>
        </div>
    </div>
    <div class="flex flex-col w-full md:w-1/2 justify-end">
        <div class="flex flex-col sm:flex-row w-full gap-4">
            <div class="flex flex-col gap-2 w-full"
                 v-for="value in ['business_card_front', 'business_card_back']"
                 :key="value">
                <VisitCardPhotoModal v-if="visitCardModalsOpen[value as keyof typeof visitCardModalsOpen]"
                                     :name="value"
                                     @capturePicture="getPicture"
                                     @close="visitCardModalsOpen[value as keyof typeof visitCardModalsOpen] = false" />

                <div class="bg-gray-50 p-4 rounded-lg border-2 border-dashed border-gray-300 cursor-pointer hover:border-orange-400 transition-colors h-[230px] flex items-center justify-center"
                     @click="visitCardModalsOpen[value as keyof typeof visitCardModalsOpen] = true">
                    <div class="flex flex-col items-center justify-center text-center p-2 w-full h-full">
                        <img v-if="streamScreen[value as keyof typeof streamScreen]"
                             class="object-contain max-h-full max-w-full"
                             :src="URL.createObjectURL(streamScreen[value as keyof typeof streamScreen] as Blob)">
                        <div v-else
                             class="flex flex-col items-center text-gray-500">
                            <svg xmlns="http://www.w3.org/2000/svg"
                                 class="h-12 w-12 mb-2"
                                 fill="none"
                                 viewBox="0 0 24 24"
                                 stroke="currentColor">
                                <path stroke-linecap="round"
                                      stroke-linejoin="round"
                                      stroke-width="2"
                                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span class="text-wrap">
                                {{ value == 'business_card_front' ? 'Передняя часть визитки' : 'Задняя часть визитки' }}
                            </span>
                        </div>
                    </div>
                </div>
                <input type="file"
                       class="hidden"
                       @change="handleHandFileUpload(value)"
                       :ref="value == 'business_card_front' ? 'userCardFront' : 'userCardBack'" />
                <div @click="openFileWindow(value)"
                     class="text-center py-2 px-4 bg-white border hover:border-[var(--brand-orange)] border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 cursor-pointer transition-colors">
                    Загрузить из галлереи
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script lang='ts'>
import { defineComponent, ref, watch } from 'vue';
import VisitCardPhotoModal from './VisitCardPhotoModal.vue';
import Api from '@/utils/Api';
import { urlToFile } from '@/utils/urlToFile';

interface IGetContactFile {
    "file_id": number,
    "name": string,
    "type": string,
    "url": string,
    "format": string,
    "created_at": string
}

export default defineComponent({
    props: {
        contactId: {
            type: String
        }
    },
    components: {
        VisitCardPhotoModal
    },
    setup(props, { emit }) {
        const camCapture = ref<HTMLVideoElement | null>(null);
        const canvasElement = ref<HTMLCanvasElement | null>(null);

        const userCardFront = ref();
        const userCardBack = ref();

        const streamScreen = ref<{ business_card_front: File | null, business_card_back: File | null }>({
            business_card_front: null,
            business_card_back: null
        });

        const visitCardModalsOpen = ref({
            business_card_front: false,
            business_card_back: false
        })

        const openFileWindow = (key: string) => {
            return key == 'business_card_front' ? userCardFront.value[0].click() : userCardBack.value[0].click();
        }

        const handleHandFileUpload = (key: string) => {
            if (!key) return
            return key == 'business_card_front' && userCardFront.value[0].files[0] ?
                streamScreen.value.business_card_front = userCardFront.value[0].files[0] :
                userCardBack.value[0].files[0] ? streamScreen.value.business_card_back = userCardBack.value[0].files[0] : ''
        }

        watch((streamScreen.value), () => {
            emit('fileUploaded', streamScreen.value)
        }, { deep: true })

        const getPicture = (file: File, name: string) => {
            visitCardModalsOpen.value[name as keyof typeof visitCardModalsOpen.value] = false;
            streamScreen.value[name as keyof typeof streamScreen.value] = file;
        }

        watch((props), () => {
            if (props.contactId) {
                Api.get(`contacts/${props.contactId}/files`)
                    .then((data) => {
                        if (data && data?.files.length) {
                            const keys = ['business_card_back', 'business_card_front'];
                            keys.forEach(key => {
                                if (data.files.find((el: IGetContactFile) => el.type == key)) {
                                    urlToFile(`${import.meta.env.VITE_API_URL}${data.files.find((el: IGetContactFile) => el.type == key).url}`, key)
                                        .then(e => streamScreen.value[key as keyof typeof streamScreen.value] = e)
                                }
                            })
                        }
                    })
            }
        }, { immediate: true, deep: true })

        return {
            userCardFront,
            userCardBack,
            camCapture,
            openFileWindow,
            canvasElement,
            streamScreen,
            // removePicture,
            handleHandFileUpload,
            URL,
            getPicture,
            visitCardModalsOpen,
        }
    }
});
</script>