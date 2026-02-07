/**
 * VILLAR DASHBOARD - Lógica Completa (Sin Duplicación)
 */

// --- 1. TEMA ---
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('villar_theme', theme);
    const icon = document.getElementById('themeIcon');
    const text = document.getElementById('themeText');
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    if (text) text.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro';
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    applyTheme(current === 'dark' ? 'light' : 'dark');
}

// --- 2. MODAL Y PRODUCTOS ---
const modal = document.getElementById('modalOverlay');

function openModal() {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function updateProductRow(id) {
    const checkbox = document.getElementById('p-' + id);
    const card = document.getElementById('card-' + id);
    const wrapper = document.getElementById('wrapper-' + id);
    const input = document.getElementById('cant-input-' + id);

    if (checkbox.checked) {
        card.style.borderColor = 'var(--primary)';
        card.style.background = 'var(--primary-soft)';
        wrapper.style.opacity = '1';
        wrapper.style.pointerEvents = 'all';
        if(input) input.focus();
    } else {
        card.style.borderColor = 'var(--border)';
        card.style.background = 'transparent';
        wrapper.style.opacity = '0.4';
        wrapper.style.pointerEvents = 'none';
    }
}

function filterModalProducts() {
    let val = document.getElementById('modalSearch').value.toLowerCase();
    document.querySelectorAll('.prod-card').forEach(card => {
        card.style.display = card.dataset.name.includes(val) ? "flex" : "none";
    });
}

function displayFileName() {
    const input = document.getElementById('archivo');
    const textDisplay = document.getElementById('file-name-text');
    if (input.files.length > 0) {
        textDisplay.innerHTML = `✅ <b>${input.files[0].name}</b>`;
    }
}

// --- 3. CRONÓMETROS ---
function updateTimers() {
    document.querySelectorAll('.user-row').forEach(row => {
        const createdAt = new Date(row.getAttribute('data-created'));
        const status = row.getAttribute('data-status');
        const timerEl = row.querySelector('.timer-text');
        
        if (status === 'Enviado') {
            if (timerEl) timerEl.textContent = "✓ FINALIZADO";
            return;
        }

        const diff = new Date() - createdAt;
        const h = Math.floor(diff / 3600000).toString().padStart(2,'0');
        const m = Math.floor((diff % 3600000) / 60000).toString().padStart(2,'0');
        const s = Math.floor((diff % 60000) / 1000).toString().padStart(2,'0');
        
        if (timerEl) timerEl.textContent = `${h}:${m}:${s}`;
    });
}

// --- 4. POLLING SIN DUPLICADOS ---
function fetchDashboardData() {
    // Si el modal está activo, pausamos el refresco para no perder selecciones
    if (modal && modal.classList.contains('active')) return;

    fetch('/dashboard', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.text())
    .then(html => {
        const container = document.getElementById('historial-peticiones');
        if (container && html.trim().length > 0) {
            // Reemplazo TOTAL del contenido interno
            container.innerHTML = html;
            updateTimers();
        }
    })
    .catch(err => console.warn("Error en actualización:", err));
}

// --- 5. INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    applyTheme(localStorage.getItem('villar_theme') || 'light');
    updateTimers();
    setInterval(updateTimers, 1000);
    setInterval(fetchDashboardData, 8000); // Polling cada 8s
});

window.onclick = (e) => { if (e.target == modal) closeModal(); }