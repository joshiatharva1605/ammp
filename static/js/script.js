// Function to fetch and display Master Data (Part Names, IDs, Stations)
async function loadMasterData() {
    const response = await fetch('/api/get_master_data');
    const data = await response.json();
    const tableBody = document.getElementById('mcBody');
    
    if (tableBody) {
        tableBody.innerHTML = '';
        // Loop through the structured JSON from app.py
        for (let partName in data) {
            for (let partId in data[partName]) {
                for (let station in data[partName][partId]) {
                    let manpower = data[partName][partId][station];
                    tableBody.innerHTML += `
                        <tr>
                            <td>${partName}</td>
                            <td>${partId}</td>
                            <td>${station}</td>
                            <td>${manpower}</td>
                            <td><button class="action-btn del">Delete</button></td>
                        </tr>`;
                }
            }
        }
    }
}

// Function to fetch available operators (Only those marked 'Present' today)
async function loadAvailableOperators() {
    const response = await fetch('/api/get_available_operators');
    const operators = await response.json();
    const opBody = document.getElementById('opBody');

    if (opBody) {
        opBody.innerHTML = '';
        operators.forEach(op => {
            opBody.innerHTML += `
                <tr>
                    <td>-</td>
                    <td>${op.name}</td>
                    <td>Skill ${op.skill}</td>
                    <td><span style="color:green">Present</span></td>
                    <td><button class="action-btn edit">Edit</button></td>
                </tr>`;
        });
    }
}

// Run these when the window loads
window.onload = () => {
    loadMasterData();
    loadAvailableOperators();
};