// Initialize chart instances
let totalChartInstance = null;
let meanTableInstance = null;
let shareChartInstance = null;

// Function to render a line chart
const renderLineChart = (chartInstance, canvasId, jsonData) => {
  const ctx = document.getElementById(canvasId).getContext('2d');

  const labels = jsonData.labels;
  const datasets = jsonData.datasets.map(dataset => ({
    label: dataset.label,
    data: dataset.data.map(value => Number(value)),
    borderWidth: dataset.borderWidth
  }));

  if (chartInstance) {
    chartInstance.destroy();
  }

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: datasets
    },
    options: {
      plugins: {
        legend: {
          align: "start"
        }
      }
    }
  });
};

// Function to render a polar area chart
const renderPolarAreaChart = (chartInstance, canvasId, jsonData) => {
  const ctx = document.getElementById(canvasId).getContext('2d');

  if (chartInstance) {
    chartInstance.destroy();
  }

  return new Chart(ctx, {
    type: "polarArea",
    data: {
      labels: jsonData.labels,  // Use the provided labels
      datasets: jsonData.datasets.map(dataset => ({
        label: dataset.label,
        data: dataset.data.map(value => Number(value).toFixed(0)),  // Ensure percentages are formatted to 2 decimal places
        borderWidth: dataset.borderWidth
      }))
    },
    options: {
      plugins: {
        legend: {
          align: "start"
        }
      }
    }
  });
};

// Function to render a table
const renderTable = (tableId, jsonData) => {
  const table = document.getElementById(tableId);
  let tableHtml = `
    <thead>
      <tr>
        <th>Category</th>
        <th>Average Income</th>
      </tr>
    </thead>
    <tbody>`;

  let totalSum = 0;
  let itemCount = 0;

  jsonData.labels.forEach((category, index) => {
    const average = jsonData.datasets[0].data[index];
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
  });

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
  const types = ["total", "mean", "share"];

  types.forEach((type) => {
    const url = `/incomes/get_incomes_by_category/${interval}?calculation_type=${type}`;
    console.log(`Fetching data from: ${url}`);

    fetch(url)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((results) => {
        const incomes_by_category = results.incomes_by_category || {};
        console.log(`Results for ${type}:`, incomes_by_category);

        switch (type) {
          case "total":
            totalChartInstance = renderLineChart(
              totalChartInstance,
              "total_chart",
              incomes_by_category
            );
            break;
          case "mean":
            renderTable("mean_table", incomes_by_category);
            break;
          case "share":
            shareChartInstance = renderPolarAreaChart(
              shareChartInstance,
              "share_chart",
              incomes_by_category,
            );
            break;
          default:
            console.error("Invalid calculation type.");
        }
      })
      .catch((error) => {
        console.error(`Error fetching data for ${type}:`, error);
        alert(`Error fetching data for ${type}: ${error.message}`);
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
