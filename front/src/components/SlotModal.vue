<template>
<div @click.stop.prevent="close()"
     class="flex bg-[#000000b3] fixed top-0 left-0 w-full h-full items-center content-center p-0 m-0 z-10">
    <div
         class="absolute top-[20px] right-[20px] cursor-pointer flex items-center justify-center bg-[#cdcdcd] p-[5px] rounded-sm">
        <CloseIcon class="w-[30px] h-[30px]" />
    </div>
    <div class="p-[70px] h-full w-full">
        <div class="flex h-full w-full m-auto">
            <div class="w-full  overflow-x-hidden bg-white rounded-lg p-[20px] max-w-full m-auto overflow-hidden max-h-full h-full"
                 @click.stop.self>
                <slot>
                </slot>
            </div>
        </div>
    </div>
</div>
</template>
<script lang="ts">
import { defineComponent } from "vue";
import CloseIcon from "@/assets/icons/CloseIcon.svg?component";

export default defineComponent({
    props: {

    },
    components: {
        CloseIcon,
    },
    setup(props, { emit }) {
        return {
            close: () => emit("close"),
        };
    },
});
</script>