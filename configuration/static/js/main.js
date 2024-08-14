const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const tableDefault = document.querySelector(".table-default");
const paginationContainer = document.querySelector(".pagination-container");
const tableOutputBody = document.querySelector(".table-output-body");

tableOutput.style.display = "none";
tableDefault.style.display = "block";

searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value.trim();
  if (!searchField) {
  }

  if (searchValue.length > 0) {
    console.log("searchValue", searchValue);
    paginationContainer.style.display = "none";
    tableOutputBody.innerHTML = ""

    fetch("/search-expenses", {
      body: JSON.stringify({ searchText: searchValue }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);

        tableDefault.style.display = "none";
        tableOutput.style.display = "block";

        let tableOutputBodyContent = '';  // Declaramos `tableOutputBodyContent` con `let`

        console.log("data.expenses.length:", data.expenses.length);
        if (data.expenses.length === 0) {
          tableOutputBodyContent = `<td style="text-center">No results found</td>`;
        } else {
          console.log("Data received:", data); // Verifica qué tipo de dato es "data"

          data.expenses.forEach((item) => {
            tableOutputBodyContent += `
              <tr>
                  <td>${item.owner}</td>
                  <td>${item.date}</td>
                  <td>${item.description}</td>
                  <td>${item.category}</td>
                  <td>${item.account}</td>
                  <td>${item.amount}</td>
              </tr>`;   
          });
        }

        tableOutputBody.innerHTML = tableOutputBodyContent;  // Asignamos el contenido generado a `tableOutputBody`
      });
  } else {
    tableDefault.style.display = "block";
    paginationContainer.style.display = "block";
    tableOutput.style.display = "none";
  }
});
