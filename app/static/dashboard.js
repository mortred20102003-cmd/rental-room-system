async function loadOverview() {
  try {
    const res = await fetch('/system/overview');
    const data = await res.json();

    const setChip = (id, ok, label) => {
      const el = document.getElementById(id);
      el.textContent = `${label} ${ok ? 'online' : 'offline'}`;
      el.classList.toggle('offline', !ok);
    };
    setChip('chip-pg', data.services.postgresql, 'PostgreSQL');
    setChip('chip-mongo', data.services.mongodb, 'MongoDB');

    document.getElementById('env-badge').textContent = data.environment;

    const m = data.metrics;
    document.getElementById('m-properties').textContent = m.total_properties;
    document.getElementById('m-rooms').textContent = m.total_rooms;
    document.getElementById('m-occupied').textContent = m.occupied_rooms;
    document.getElementById('m-vacant').textContent = m.vacant_rooms;
    document.getElementById('m-tenants').textContent = m.total_tenants;
    document.getElementById('m-leases').textContent = m.active_leases;
    document.getElementById('m-pending').textContent = m.pending_payments;
    document.getElementById('m-maint').textContent = m.open_maintenance;
    document.getElementById('m-users').textContent = m.users;

    // scale bars to the largest metric so the visual pulse is proportional
    const max = Math.max(
      m.total_properties, m.total_rooms, m.occupied_rooms, m.total_tenants,
      m.active_leases, m.pending_payments, m.open_maintenance, m.users, 1,
    );
    const bar = (id, v) => document.getElementById(id).style.width = `${(v / max) * 100}%`;
    bar('b-properties', m.total_properties);
    bar('b-rooms', m.total_rooms);
    bar('b-occupied', m.occupied_rooms);
    bar('b-tenants', m.total_tenants);
    bar('b-leases', m.active_leases);
    bar('b-pending', m.pending_payments);
    bar('b-maint', m.open_maintenance);
    bar('b-users', m.users);
  } catch (e) {
    console.error('overview failed', e);
  }
}

loadOverview();
setInterval(loadOverview, 15000);