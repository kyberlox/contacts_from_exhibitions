<template>
<header class="z-[0]">
    <div class="header bg-white shadow-md">
        <div
             class="header__wrapper max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4 flex flex-col sm:flex-row justify-between items-center">
            <div class="header__logo__wrapper mb-3 sm:mb-0">
                <RouterLink :to="{ name: 'contact' }"
                            class="header__logo">
                    <img src="@/assets/logo.png"
                         alt="logo"
                         class="h-8 sm:h-10 md:h-12 w-auto">
                </RouterLink>
            </div>
            <nav class="w-full sm:w-auto">
                <ul
                    class="header__navbar flex flex-wrap justify-center sm:justify-end items-center space-x-2 sm:space-x-4 md:space-x-8">
                    <RouterLink :to="{ name: nav.route }"
                                v-for="(nav) in headerLinks"
                                :key="'nav' + nav.id"
                                class="text-theme-grey-blue hover:text-theme-blue-dark font-medium transition-colors duration-200 text-sm sm:text-base px-2 py-1 rounded hover:bg-gray-100 cursor-pointer flex items-center">
                        {{ nav.title }}
                    </RouterLink>
                </ul>
            </nav>
        </div>
    </div>
</header>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { headerLinks } from "@/assets/data";

export default defineComponent({
    name: "HeaderMos",
    emits: ['scrollToEl'],
    setup(props, { emit }) {
        const activeIndex = ref();

        const subPointActive = ref(false);
        const handleSubpoints = (value: boolean, id: number) => {
            subPointActive.value = value;
            activeIndex.value = id;
        }

        const handleScrollTabs = (route: string) => {
            emit('scrollToEl', route);
        }

        return {
            headerLinks,
            subPointActive,
            handleSubpoints,
            activeIndex,
            handleScrollTabs
        }
    }
})
</script>