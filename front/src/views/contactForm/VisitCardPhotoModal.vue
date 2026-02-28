<template>
<SlotModal>
    <div class="flex flex-col gap-1 h-full">
        <div
             class="p-2 border-2 border-white h-full  border-dashed justify-center flex items-center min-w-[375px] min-h-[214px] relative">
            <video class="object-cover max-h-full aspect-video z-0 h-full"
                   ref="camCapture"
                   autoplay
                   playsinline>

            </video>
            <div class="absolute max-h-[100%] h-[500px] aspect-video border-green-500 border-4 bg-[#00000052]"></div>
            <canvas ref="canvasElement"
                    class="hidden"></canvas>
        </div>
        <div class="w-full">
            <div class="m-auto rounded-lg bg-amber-400 hover:bg-amber-500 border-black border-1 w-fit py-2 px-4 text-center cursor-pointer"
                 @click="capturePicture">
                Фото
            </div>
        </div>
    </div>
</SlotModal>
</template>

<script lang='ts'>
import { defineComponent, onMounted, ref, } from 'vue';
import SlotModal from '@/components/SlotModal.vue';

export default defineComponent({
    components: {
        SlotModal
    },
    props: {
        name: {
            type: String
        }
    },
    emits: ['capturePicture'],
    setup(props, { emit }) {
        const camCapture = ref<HTMLVideoElement | null>(null);
        const canvasElement = ref<HTMLCanvasElement | null>(null);
        const userCard = ref();
        const streamScreen = ref<File[]>([]);

        const initCamera = () => {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } } })
                    .then(stream => {
                        if (camCapture.value) {
                            camCapture.value.srcObject = stream;
                        }
                    })
                    .catch(error => {
                        console.error("Error accessing camera:", error);
                    });
            } else {
                console.error("getUserMedia is not supported in this browser");
            }
        };

        const capturePicture = () => {
            if (!camCapture.value || !canvasElement.value) return;
            const video = camCapture.value;
            const canvas = canvasElement.value;
            const context = canvas.getContext('2d');
            if (!context) return;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            canvas.toBlob((blob) => {
                if (!blob) return;
                const file = new File([blob], 'image.png', { type: 'image/png' });
                emit('capturePicture', file, props.name,)
            });
        };

        onMounted(() => {
            initCamera()
        })

        return {
            camCapture,
            canvasElement,
            userCard,
            streamScreen,
            capturePicture
        }
    }
});
</script>