document.addEventListener('DOMContentLoaded', () => {
    const attendanceBody = document.getElementById('attendance-body');
    const presentCount = document.getElementById('present-count');
    const lateCount = document.getElementById('late-count');
    const totalCount = document.getElementById('total-count');
    const filterInput = document.getElementById('log-filter');
    let attendanceRecords = [];

    // Fetch and update attendance logic
    async function updateAttendance() {
        if (!attendanceBody) return; // Only run on dashboard

        try {
            const response = await fetch('/attendance_data');
            const data = await response.json();
            attendanceRecords = data.attendance;

            // Update stats
            presentCount.innerText = data.stats.present;
            lateCount.innerText = data.stats.late;
            totalCount.innerText = data.stats.total;

            // Render logic
            renderTable();
        } catch (error) {
            console.error('Error fetching attendance data:', error);
        }
    }

    function renderTable() {
        const query = filterInput ? filterInput.value.toLowerCase() : '';
        let html = '';
        attendanceRecords.forEach(record => {
            const match = record.Name.toLowerCase().includes(query) || record['Student ID'].toString().includes(query);
            if (!match) return;

            const statusClass = record.Status.toLowerCase();
            html += `
                <tr>
                    <td>${record['Student ID']}</td>
                    <td>${record.Name}</td>
                    <td>${record.Time}</td>
                    <td><span class="status-badge status-${statusClass}">${record.Status}</span></td>
                </tr>
            `;
        });
        attendanceBody.innerHTML = html || '<tr><td colspan="4" style="text-align:center">No matches found.</td></tr>';
    }

    if (filterInput) {
        filterInput.addEventListener('input', renderTable);
    }

    // Initial load
    updateAttendance();
    // Refresh every 2 seconds
    setInterval(updateAttendance, 2000);
});
