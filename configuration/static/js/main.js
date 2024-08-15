const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output-body");
const tableDefault = document.querySelector(".table-default-body");
const paginationContainer = document.querySelector(".pagination-container");
const tableOutputBody = document.querySelector(".table-output-body");

// Initially, hide the output table and show the default table
tableOutput.classList.add("hidden");
tableDefault.classList.add("visible");
paginationContainer.classList.add("visible");

searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value.trim();

    if (searchValue.length > 0) {
        tableOutputBody.innerHTML = "";

         // Always reset to the first page
        const url = new URL(window.location.href);
        url.searchParams.set('search', searchValue);
        url.searchParams.set('page', 1); // Go to the first page of results

        fetch("/search-expenses", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {

            let tableOutputBodyContent = "";
            if (data.expenses.length === 0) {
                tableOutputBodyContent = `<tr><td colspan="7" class="text-center">No results found</td></tr>`;
                paginationContainer.classList.remove("visible");
                paginationContainer.classList.add("hidden");        
            } else {
                data.expenses.forEach((item) => {
                    // Hide the default table and show the output table
                    tableDefault.classList.remove("visible");
                    tableDefault.classList.add("hidden");

                    tableOutput.classList.remove("hidden");
                    tableOutput.classList.add("visible");

                    paginationContainer.classList.remove("hidden");
                    paginationContainer.classList.add("visible");        
                    // Truncate description if it's longer than 30 characters
                    let truncatedDescription = item.description.length > 30 
                        ? item.description.slice(0, 30) + "..." 
                        : item.description;

                    tableOutputBodyContent += `
                        <tr>
                            <td>${item.owner}</td>
                            <td>${item.date}</td>
                            <td>${truncatedDescription}</td>
                            <td>${item.category}</td>
                            <td>${item.account}</td>
                            <td class="amount-cell">${item.amount}</td>
                            <td>
                              <a href="/edit-expense/${item.id}" class="btn btn-secondary btn-sm">Edit</a>
                              <button type="button" class="btn btn-danger btn-sm" data-bs-toggle="modal" data-bs-target="#deleteModal" data-id="${item.id}">Delete</button>
                            </td>
                        </tr>`;
                });
            }

            tableOutputBody.innerHTML = tableOutputBodyContent;
            searchField.value = searchValue;
        });
    } else {
        // If search field is empty, show the default table and pagination
        tableDefault.classList.remove("hidden");
        tableDefault.classList.add("visible");

        paginationContainer.classList.remove("hidden");
        paginationContainer.classList.add("visible");

        tableOutput.classList.remove("visible");
        tableOutput.classList.add("hidden");
    }
});
