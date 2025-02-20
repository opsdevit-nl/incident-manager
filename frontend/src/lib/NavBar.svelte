<script>
  import { createEventDispatcher, onMount } from 'svelte';
  const dispatch = createEventDispatcher();

  // Modal flag for the full filters modal.
  let showFiltersModal = false;

  // Reference for the date range picker button.
  let dateRangeButton;

  export const userProfile = { fullName: "John Doe", role: "Admin", appVersion: "1.0.0" };
  export let darkMode = false;
  export let undoAction = () => {};
  export let redoAction = () => {};
  export let toggleDarkMode = () => {};
  export let logout = () => {};

  // These props come from the store via the layout.
  export let statusFilter;
  export let teamFilter;
  export let assigneeFilter;
  export let severityFilter;
  export let sortBy;
  export let sortOrder;
  export let firstAlertStart;
  export let firstAlertEnd;
  export let lastAlertStart;
  export let lastAlertEnd;

  // When a select changes, dispatch a custom event with the new value.
  function handleStatusChange(e) {
    dispatch('statusFilterChange', e.target.value);
  }
  function handleTeamChange(e) {
    dispatch('teamFilterChange', e.target.value);
  }
  function handleAssigneeChange(e) {
    dispatch('assigneeFilterChange', e.target.value);
  }
  function handleSeverityChange(e) {
    dispatch('severityFilterChange', e.target.value);
  }
  function handleSortByChange(e) {
    dispatch('sortByChange', e.target.value);
  }
  function handleSortOrderChange(e) {
    dispatch('sortOrderChange', e.target.value);
  }
  // (Optional) A generic date filter handler if needed elsewhere.
  function handleDateFilterChange(filterKey, e) {
    const value = e.target.value;
    console.log(`NavBar: Date filter changed: ${filterKey} = ${value}`);
    dispatch('dateFilterChange', { filterKey, value });
  }

  // Helper functions to format the date range for display.
  function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
  }
  function formatDateRange(start, end) {
    const s = formatDate(start);
    const e = formatDate(end);
    return s && e ? `${s} – ${e}` : 'Select Date Range';
  }

  // Initialize the Bootstrap Date Range Picker on the button.
  onMount(() => {
    // Initialize the daterangepicker using globalThis.$ (jQuery)
    globalThis.$(dateRangeButton).daterangepicker({
      timePicker: true,
      timePicker24Hour: false, // adjust as needed
      autoUpdateInput: false,  // we'll update our props manually
      locale: {
        format: 'YYYY-MM-DDTHH:mm',
        cancelLabel: 'Clear'
      },
      // Add a preset for "Today"
      ranges: {
        'Today': [moment(), moment()]
      }
    }, function(start, end, label) {
      // This callback is triggered on "apply"
      firstAlertStart = start.format('YYYY-MM-DDTHH:mm');
      firstAlertEnd = end.format('YYYY-MM-DDTHH:mm');
      dispatch('dateFilterChange', { filterKey: 'firstAlertStart', value: firstAlertStart });
      dispatch('dateFilterChange', { filterKey: 'firstAlertEnd', value: firstAlertEnd });
    });

    // Listen for the cancel (clear) event
    globalThis.$(dateRangeButton).on('cancel.daterangepicker', function(ev, picker) {
      firstAlertStart = '';
      firstAlertEnd = '';
      dispatch('dateFilterChange', { filterKey: 'firstAlertStart', value: '' });
      dispatch('dateFilterChange', { filterKey: 'firstAlertEnd', value: '' });
    });
  });
</script>

<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid">
    <!-- Main Navbar Content -->
    <div class="d-flex w-100 justify-content-between align-items-center">
      <div class="d-flex align-items-center">
        <a class="navbar-brand" href="/">Infra Incident Management</a>
        <button class="navbar-toggler ml-2" type="button" data-toggle="collapse" data-target="#navbarContent"
                aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
      </div>
      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item"><a class="nav-link" href="/">Incidents</a></li>
          <li class="nav-item"><a class="nav-link" href="/unknown-messages/">Unknown Messages</a></li>
        </ul>
      </div>
      <div class="d-flex align-items-center">
        <!-- Quick-access filters -->
        <select id="statusFilter" class="form-control form-control-sm mr-2" style="width: 7em;"
                bind:value={statusFilter} on:change={handleStatusChange}>
          <option value="all">--All--</option>
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
        </select>
        <select id="teamFilter" class="form-control form-control-sm mr-2" style="width: 6em;"
                bind:value={teamFilter} on:change={handleTeamChange}>
          <option value="">--Team--</option>
          <option value="team1">team1</option>
          <option value="team2">team2</option>
          <option value="team3">team3</option>
        </select>

        <!-- Compact Date Range Picker Button (using Bootstrap Date Range Picker) -->
        <div class="position-relative mr-2">
          <button type="button" class="btn btn-secondary mr-2" bind:this={dateRangeButton}>
            <i class="bi bi-calendar-range"></i>
            {firstAlertStart && firstAlertEnd
              ? formatDateRange(firstAlertStart, firstAlertEnd)
              : ''}
          </button>
        </div>

        <!-- Updated filter settings button (icon only) -->
        <button class="btn btn-secondary mr-2" on:click={() => showFiltersModal = true}
                aria-label="Filter settings">
          <i class="bi bi-sliders2"></i>
        </button>
        <button on:click={() => { console.log("Undo button clicked"); undoAction(); }}
                class="btn btn-secondary mr-2" aria-label="Undo">
          <i class="bi bi-arrow-counterclockwise"></i>
        </button>
        <button on:click={() => { console.log("Redo button clicked"); redoAction(); }}
                class="btn btn-secondary mr-2" aria-label="Redo">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
        <button on:click={() => toggleDarkMode()}
                class="btn btn-secondary mr-2" aria-label="Dark Mode Toggle">
          {#if darkMode}
            <i class="bi bi-sun-fill"></i>
          {:else} 
            <i class="bi bi-sun"></i>
          {/if}
        </button>
        <button on:click={() => logout()} class="btn btn-secondary mr-2">Logout</button>
      </div>
    </div>
  </div>

  <!-- Overlay Modal for Filters & Sorting -->
  {#if showFiltersModal}
    <div class="filter-modal-overlay" aria-label="menu"  role="button" tabindex="0" on:click={() => showFiltersModal = false} on:keydown={(e) => { if(e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); } }}>
      <div class="filter-modal-content" class:dark={darkMode} aria-label="menu" role="button" tabindex="0"  on:click|stopPropagation on:keydown={(e) => { if(e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); } }}>
        <div class="d-flex justify-content-between align-items-center mb-2">
          <h5 class="mb-0">Filters &amp; Sorting</h5>
          <button class="btn btn-link" on:click={() => showFiltersModal = false}>Close</button>
        </div>
        <div class="form-group">
          <label for="statusFilter">Status:</label>
          <select id="statusFilter" class="form-control" bind:value={statusFilter} on:change={handleStatusChange}>
            <option value="open">Open</option>
            <option value="resolved">Resolved</option>
            <option value="all">--All--</option>
          </select>
        </div>
        <div class="form-group">
          <label for="teamFilter">Team:</label>
          <select id="teamFilter" class="form-control" bind:value={teamFilter} on:change={handleTeamChange}>
            <option value="">--Team--</option>
            <option value="team1">team1</option>
            <option value="team2">team2</option>
            <option value="team3">team3</option>
          </select>
        </div>
        <div class="form-group">
          <label for="assigneeFilter">Assignee:</label>
          <select id="assigneeFilter" class="form-control" bind:value={assigneeFilter} on:change={handleAssigneeChange}>
            <option value="">--Assignee--</option>
            <option value="person1">person1</option>
            <option value="person2">person2</option>
            <option value="person3">person3</option>
            <option value="person4">person4</option>
          </select>
        </div>
        <div class="form-group">
          <label for="severityFilter">Severity:</label>
          <select id="severityFilter" class="form-control" bind:value={severityFilter} on:change={handleSeverityChange}>
            <option value="">--Severity--</option>
            <option value="MAJOR">MAJOR</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
        <div class="form-group">
          <label for="sortBy">Sort By:</label>
          <select id="sortBy" class="form-control" bind:value={sortBy} on:change={handleSortByChange}>
            <option value="alert_count">Alerts Count</option>
            <option value="created">Created (Time)</option>
            <option value="last_alert">Last Alert Received</option>
            <option value="team">Team</option>
            <option value="severity">Severity</option>
          </select>
        </div>
        <div class="form-group">
          <label for="sortOrder">Sort Order:</label>
          <select id="sortOrder" class="form-control" bind:value={sortOrder} on:change={handleSortOrderChange}>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </div>
        <div class="form-group">
          <label for="first-alert-start">First Alert Start:</label>
          <input type="datetime-local" id="first-alert-start" class="form-control"
                 bind:value={firstAlertStart} on:change={e => handleDateFilterChange('firstAlertStart', e)} />
        </div>
        <div class="form-group">
          <label for="first-alert-end">First Alert End:</label>
          <input type="datetime-local" id="first-alert-end" class="form-control"
                 bind:value={firstAlertEnd} on:change={e => handleDateFilterChange('firstAlertEnd', e)} />
        </div>
        <div class="form-group">
          <label for="last-alert-start">Last Alert Start:</label>
          <input type="datetime-local" id="last-alert-start" class="form-control"
                 bind:value={lastAlertStart} on:change={e => handleDateFilterChange('lastAlertStart', e)} />
        </div>
        <div class="form-group">
          <label for="last-alert-end">Last Alert End:</label>
          <input type="datetime-local" id="last-alert-end" class="form-control"
                 bind:value={lastAlertEnd} on:change={e => handleDateFilterChange('lastAlertEnd', e)} />
        </div>
      </div>
    </div>
  {/if}

  <style>
    .filter-modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1050;
    }
    .filter-modal-content {
      background: #fff;
      padding: 1rem;
      border-radius: 4px;
      width: 90%;
      max-width: 500px;
    }
    /* Dark mode styles */
    .filter-modal-content.dark {
      background: #343a40;
      color: #fff;
    }
    .filter-modal-content.dark .form-control {
      background-color: #495057;
      border-color: #6c757d;
    }
    .filter-modal-content.dark label {
      color: #fff;
    }
  </style>
</nav>
