document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');
    
    if (!dateInput) {
        return; // Exit if the date input element is not found
    }

    const dateValue = dateInput.value;

    // Only set to today's date if the value is empty or in the 'yyyy-mm-dd' format
    const isDefaultDate = /^\d{4}-\d{2}-\d{2}$/.test(dateValue);


    if (dateValue === '' || isDefaultDate) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
});
