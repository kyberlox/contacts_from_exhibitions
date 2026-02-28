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
    }
]

export const radios = {
    name: 'contact_type', 
    values:[
    { id: 1, name: 'ПРОЕКТНЫЙ ИНСТИТУТ', value: false },
    { id: 2, name: 'ПОТРЕБИТЕЛЬ', value: false },
    { id: 3, name: 'КОНКУРЕНТ', value: false },
    { id: 4, name: 'ДРУГОЕ', value: false },
]
}

export const checkboxGroup = [
    {
            title: 'Интересующая Вас продукция?',
            name: 'product_type',
            choices: [
                {
                    id: 1, name: 'краны шаровые', value: false, 
                },
                {
                    id: 2, name: 'затворы дисковые', value: false, 
                },
                {
                    id: 3, name: 'клапаны обратные', value: false, 
                },
                {
                    id: 4, name: 'сильфоны и компенсаторы', value: false, 
                },
                {
                    id: 5, name: 'задвижки', value: false, 
                },
                {
                    id: 6, name: 'криогенная арматура', value: false, 
                },
                {
                    id: 7, name: 'блочно-модульное оборудование', value: false, 
                },
                {
                    id: 8, name: 'самостабилизатор давления', value: false, 
                },
                {
                     id: 9, name: 'электроприводы', value: false,
                },
                {
                     id: 10, name: 'регулирующая арматура', value: false,
                },
                {
                     id: 11, name: 'предохранительная арматура', value: false,
                },
                {
                     id: 12, name: 'ДРУГОЕ', value: false,
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
                    name: 'ДРУГОЕ', value: false, id: 9
                },
            ]
    },
]