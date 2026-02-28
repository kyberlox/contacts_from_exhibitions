<template>
<SlotModal>
    <div class="flex flex-col gap-6 h-full">
        <div
             class="relative w-full aspect-[16/9] max-h-[70vh] rounded-xl overflow-hidden bg-gray-900 border-2 border-dashed border-gray-600 shadow-lg">
            <video ref="camCapture"
                   autoplay
                   playsinline
                   class="w-full h-full object-cover"></video>

            <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div class="border-2 border-white border-dashed rounded-lg w-[95%] h-[90%]  opacity-70"></div>
            </div>

            <div
                 class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black opacity-20 pointer-events-none">
            </div>

            <canvas ref="canvasElement"
                    class="hidden"></canvas>
        </div>

        <div class="w-full px-4">
            <button @click="capturePicture"
                    class="w-full py-4 bg-[var(--brand-orange)] hover:bg-orange-400 cursor-pointer text-white font-semibold rounded-xl shadow-lg transform transition duration-200 hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-opacity-50">
                <div class="flex items-center justify-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg"
                         class="h-6 w-6"
                         fill="none"
                         viewBox="0 0 24 24"
                         stroke="currentColor">
                        <path stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                        <path stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Сделать фото визитки
                </div>
            </button>
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