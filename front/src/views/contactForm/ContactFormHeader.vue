<template>
<div class="flex flex-row flex-wrap justify-between gap-2">
    <div class="flex flex-col w-full max-w-[500px]">
        <img />
        <div class="flex flex-col">
            <h1>Памятка стендиста</h1>
            <div class="text-md">
                Внимание! Памятка заполняется для каждого посетителя.
                Все вопросы обязательны для заполнения.
            </div>
            <div>
                <b> Загрузить визитную карточку можно нажав на область визитки и сфотографировав или вручную нажатием
                    на
                    загрузить из галлереи</b>
            </div>
        </div>
    </div>
    <div class="flex flex-col w-full">
        <div class="flex flex-row space-between w-full gap-2">
            <div class="flex flex-col gap-1"
                 v-for="value in ['business_card_front', 'business_card_back']"
                 :key="value">
                <VisitCardPhotoModal v-if="visitCardModalsOpen[value as keyof typeof visitCardModalsOpen]"
                                     :name="value"
                                     @capturePicture="getPicture"
                                     @close="visitCardModalsOpen[value as keyof typeof visitCardModalsOpen] = false" />

                <div class="bg-orange-200 p-2 max-h-[230px] aspect-video"
                     @click="visitCardModalsOpen[value as keyof typeof visitCardModalsOpen] = true">
                    <div
                         class="p-2 border-2 border-white h-full border-dashed justify-center flex items-center min-w-[375px] min-h-[214px]">
                        <img v-if="streamScreen[value as keyof typeof streamScreen]"
                             class="object-cover max-h-[100%] aspect-video z-0 flex-grow"
                             :src="URL.createObjectURL(streamScreen[value as keyof typeof streamScreen] as Blob)">
                        <span v-if="!streamScreen[value as keyof typeof streamScreen]"
                              class="text-wrap max-w-[391px]">
                            {{ value == 'business_card_front' ? 'Передняя часть визитки' : 'Задняя часть визитки' }}
                        </span>
                    </div>
                </div>
                <input type="file"
                       class="hidden"
                       @change="handleHandFileUpload(value)"
                       :ref="value == 'business_card_front' ? 'userCardFront' : 'userCardBack'" />
                <div @click="openFileWindow(value)">
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

export default defineComponent({
    props: {},
    components: {
        VisitCardPhotoModal
    },
    setup(_, { emit }) {
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
            console.log(userCardBack.value);
            console.log(userCardFront.value);

            return key == 'business_card_front' ? userCardFront.value[0].click() : userCardBack.value[0].click();
        }

        const handleHandFileUpload = (key: string) => {
            if (!key) return
            return key == 'business_card_front' ?
                streamScreen.value.business_card_front = userCardFront.value[0].files[0] :
                streamScreen.value.business_card_back = userCardBack.value[0].files[0]
        }

        watch((streamScreen.value), () => {
            emit('fileUploaded', streamScreen.value)
        }, { deep: true })

        // const removePicture = () => {
        //     streamScreen.value.length = 0;
        // }

        const getPicture = (file: File, name: string) => {
            visitCardModalsOpen.value[name as keyof typeof visitCardModalsOpen.value] = false;
            streamScreen.value[name as keyof typeof streamScreen.value] = file;
        }

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