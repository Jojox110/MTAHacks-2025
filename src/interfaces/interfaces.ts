export interface message{
    content:string;
    role: 'user' | 'assistant';
    id:string;
}