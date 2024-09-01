let totalChartInstance = null;
let meanTableInstance = null;
let shareChartInstance = null;

// Function to render a line chart
const renderLineChart = (chartInstance, canvasId, chartTitle, labels, data) => {
  const ctx = document.getElementById(canvasId);

  if (chartInstance) {
    chartInstance.destroy();
  }

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Expenses",
          data: data,
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: {
        title: {
          display: false,
          text: chartTitle,
        },
        legend: {
          align: "start",
        },
      },
    },
  });
};

// Function to render a polar area chart
const renderPolarAreaChart = (
  chartInstance,
  canvasId,
  chartTitle,
  labels,
  data
) => {
  const ctx = document.getElementById(canvasId);

  if (chartInstance) {
    chartInstance.destroy();
  }

  return new Chart(ctx, {
    type: "polarArea",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Expenses",
          data: data,
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: {
        title: {
          display: false,
          text: chartTitle,
        },
        legend: {
          align: "start",
        },
      },
    },
  });
};

// Function to render a table and print to console
const renderTable = (tableId, data) => {
  const table = document.getElementById(tableId);
  let tableHtml = `
    <thead>
      <tr>
        <th>Category</th>
        <th>Average Expense</th>
      </tr>
    </thead>
    <tbody>`;

  let totalSum = 0; // Initialize total sum for average expenses
  let itemCount = 0; // Initialize item count for calculating the total average

  for (const [category, average] of Object.entries(data)) {
    const averageNumber = Number(average); // Convert to number
    if (!isNaN(averageNumber)) {
      totalSum += averageNumber; // Accumulate total sum
      itemCount += 1; // Increment item count
    }

    tableHtml += `
      <tr>
        <td>${category}</td>
        <td>${isNaN(averageNumber) ? "N/A" : averageNumber.toFixed(2)}</td>
      </tr>`;
  }

  // Calculate total average
  const totalAverage =
    itemCount > 0 ? (totalSum / itemCount).toFixed(2) : "N/A";

  tableHtml += `
    </tbody>
    <tfoot>
      <tr>
        <td><strong>Total</strong></td>
        <td><strong>${totalAverage}</strong></td>
      </tr>
    </tfoot>`;

  table.innerHTML = tableHtml;

  // Print category and average to the console
  console.log(`Total Average: ${totalAverage}`);
};

// Function to get data and render charts/tables
const getChartData = (interval) => {
  const types = ["total", "mean", "proportions"];

  types.forEach((type) => {
    fetch(
      `/expenses/get_expenses_by_category/${interval}?calculation_type=${type}`
    )
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((results) => {
        const expenses_by_category = results.expenses_by_category || {};
        const [labels, data] = [
          Object.keys(expenses_by_category),
          Object.values(expenses_by_category),
        ];

        switch (type) {
          case "total":
            totalChartInstance = renderLineChart(
              totalChartInstance,
              "total_chart",
              "Total Expenses by Category",
              labels,
              data
            );
            break;
          case "mean":
            renderTable("mean_table", expenses_by_category);
            break;
          case "proportions":
            shareChartInstance = renderPolarAreaChart(
              shareChartInstance,
              "share_chart",
              "Expense Share by Category",
              labels,
              data
            );
            break;
          default:
            console.error("Invalid calculation type.");
        }
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  });
};

// Set default chart load
document.addEventListener("DOMContentLoaded", () => {
  const defaultInterval = "Year";

  // Initialize charts and table with default interval
  getChartData(defaultInterval);

  // Add event listener for interval change
  document
    .getElementById("intervalSelect")
    .addEventListener("change", (event) => {
      const selectedInterval = event.target.value;

      // Fetch data for all charts and table based on selected interval
      getChartData(selectedInterval);
    });
});
