(() => {
  const body = document.getElementById('members-body');
  const search = document.getElementById('search-input');
  const filterButton = document.getElementById('filter-button');
  const filterRow = document.getElementById('filter-row');
  const showingCount = document.getElementById('showing-count');
  const availableCount = document.getElementById('available-count');
  const busyCount = document.getElementById('busy-count');
  const caption = document.getElementById('availability-caption');
  const syncStatus = document.querySelector('.sync-status');
  const syncText = document.getElementById('sync-text');
  const toast = document.getElementById('toast');
  let activeFilter = 'all';
  let toastTimer;

  function showToast(message, isError = false) {
    toast.textContent = message;
    toast.classList.toggle('error', isError);
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
  }

  function setSync(state, message) {
    syncStatus.classList.remove('saving', 'error');
    if (state !== 'saved') syncStatus.classList.add(state);
    syncText.textContent = message;
  }

  function updateSummary() {
    const rows = [...body.querySelectorAll('tr')];
    const total = rows.length;
    const available = rows.filter(row => row.dataset.status === 'available').length;
    const busy = total - available;
    availableCount.innerHTML = `${available}<span class="stat-out-of"> / ${total}</span>`;
    busyCount.textContent = busy;
    caption.textContent = `${total ? Math.round(available / total * 100) : 0}% of your team is available`;
  }

  function applyFilters() {
    const query = search.value.trim().toLowerCase();
    const rows = [...body.querySelectorAll('tr')];
    let shown = 0;
    rows.forEach(row => {
      const matchesName = row.dataset.name.includes(query);
      const matchesFilter = activeFilter === 'all' || row.dataset.status === activeFilter;
      row.hidden = !(matchesName && matchesFilter);
      if (!row.hidden) shown++;
    });
    showingCount.innerHTML = `Showing <strong>${shown}</strong> of ${rows.length} team members`;
  }

  async function saveAvailability(input) {
    const row = input.closest('tr');
    const memberId = input.dataset.memberId;
    const requestedState = input.checked;
    input.disabled = true;
    setSync('saving', 'Saving change…');
    try {
      const response = await fetch(`/api/members/${memberId}/availability`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_available: requestedState })
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'Could not save this change.');
      const member = result.member;
      row.dataset.status = member.is_available ? 'available' : 'busy';
      const pill = row.querySelector('[data-status-pill]');
      pill.className = `status-pill ${member.is_available ? 'available' : 'busy'}`;
      pill.querySelector('span').textContent = member.is_available ? 'Available' : 'Busy';
      row.querySelector('[data-updated]').textContent = 'Just now';
      updateSummary();
      applyFilters();
      setSync('saved', 'All changes synced');
      showToast(`${member.name} is now ${member.is_available ? 'available' : 'busy'}.`);
    } catch (error) {
      input.checked = !requestedState;
      setSync('error', 'Could not sync — try again');
      showToast(error.message || 'Network error. Please try again.', true);
    } finally {
      input.disabled = false;
    }
  }

  body.addEventListener('change', event => {
    if (event.target.matches('.availability-toggle')) saveAvailability(event.target);
  });
  search.addEventListener('input', applyFilters);
  filterButton.addEventListener('click', () => { filterRow.hidden = !filterRow.hidden; });
  filterRow.addEventListener('click', event => {
    const button = event.target.closest('[data-filter]');
    if (!button) return;
    activeFilter = button.dataset.filter;
    filterRow.querySelectorAll('.filter-chip').forEach(chip => chip.classList.toggle('selected', chip === button));
    applyFilters();
  });
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault(); search.focus();
    }
    if (event.key === 'Escape') { search.value = ''; applyFilters(); search.blur(); }
  });
  updateSummary();
  applyFilters();
})();
