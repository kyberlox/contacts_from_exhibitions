export const passport = [
    {
        title: 'Название компании',
        name: 'title'
    },
    {
        title: 'ФИО',
        name: 'full_name'
    },
    {
        title: 'Город',
        name: 'city'
    },
    {
        title: 'Должность',
        name: 'position'
    },
    {
        title: 'Телефон',
        name: 'phone_number'
    },
    {
        title: 'E-mail',
        name: 'email'
    },
]

export const radios = {
    name: 'position', 
    values:[
    { id: 1, name: 'Проектный институт', value: false },
    { id: 2, name: 'Потребитель', value: false },
    { id: 3, name: 'Конкурент', value: false },
    { id: 4, name: 'Другое', value: false },
]
}

export const checkboxGroup = [
    {
            title: 'Интересующая Вас продукция?',
            name: 'product_type',
            choices: [
                {
                    id: 1, name: 'Краны шаровые', value: false, 
                },
                {
                    id: 2, name: 'Затворы дисковые', value: false, 
                },
                {
                    id: 3, name: 'Клапаны обратные', value: false, 
                },
                {
                    id: 4, name: 'Сильфоны и компенсаторы', value: false, 
                },
                {
                    id: 5, name: 'Задвижки', value: false, 
                },
                {
                    id: 6, name: 'Криогенная арматура', value: false, 
                },
                {
                    id: 7, name: 'Блочно-модульное оборудование', value: false, 
                },
                {
                    id: 8, name: 'Самостабилизатор давления', value: false, 
                },
                {
                     id: 9, name: 'Электроприводы', value: false,
                },
                {
                     id: 10, name: 'Регулирующая арматура', value: false,
                },
                {
                     id: 11, name: 'Предохранительная арматура', value: false,
                },
                {
                     id: 12, name: 'Другое', value: false,
                },
            ]
    },
    {
            title: 'Какие производители Вас заинтересовали?',
            name: 'manufacturer',
            choices: [
                {
                    name: 'Саратовский арматурный завод', value: false, id: 1
                },
                {
                    name: 'Курганспецарматура', value: false, id: 2
                },
                {
                    name: 'НПО Регулятор', value: false, id: 3
                },
                {
                    name: 'Техпромарма', value: false, id: 4
                },
                {
                    name: 'Арматом', value: false, id: 5
                },
                {
                    name: 'Тулаэлектропривод', value: false, id: 6
                },
                {
                    name: 'Пульсатор', value: false, id: 7
                },
                {
                    name: 'Техно-Сфера', value: false, id: 8
                },
                {
                    name: 'Другое', value: false, id: 9
                },
            ]
    },
]