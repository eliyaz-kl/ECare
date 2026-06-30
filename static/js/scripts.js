const sidebar = document.getElementById('sidebarColumn');
const toggleBtn = document.getElementById('toggleSidebar');
const userStatus = document.getElementById('userStatus');

if (sidebar && toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];

    for (const cookie of cookies) {
        const trimmedCookie = cookie.trim();

        if (trimmedCookie.startsWith(`${name}=`)) {
            return decodeURIComponent(trimmedCookie.slice(name.length + 1));
        }
    }

    return null;
}

if (userStatus) {
    let previousStatus = userStatus.value;

    userStatus.addEventListener('change', async () => {
        const selectedStatus = userStatus.value;
        userStatus.disabled = true;

        try {
            const response = await fetch(userStatus.dataset.statusUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({status: selectedStatus}),
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || 'Could not update status.');
            }

            previousStatus = selectedStatus;
        } catch (error) {
            userStatus.value = previousStatus;
            console.error(error);
            alert(error.message);
        } finally {
            userStatus.disabled = false;
        }
    });
}
