async function loadOverview() {
  const chipEls = {
    postgresql: document.getElementById('chip-pg'),
    mongodb: document.getElementById('chip-mongo'),
  };

  Object.values(chipEls).forEach((chip) => {
    if (chip) chip.classList.add('fetching');
  });

  try {
    const res = await fetch('/system/overview');
    const data = await res.json();

    const setChip = (key, label) => {
      const el = chipEls[key];
      if (!el) return;
      const ok = Boolean(data?.services?.[key]);
      el.textContent = `${label} ${ok ? 'online' : 'offline'}`;
      el.classList.toggle('offline', !ok);
      el.classList.remove('fetching');
    };

    setChip('postgresql', 'PostgreSQL');
    setChip('mongodb', 'MongoDB');

    const envBadge = document.getElementById('env-badge');
    if (envBadge) envBadge.textContent = data.environment || 'DEVELOPMENT';

    const m = data.metrics || {};
    const metrics = [
      ['m-properties', 'total_properties', 'b-properties'],
      ['m-rooms', 'total_rooms', 'b-rooms'],
      ['m-occupied', 'occupied_rooms', 'b-occupied'],
      ['m-vacant', 'vacant_rooms', null],
      ['m-tenants', 'total_tenants', 'b-tenants'],
      ['m-leases', 'active_leases', 'b-leases'],
      ['m-pending', 'pending_payments', 'b-pending'],
      ['m-maint', 'open_maintenance', 'b-maint'],
      ['m-users', 'users', 'b-users'],
    ];

    metrics.forEach(([valueId, metricKey, barId]) => {
      const el = document.getElementById(valueId);
      if (!el) return;
      const val = Number(m[metricKey] ?? 0);
      el.textContent = Number.isFinite(val) ? val : '—';
      if (barId) {
        const bar = document.getElementById(barId);
        if (bar) bar.style.width = '0%';
      }
    });

    const max = Math.max(
      Number(m.total_properties || 0),
      Number(m.total_rooms || 0),
      Number(m.occupied_rooms || 0),
      Number(m.total_tenants || 0),
      Number(m.active_leases || 0),
      Number(m.pending_payments || 0),
      Number(m.open_maintenance || 0),
      Number(m.users || 0),
      1,
    );

    const fillBar = (barId, valueKey) => {
      const bar = document.getElementById(barId);
      if (!bar) return;
      const value = Number(m[valueKey] ?? 0);
      bar.style.width = `${Math.min((value / max) * 100, 100)}%`;
    };

    fillBar('b-properties', 'total_properties');
    fillBar('b-rooms', 'total_rooms');
    fillBar('b-occupied', 'occupied_rooms');
    fillBar('b-tenants', 'total_tenants');
    fillBar('b-leases', 'active_leases');
    fillBar('b-pending', 'pending_payments');
    fillBar('b-maint', 'open_maintenance');
    fillBar('b-users', 'users');
  } catch (error) {
    console.error('overview failed', error);
    Object.values(chipEls).forEach((chip) => {
      if (!chip) return;
      chip.textContent = chip.id === 'chip-pg' ? 'PostgreSQL offline' : 'MongoDB offline';
      chip.classList.add('offline');
      chip.classList.remove('fetching');
    });

    ['m-properties', 'm-rooms', 'm-occupied', 'm-vacant', 'm-tenants', 'm-leases', 'm-pending', 'm-maint', 'm-users']
      .forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.textContent = '—';
      });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadOverview();
  window.setInterval(loadOverview, 15000);
});
