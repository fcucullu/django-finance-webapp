// Initialize chart instances
let totalChartInstance = null;
let meanTableInstance = null;
let shareChartInstance = null;

// Function to render a line chart
const renderLineChart = (chartInstance, canvasId, jsonData) => {
  const ctx = document.getElementById(canvasId).getContext('2d');

  // Convert the JSON data to the correct format for Chart.js
  const labels = jsonData.labels;
  const datasets = jsonData.datasets.map(dataset => ({
    label: dataset.label,
    data: dataset.data.map(value => Number(value)),  // Convert Decimal to Number
    borderWidth: dataset.borderWidth
  }));

  // Destroy the existing chart instance if it exists
  if (chartInstance) {
    chartInstance.destroy();
  }

  // Create a new Chart.js instance
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: 'Your Chart Title'
        },
        legend: {
          align: "start"
        }
      }
    }
  });
};

// Function to render a polar area chart
const renderPolarAreaChart = (chartInstance, canvasId, labels, data, chartTitle = '') => {
  const ctx = document.getElementById(canvasId).getContext('2d');

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
          borderWidth: 1
        }
      ]
    },
    options: {
      plugins: {
        title: {
          display: false,
          text: chartTitle
        },
        legend: {
          align: "start"
        }
      }
    }
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

  let totalSum = 0;
  let itemCount = 0;

  for (const [category, average] of Object.entries(data)) {
    const averageNumber = Number(average);
    if (!isNaN(averageNumber)) {
      totalSum += averageNumber;
      itemCount += 1;
    }

    tableHtml += `
      <tr>
        <td>${category}</td>
        <td>${isNaN(averageNumber) ? "N/A" : averageNumber.toFixed(2)}</td>
      </tr>`;
  }

  const totalAverage = itemCount > 0 ? (totalSum / itemCount).toFixed(2) : "N/A";

  tableHtml += `
    </tbody>
    <tfoot>
      <tr>
        <td><strong>Total</strong></td>
        <td><strong>${totalAverage}</strong></td>
      </tr>
    </tfoot>`;

  table.innerHTML = tableHtml;
};

// Function to get data and render charts/tables
const getChartData = (interval) => {
  const types = ["total", "mean", "proportions"];

  types.forEach((type) => {
    fetch(`/expenses/get_expenses_by_category/${interval}?calculation_type=${type}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((results) => {
        const expenses_by_category = results.expenses_by_category || {};

        switch (type) {
          case "total":
            totalChartInstance = renderLineChart(
              totalChartInstance,
              "total_chart",
              expenses_by_category
            );
            break;
          case "mean":
            renderTable("mean_table", expenses_by_category);
            break;
          case "proportions":
            shareChartInstance = renderPolarAreaChart(
              shareChartInstance,
              "share_chart",
              Object.keys(expenses_by_category),
              Object.values(expenses_by_category)
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
  getChartData(defaultInterval);

  document
    .getElementById("intervalSelect")
    .addEventListener("change", (event) => {
      const selectedInterval = event.target.value;
      getChartData(selectedInterval);
    });
});
