const admin = (() => {
  const state = {
    properties: [],
    rooms: [],
    tenants: [],
    leases: [],
    payments: [],
    maintenance: [],
  };

  const openModal = (id) => {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
  };

  const closeModal = (id) => {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
  };

  const setModalHandlers = () => {
    document.querySelectorAll('[data-close-modal]').forEach((button) => {
      button.addEventListener('click', () => closeModal(button.dataset.closeModal));
    });

    document.querySelectorAll('.close-button').forEach((button) => {
      button.addEventListener('click', () => {
        const modal = button.closest('.modal');
        if (modal) closeModal(modal.id);
      });
    });

    document.querySelectorAll('.js-open-modal').forEach((button) => {
      button.addEventListener('click', () => openModal(button.dataset.target));
    });

    document.querySelectorAll('.modal').forEach((modal) => {
      modal.addEventListener('click', (event) => {
        if (event.target === modal) closeModal(modal.id);
      });
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        document.querySelectorAll('.modal.open').forEach((modal) => closeModal(modal.id));
      }
    });
  };

  const loadCollection = async (path, key) => {
    try {
      const data = await api.get(path);
      state[key] = Array.isArray(data) ? data : [];
      return state[key];
    } catch (error) {
      console.error(`Failed to load ${key}`, error);
      return [];
    }
  };

  const initListPage = ({
    entity,
    apiPath,
    tableBodyId,
    modalId,
    formId,
    searchInputId = null,
    filterId = null,
    renderRow,
    formBuilder = () => ({}),
    mapper = (data) => data,
  }) => {
    const tbody = document.getElementById(tableBodyId);
    const form = document.getElementById(formId);
    const modal = document.getElementById(modalId);
    const searchInput = searchInputId ? document.getElementById(searchInputId) : null;
    const filterSelect = filterId ? document.getElementById(filterId) : null;

    const updateRows = (items) => {
      if (!tbody) return;
      tbody.innerHTML = items.length
        ? items.map((item) => renderRow(item)).join('')
        : `<tr><td colspan="100%" class="muted-cell">No records found.</td></tr>`;

      tbody.querySelectorAll('[data-edit]').forEach((button) => {
        button.addEventListener('click', async () => {
          const id = Number(button.dataset.edit);
          const item = items.find((entry) => Number(entry.id) === id);
          if (!item || !form) return;
          Object.entries(formBuilder(item)).forEach(([key, value]) => {
            const field = form.elements.namedItem(key);
            if (field) field.value = value;
          });
          form.dataset.editId = String(id);
          openModal(modalId);
        });
      });

      tbody.querySelectorAll('[data-delete]').forEach((button) => {
        button.addEventListener('click', async () => {
          const id = Number(button.dataset.delete);
          if (!confirm(`Delete this ${entity}?`)) return;
          try {
            await api.del(`${apiPath}/${id}`);
            await loadAll();
          } catch (error) {
            alert(error.message || 'Delete failed');
          }
        });
      });
    };

    const loadAll = async () => {
      const items = await loadCollection(apiPath, `${entity}s`);
      let filtered = [...items];

      if (searchInput) {
        const term = searchInput.value.trim().toLowerCase();
        if (term) {
          filtered = filtered.filter((item) => JSON.stringify(item).toLowerCase().includes(term));
        }
      }

      if (filterSelect && filterSelect.value !== 'all') {
        filtered = filtered.filter((item) => (item.status || '').toLowerCase() === filterSelect.value.toLowerCase());
      }

      updateRows(filtered);
    };

    if (searchInput) searchInput.addEventListener('input', loadAll);
    if (filterSelect) filterSelect.addEventListener('change', loadAll);

    if (form) {
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = Object.fromEntries(new FormData(form).entries());
        const payload = mapper(formData);
        const id = form.dataset.editId;

        try {
          if (id) {
            await api.put(`${apiPath}/${id}`, payload);
          } else {
            await api.post(apiPath, payload);
          }
          form.reset();
          delete form.dataset.editId;
          closeModal(modalId);
          await loadAll();
        } catch (error) {
          alert(error.message || 'Save failed');
        }
      });
    }

    if (modal) {
      const btn = document.querySelector(`[data-target="${modalId}"]`);
      if (btn) btn.addEventListener('click', () => {
        form && form.reset();
        delete form.dataset.editId;
        openModal(modalId);
      });
    }

    loadAll();
  };

  const initRoomGrid = async () => {
    const grid = document.getElementById('rooms-grid');
    if (!grid) return;

    const rooms = await loadCollection('/rooms', 'rooms');
    const properties = await loadCollection('/properties', 'properties');
    const propertyMap = Object.fromEntries(properties.map((prop) => [prop.id, prop.name]));

    grid.innerHTML = rooms.length
      ? rooms.map((room) => `
          <article class="room-card">
            <h3>Room ${room.room_number || room.id}</h3>
            <div class="room-meta">
              <span>${propertyMap[room.property_id] || 'Property'}</span>
              <span>${room.room_type || 'Studio'}</span>
              <span>${room.occupied ? 'Occupied' : 'Vacant'}</span>
            </div>
            <p><strong>Rent:</strong> $${Number(room.monthly_rent || 0).toFixed(2)}</p>
            <div class="room-actions">
              <button class="ghost-button" type="button">Edit</button>
              <button class="ghost-button danger" type="button">Delete</button>
            </div>
          </article>
        `).join('')
      : '<div class="muted-cell">No rooms found.</div>';
  };

  const initMaintenanceBoard = async () => {
    const tasks = await loadCollection('/maintenance', 'maintenance');
    const columns = {
      open: document.getElementById('tasks-open'),
      in_progress: document.getElementById('tasks-in_progress'),
      resolved: document.getElementById('tasks-resolved'),
    };

    Object.entries(columns).forEach(([status, el]) => {
      if (!el) return;
      const matches = tasks.filter((task) => (task.status || 'open') === status);
      el.innerHTML = matches.length
        ? matches.map((task) => `
            <article class="task-card">
              <h4>${task.title || 'Untitled ticket'}</h4>
              <p>${task.description || 'No details provided.'}</p>
              <div class="task-meta">
                <span class="badge ${task.priority === 'high' ? 'danger' : task.priority === 'medium' ? 'warning' : 'neutral'}">${task.priority || 'low'}</span>
              </div>
            </article>
          `).join('')
        : '<p class="muted-cell">No tasks.</p>';
    });

    document.querySelectorAll('.kanban-column').forEach((column) => {
      const badge = column.querySelector('.badge');
      if (badge) {
        const count = tasks.filter((task) => (task.status || 'open') === column.dataset.status).length;
        badge.textContent = String(count);
      }
    });
  };

  return {
    setModalHandlers,
    initListPage,
    initRoomGrid,
    initMaintenanceBoard,
  };
})();

window.addEventListener('DOMContentLoaded', () => {
  admin.setModalHandlers();
});
