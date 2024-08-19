function showDeleteModal(type, item) {
  const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
  $("#deleteConfirmationModal").modal("show");

  confirmDeleteBtn.onclick = function () {
    deleteCategoryOrAccount(type, item);
    $("#deleteConfirmationModal").modal("hide");
  };
}

function deleteCategoryOrAccount(type, item) {
  const csrfToken = document.querySelector(
    'input[name="csrfmiddlewaretoken"]'
  ).value;

  fetch("/preferences/delete-category-or-account/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ category_type: type, item: item }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        // Reload the page and goes to the top to see messages
        window.location.reload();
        window.onload = function () {
          window.scrollTo(0, 0);
        };
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function addCategoryOrAccount(type) {
  const csrfToken = document.querySelector(
    'input[name="csrfmiddlewaretoken"]'
  ).value;
  let newItem = "";

  if (type === "income") {
    newItem = document.getElementById("new-category-income").value;
  } else if (type === "expense") {
    newItem = document.getElementById("new-category-expense").value;
  } else if (type === "account") {
    newItem = document.getElementById("new-account").value;
  }

  if (newItem) {
    fetch("/preferences/add-category-or-account/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        category_type: type,
        new_item: newItem,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          // Reload the page
          window.location.reload().scrollTo(0, 0);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
}
