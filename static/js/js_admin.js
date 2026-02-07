/**
 * VILLAR ADMIN - Lógica de Control Sincronizada y Gestión de Stock
 */

// --- 1. GESTIÓN DE TEMA UNIVERSAL ---
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('villar_theme', theme);
    
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');
    
    if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    if (text) text.textContent = theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro';
}

function toggleTheme() {
    const target = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(target);
}

// --- 2. LÓGICA DE CRONÓMETROS ---
function updateAllTimers() {
    const now = new Date();
    document.querySelectorAll('.peticion-row').forEach(row => {
        const id = row.id.split('-')[1];
        const status = row.getAttribute('data-status');
        const timerEl = document.getElementById(`timer-${id}`);
        const labelAtraso = document.getElementById(`atraso-${id}`);
        
        if (status === 'Enviado') {
            if (timerEl) {
                timerEl.textContent = "✓ Completado";
                timerEl.style.background = "var(--success)";
                timerEl.style.color = "white";
            }
            if (labelAtraso) labelAtraso.style.display = 'none';
            return;
        }

        const createdAt = new Date(row.getAttribute('data-created'));
        const diff = now - createdAt;
        
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        const s = Math.floor((diff % 60000) / 1000);
        
        if (timerEl) {
            timerEl.textContent = `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        }

        if (h >= 24 && labelAtraso) {
            labelAtraso.style.display = 'block';
        }
    });
}

// --- 3. MODALES (DETALLES Y VISOR) ---
function abrirDetalles(id) {
    const template = document.getElementById(`template-${id}`);
    const modalTarget = document.getElementById('modal-inject-content');
    const modal = document.getElementById('modalDetails');

    if (template && modalTarget) {
        modalTarget.innerHTML = template.innerHTML;
        modal.style.display = 'flex';
        modal.classList.add('active'); // Marcador de estado
        document.body.style.overflow = 'hidden';
    }
}

function cerrarDetalles() {
    const modal = document.getElementById('modalDetails');
    modal.style.display = 'none';
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function verArchivo(url) {
    const viewer = document.getElementById('modalViewer');
    const frame = document.getElementById('fileFrame');
    if (frame && viewer) {
        frame.src = url;
        viewer.style.display = 'flex';
        viewer.classList.add('active');
    }
}

function cerrarVisor() {
    const viewer = document.getElementById('modalViewer');
    const frame = document.getElementById('fileFrame');
    if (viewer && frame) {
        viewer.style.display = 'none';
        viewer.classList.remove('active');
        frame.src = '';
    }
}

function cerrarModalClickFuera(event, modalId) {
    if (event.target.id === modalId) {
        if (modalId === 'modalViewer') cerrarVisor();
        else cerrarDetalles();
    }
}

// --- 4. COMUNICACIÓN SERVIDOR (AJAX / POLLING) ---
function fetchNewData() {
    // Verificamos si hay algún modal activo usando clases para mayor seguridad
    const detailModal = document.getElementById('modalDetails');
    const viewerModal = document.getElementById('modalViewer');
    
    const isModalOpen = (detailModal && detailModal.classList.contains('active')) || 
                        (viewerModal && viewerModal.classList.contains('active'));

    // Solo cancelamos la actualización si el modal de detalles está abierto
    // para evitar que el contenido que el admin está leyendo cambie o desaparezca.
    if (isModalOpen) return;

    // Obtener sucursal del botón activo
    const activeBtn = document.querySelector('.filter-btn.active');
    const sucursal = activeBtn ? activeBtn.getAttribute('data-sucursal') : 'Todas';

    fetch(`/admin?sucursal=${encodeURIComponent(sucursal)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.text();
    })
    .then(html => {
        const container = document.getElementById('peticiones-content');
        if (container && html.trim() !== "") {
            container.innerHTML = html;
            updateAllTimers();
        }
    })
    .catch(error => console.warn("Error de sincronización:", error));
}

function cambiarEstado(id, nuevoEstado) {
    if (nuevoEstado === 'Enviado') {
        if (!confirm("¿Deseas marcar como enviado? Se descontará el inventario.")) return;
    }

    fetch(`/admin/cambiar_estado/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado: nuevoEstado })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            fetchNewData(); 
        } else {
            alert("Error: " + data.error);
        }
    });
}

// --- 5. INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    applyTheme(localStorage.getItem('villar_theme') || 'light');

    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-btn')) {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            fetchNewData(); 
        }
    });

    updateAllTimers();
    setInterval(updateAllTimers, 1000);
    // Reducimos el polling a 3 segundos para mayor sensación de "tiempo real"
    setInterval(fetchNewData, 3000); 
});