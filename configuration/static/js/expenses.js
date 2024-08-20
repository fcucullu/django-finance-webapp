document.addEventListener('DOMContentLoaded', function () {   
    var deleteModal = document.getElementById('deleteModal');
    deleteModal.addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget; // Button that triggered the modal
        var expenseId = button.getAttribute('data-id'); // Extract info from data-* attributes
        var confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        var deleteUrl = '/expenses/delete-expense/' + expenseId;
        confirmDeleteBtn.href = deleteUrl; // Set href to the delete URL
        }); 
    }
);
  