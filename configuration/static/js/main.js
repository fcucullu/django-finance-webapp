const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output-body");
const tableDefault = document.querySelector(".table-default-body");
const paginationContainer = document.querySelector(".pagination-container");
const tableOutputBody = document.querySelector(".table-output-body");

searchField.addEventListener("keypress", (e) => {
  if (e.key === 'Enter') {  // Check if the Enter key was pressed
      const searchValue = e.target.value.trim();

      if (searchValue.length > 0) {
          // Always reset to the first page
          const url = new URL(window.location.href);
          url.searchParams.set('search', searchValue);
          url.searchParams.set('page', 1); // Go to the first page of results
          
          // Redirect to the new URL with the search query
          window.location.href = url.toString();
      } else {
          // If search field is empty, redirect to the default state
          window.location.href = '?';
      }
  }
});

searchField.addEventListener("input", (e) => {
  const searchValue = e.target.value.trim();
  if (searchValue.length === 0) {
      // If search field is empty, redirect to the default state
      window.location.href = '?';
  }
});
