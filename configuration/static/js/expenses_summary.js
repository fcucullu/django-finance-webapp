const renderChart = (labels, data) => {
  const ctx = document.getElementById("myChart");
  const chart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Last 6 months expenses",
          data: data,
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: "Expenses by Category",
        },
      },
    },
  });
};

const getChartData = () => {
  fetch("/expenses/expense-category-summary")
    .then((res) => res.json())
    .then((results) => {
      console.log("results", results);
      const category_data = results.expense_category_data;
      const [labels, data] = [
        Object.keys(category_data),
        Object.values(category_data),
      ];
      renderChart(labels, data);
    });
};

document.onload = getChartData();
