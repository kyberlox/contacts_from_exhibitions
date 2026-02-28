export interface IPostContacts {
    title: string;
    description: string;
    full_name: string;
    position: string;
    email: string;
    phone_number: string;
    city: string;
    questionnaire: {
        product_type: string[];
        manufacturer: string[];
        contact_typeL: string
    }
}
