const sidebar = document.getElementById('sidebarColumn');
const toggleBtn = document.getElementById('toggleSidebar');

if (sidebar && toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}
