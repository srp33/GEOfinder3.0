const data = [...Array(200).keys()].map(i => ({ id: i + 1, name: `Item ${i + 1}`, info: `Info ${i + 1}` })); // Example data
let currentPage = 1;
const itemsPerPage = 10;

function renderTable(page) {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const paginatedItems = data.slice(start, end);
    const resultsBody = document.getElementById('results-body');

    resultsBody.innerHTML = paginatedItems.map(item => `
        <tr>
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.info}</td>
        </tr>
    `).join('');
}

function updatePagination() {
    document.getElementById('prev-btn').disabled = currentPage === 1;
    document.getElementById('next-btn').disabled = currentPage * itemsPerPage >= data.length;
}

document.getElementById('prev-btn').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        renderTable(currentPage);
        updatePagination();
    }
});

document.getElementById('next-btn').addEventListener('click', () => {
    if (currentPage * itemsPerPage < data.length) {
        currentPage++;
        renderTable(currentPage);
        updatePagination();
    }
});

// Initial render
renderTable(currentPage);
updatePagination();
