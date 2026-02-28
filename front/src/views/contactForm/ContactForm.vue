<template>
<div class="max-w-7xl m-auto mt-4  flex flex-col gap-2 justify-center w-full">
    <div v-if="author"
         class="ml-auto"><b>{{ `Автор: ${author}` }}</b></div>
    <ContactFormHeader @fileUploaded="fileUploaded"
                       :contactId="id" />
    <div class="flex flex-col mt-2 gap-2"
         v-if="keywords.length">
        <h1>
            Визитная карточка успешно распознана, нажмите на подсказку, чтобы скопировать текст
        </h1>
        <div class="flex flex-row flex-wrap gap-2">
            <div v-for="(key, index) in keywords"
                 :key="index"
                 class="rounded-lg border  border-black py-1 px-2 bg-gray-200 hover:bg-gray-300 cursor-pointer"
                 :class="{ 'bg-orange-200': textInClip == (key) }"
                 @click="copyText(key)">
                {{ key }}
            </div>
        </div>
    </div>
    <div class="flex flex-col gap-2 mt-2">
        <h2 class="m-auto">Контактная информация:</h2>
        <!-- Верхник блок о заказчике -->
        <div class="flex flex-row gap-2 flex-wrap"
             v-for="(question, index) in passportRef"
             :key="'p' + index">
            <div class="text-orange-[var(--brand-orange)]">{{ question.title }}</div>
            <input class="border-b-2 border-[var(--brand-orange)] outline-0 flex-grow"
                   v-model="passportData[question.name as keyof typeof passportData]" />
        </div>
        <!-- В чем интерес клиента -->
        <div class="relative border border-[var(--brand-orange)] min-h-[500px] p-4 rounded-lg mt-2">
            <textarea class="absolute w-full h-full max-w-[97%] flex-1 resize-none p-1 outline-0 placeholder:text-[var(--brand-orange)] placeholder:text-3xl placeholder:text-center"
                      placeholder="В чем интерес клиента?"
                      v-model="passportData.description"></textarea>
        </div>
        <!-- Кто клиент -->
        <div class="border border-[var(--brand-orange)] rounded-lg p-4 grid grid-cols-4  gap-x-10 gap-1">
            <div class="flex flex-row items-center justify-between gap-1 group"
                 v-for="radio in radiosRef.values"
                 :key="'r' + radio.id">
                <label class="flex items-center gap-2 cursor-pointer group">
                    <span class="w-5 h-5 border-2 border-[var(--brand-orange)] flex items-center justify-center">
                        <input type="radio"
                               class="hidden"
                               :checked="questionaireData[radiosRef.name as keyof typeof questionaireData].includes(radio.name) || Boolean(radio.name == 'ДРУГОЕ' && additionalChoices.find(e => e.name == radiosRef.name as keyof typeof additionalChoices)?.value)"
                               :name=radiosRef.name
                               @change="handleProductPick('radio', radiosRef.name, radio.name)" />
                        <span class="w-3 h-3 group-has-[input:checked]:bg-green-500"></span>
                    </span>
                    <span :class="{ 'group-has-[input:checked]:hidden': radio.name == 'ДРУГОЕ' }">{{
                        radio.name }}
                    </span>
                    <input v-if="radio.name == 'ДРУГОЕ'"
                           class="border-b-2 border-[var(--brand-orange)] outline-0 flex-grow invisible group-has-[input:checked]:visible"
                           v-model="additionalChoices.find(el => el.name == radiosRef.name)!.value" />
                </label>
            </div>
        </div>
        <!-- Интересующая продукция и производители -->
        <div class="flex flex-col gap-5">
            <div class="border-1 border-[var(--brand-orange)] rounded-lg p-4"
                 v-for="(checkboxBlock, index) in checkboxGroupRef"
                 :key="index + 'checkbox'">
                <h3>
                    <b>{{ checkboxBlock.title }}</b>
                </h3>
                <div class="grid gap-x-10 gap-1 mt-5 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
                    <div v-for="checkbox in checkboxBlock.choices"
                         :key="'r' + checkbox.id">
                        <label class="flex justify-start gap-2 cursor-pointer group">
                            <span
                                  class="w-5 h-5 border-2 border-[var(--brand-orange)] flex items-center justify-center">
                                <input type="checkbox"
                                       :name="checkbox.name"
                                       :checked="questionaireData[checkboxBlock.name as keyof typeof questionaireData].includes(checkbox.name) || Boolean(checkbox.name == 'ДРУГОЕ' && additionalChoices.find(e => e.name == radiosRef.name as keyof typeof additionalChoices)?.value)"
                                       class="hidden"
                                       @change="handleProductPick('checkbox', checkboxBlock.name, checkbox.name)" />
                                <span class="w-3 h-3 group-has-[input:checked]:bg-green-500"></span>
                            </span>
                            <span :class="{ 'group-has-[input:checked]:hidden': checkbox.name == 'ДРУГОЕ' }">
                                {{
                                    checkbox.name
                                }}
                            </span>
                            <input v-if="(checkbox.name == 'ДРУГОЕ')"
                                   class="border-b-2 border-[var(--brand-orange)] outline-0 flex-grow invisible group-has-[input:checked]:visible"
                                   v-model="additionalChoices.find((e) => e.name == checkboxBlock.name)!.value" />
                        </label>
                    </div>
                </div>
            </div>
        </div>
        <!-- Кнопк отправки -->
        <div class="mt-1 w-full">
            <div class="border-1 m-auto border-gray-400 max-w-[300px] text-center rounded-lg p-2 cursor-pointer bg-green-400 hover:bg-green-600"
                 @click="saveContact">
                Сохранить
            </div>
            <div class="m-auto max-w-[550px]">
                <span>* Отправляя контактные данные, вы подтверждаете согласие с <a
                       class="underline text-blue-600 hover:text-blue-400"
                       href="https://exhibitions.emk.ru/api/user_agreement"
                       download>пользовательским соглашением</a> и
                    даёте
                    разрешение на обработку персональных данных.</span>
            </div>
        </div>
    </div>
</div>
</template>

<script lang="ts">
export interface IUsersPassport {
    title: string,
    description: string,
    full_name: string,
    position: string,
    email: string,
    phone_number: string,
    city: string
}
export interface IUsersQuestionaire {
    product_type: string[],
    manufacturer: string[],
    contact_type: string
}

export interface IGetContact {
    "description": string,
    "author_id": number,
    "author": string,
    "full_name": string,
    "is_validated": boolean,
    "position": string,
    "validated_by_id": null | number,
    "email": string,
    "validated_at": null | string,
    "phone_number": string,
    "notes": null,
    "city": string,
    "created_at": string,
    "title": string,
    "updated_at": string,
    "id": number,
    "exhibition_id": number,
    "questionnaire"?: {
        "manufacturer": string[],
        "product_type": string[],
        "contact_type": string
    }
}

import { defineComponent, ref, watch } from 'vue';
import ContactFormHeader from '@/views/contactForm/ContactFormHeader.vue';
import { passport, checkboxGroup, radios } from '@/assets/static/formQuestions';
import Api from '@/utils/Api';
import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";
import { useUserData } from '@/store/userStore';

export default defineComponent({
    name: 'contactForm',
    components: {
        ContactFormHeader,
    },
    props: {
        id: {
            type: String
        }
    },
    setup(props) {
        const pageType = ref<'new' | 'edit'>('new');

        const passportRef = ref(passport);
        const passportData = ref<IUsersPassport>({
            title: '',
            description: '',
            full_name: '',
            position: '',
            email: '',
            phone_number: '',
            city: ''
        });
        const questionaireData = ref<IUsersQuestionaire>({
            product_type: [],
            manufacturer: [],
            contact_type: ''
        });

        const checkboxGroupRef = ref(checkboxGroup);
        const radiosRef = ref(radios);
        const options = ref(['Менеджер1', 'менеджер2']);
        const additionalChoices = ref([
            {
                name: "contact_type",
                value: '',
            },
            {
                name: "product_type",
                value: '',
            },
            {
                name: 'manufacturer',
                value: ''
            }]);

        const visitCard = ref<{ business_card_front: File | null, business_card_back: File | null }>({ business_card_front: null, business_card_back: null });
        const keywords = ref([]);
        const textInClip = ref();
        const author = ref<string>();

        const handleProductPick = (type: 'radio' | 'checkbox', key: string, item: string) => {
            if (type == 'radio') {
                if (item !== 'ДРУГОЕ') {
                    additionalChoices.value.find(e => e.name == key)!.value = '';
                    if (key in passportData.value) {
                        passportData.value[key as keyof typeof passportData.value] = item;
                    }
                    else {
                        if (Array.isArray(questionaireData.value[key as keyof typeof questionaireData.value])) {
                            (questionaireData.value[key as keyof typeof questionaireData.value] as string[]).push(item);
                        }
                        else if (typeof questionaireData.value[key as keyof typeof questionaireData.value] == 'string') {
                            (questionaireData.value[key as keyof typeof questionaireData.value] as string) = item
                        }
                    }
                }
            }
            else if (type == 'checkbox') {

                if (item == 'ДРУГОЕ' && additionalChoices.value.find(e => e.name == key)) {
                    additionalChoices.value.find(e => e.name == key)!.value = '';
                }
                else if (!questionaireData.value[key as keyof typeof questionaireData.value].includes(item) && !additionalChoices.value.find(e => e.value == item)) {
                    (questionaireData.value[key as keyof typeof questionaireData.value] as string[]).push(item);
                }
                else (questionaireData.value[key as keyof typeof questionaireData.value] as string[]).splice(questionaireData.value[key as keyof typeof questionaireData.value].indexOf(item), 1)
            }
        }

        const saveContact = () => {
            const postBody = JSON.parse(JSON.stringify({
                ...passportData.value,
                questionnaire: questionaireData.value
            }));

            const additionalChoicesKeys = ['contact_type', 'product_type', 'manufacturer']
            additionalChoicesKeys.forEach(key => {

                additionalChoices.value.forEach(e => {
                    if (e.name == key && e.value) {
                        if (Array.isArray(postBody.questionnaire[key]) && !postBody.questionnaire[key].includes(e.value)) {
                            postBody.questionnaire[key].push(e.value)
                        }
                        else if (typeof postBody.questionnaire[key] == 'string') {
                            postBody.questionnaire[key] = e.value
                        }
                    }
                })
            });

            if (pageType.value == 'new') {
                Api.post('/contacts/', postBody)
                    .then((data) => {
                        if ((visitCard.value.business_card_back || visitCard.value.business_card_front) && data.id) {
                            const newBody = new FormData();
                            Object.keys(visitCard.value).forEach(el => { if (visitCard.value[el as keyof typeof visitCard.value]) newBody.append(el, visitCard.value[el as keyof typeof visitCard.value] as Blob) })
                            Api.post(`contacts/${data.id}/files`, newBody)
                                .then((data) => {
                                    if (data.message.includes('Успешно')) {
                                        toast(data.message, { type: 'success', position: 'bottom-right' })
                                    }
                                })
                        }
                    })
            }
            else {
                Api.put(`/contacts/${props.id}`, postBody)
                    .then(() => {
                        if ((visitCard.value.business_card_back || visitCard.value.business_card_front) && props.id) {
                            const newBody = new FormData();
                            Object.keys(visitCard.value).forEach(el => newBody.append(el, visitCard.value[el as keyof typeof visitCard.value] as Blob))
                            Api.post(`contacts/${props.id}/files`, newBody)
                                .then((data) => {
                                    if (data.message.includes('Успешно')) {
                                        toast(data.message, { type: 'success', position: 'bottom-right' })
                                    }
                                })
                        }
                    })
            }
            if (!useUserData().getAdmin) {
                window.location.href = 'https://cloud.mail.ru/public/uorZ/bgpR3gNXm'
            }
        }

        const fileUploaded = (imgObj: { business_card_front: File | null, business_card_back: File | null }) => {
            visitCard.value = imgObj
            const newBody = new FormData();
            Object.keys(imgObj).forEach(e => {
                if (!imgObj[e as keyof typeof imgObj]) return
                newBody.append('file', imgObj[e as keyof typeof imgObj] as File)
                Api.post('ocr', newBody)
                    .then((data) => {
                        if (data && data.length)
                            keywords.value = data;
                    })
            })
        }

        const copyText = (key: string) => {
            navigator.clipboard.writeText(key);
            textInClip.value = key;
        }


        watch((props), () => {
            const queastionaireTypes = {
                manufacturer: checkboxGroup.find(e => e.name == 'manufacturer')?.choices.map(e => e.name),
                product_type: checkboxGroup.find(e => e.name == 'product_type')?.choices.map(e => e.name),
                contact_type: radios.values.map(e => e.name)
            }

            if (props.id) {
                pageType.value = 'edit';
                Api.get(`contacts/${props.id}`)
                    .then((data: IGetContact) => {
                        author.value = data.author;
                        const keys = ['title', 'description', 'full_name', 'position', 'email', 'phone_number', 'city'];
                        const questionnaireKeys = ['manufacturer', 'product_type', 'contact_type'];
                        keys.forEach(key => {
                            if (key in data) {
                                passportData.value[key as keyof typeof passportData.value] = data[key as (keyof typeof data)] as string;
                                questionnaireKeys.forEach(key => {
                                    if (data.questionnaire && data.questionnaire[key as keyof typeof data.questionnaire]) {
                                        const gettedResult = data.questionnaire[key as keyof typeof data.questionnaire];
                                        const isElNotInDefaultQuestionaire = (typeof gettedResult == 'string' && !queastionaireTypes[key as keyof typeof queastionaireTypes]?.find(el => el == gettedResult)) ? gettedResult : Array.isArray(gettedResult) ? gettedResult.find(el => !queastionaireTypes[key as keyof typeof queastionaireTypes]?.includes(el)) : false;


                                        if (isElNotInDefaultQuestionaire) {
                                            const target = additionalChoices.value.find(i => i.name == key);
                                            if (target) {
                                                target.value = !Array.isArray(gettedResult) ? gettedResult : isElNotInDefaultQuestionaire;
                                            }
                                        } else {
                                            if (typeof questionaireData.value[key as keyof typeof questionaireData.value] == 'string') {
                                                (questionaireData.value[key as keyof typeof questionaireData.value] as string) = gettedResult as string;
                                            } else
                                                (questionaireData.value[key as keyof typeof questionaireData.value] as string[]) = (gettedResult as string[])
                                        }

                                    }
                                })
                            }
                        });
                    })
            }
            else {
                pageType.value = 'new';
                passportData.value = ({
                    title: '',
                    description: '',
                    full_name: '',
                    position: '',
                    email: '',
                    phone_number: '',
                    city: ''
                });
                questionaireData.value = ({
                    product_type: [],
                    manufacturer: [],
                    contact_type: ''
                });
                additionalChoices.value = ([
                    {
                        name: "contact_type",
                        value: '',
                    },
                    {
                        name: "product_type",
                        value: '',
                    },
                    {
                        name: 'manufacturer',
                        value: ''
                    }]);
            };
        }, { immediate: true, deep: true })

        return {
            passportRef,
            checkboxGroupRef,
            radiosRef,
            options,
            questionaireData,
            passportData,
            additionalChoices,
            keywords,
            textInClip,
            author,
            saveContact,
            handleProductPick,
            fileUploaded,
            copyText,
        }
    }
})
</script>
