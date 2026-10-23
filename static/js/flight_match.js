/* File controls and FAQs from the supplied concept; submission uses Django. */
function toggleFaq(num) {
    const answer = document.getElementById('faq-ans-' + num);
    const open = answer.classList.toggle('hidden') === false;
    document.getElementById('faq-icon-' + num).classList.toggle('rotate-180', open);
    document.querySelector('[aria-controls="faq-ans-' + num + '"]').setAttribute('aria-expanded', String(open));
}
function handleFileSelected(input, previewId, emptyId, nameId) {
    const file = input.files[0];
    if (!file) return;
    document.getElementById(emptyId).classList.add('hidden');
    const preview = document.getElementById(previewId);
    preview.classList.remove('hidden');
    preview.classList.add('flex');
    document.getElementById(nameId).textContent = Array.from(input.files, item => item.name).join('\n');
}
function removeFile(inputId, previewId, emptyId) {
    document.getElementById(inputId).value = '';
    document.getElementById(previewId).classList.add('hidden');
    document.getElementById(previewId).classList.remove('flex');
    document.getElementById(emptyId).classList.remove('hidden');
}
document.querySelectorAll('#sama-match-page [onclick^="toggleFaq"]').forEach((button, index) => {
    button.type = 'button';
    button.setAttribute('aria-controls', 'faq-ans-' + (index + 1));
    button.setAttribute('aria-expanded', 'false');
});
// A transparent native file input covers each drop zone, supporting keyboard,
// tap and drag/drop without hiding required controls from browser validation.
const matchForm = document.getElementById('samaMatchForm');
if (matchForm) {
    const phone = document.getElementById('inputWhatsApp');
    const email = document.getElementById('inputEmail');
    const checkContact = () => {
        phone.required = !email.value.trim();
        email.required = !phone.value.trim();
    };
    phone.addEventListener('input', checkContact);
    email.addEventListener('input', checkContact);
    checkContact();
    if (matchForm.querySelector('.match-errors')) {
        matchForm.scrollIntoView({block:'start'});
    }
}
