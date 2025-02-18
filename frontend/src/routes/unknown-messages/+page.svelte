<script>
  import { onMount } from 'svelte';

  // Dummy user profile – replace with your real data as needed.
  let userProfile = {
    fullName: "John Doe",
    role: "Admin",
    appVersion: "1.0.0"
  };

  // Navbar state
  let showUserMenu = false;
  let darkMode = false;

  // Filter state – plain text fields for host and sources; date range for start/end dates.
  let hostFilter = "";
  let sourcesFilter = "";
  let startDate = "";
  let endDate = "";
  let filterWindows = false;
  let filterLinux = false;

  // Data arrays for raw unknown messages and the grouped cards.
  let unknownMessages = [];
  let groupedMessages = [];

  // Global toggles for all cards (for hosts and apps lists)
  let showAllHosts = false;
  let showAllApps = false;

  // Load unknown messages from the backend using current filters.
  async function loadUnknownMessages() {
    const params = new URLSearchParams({
      host: hostFilter,
      sources: sourcesFilter,
      startDate: startDate,
      endDate: endDate,
      filter_windows: filterWindows,
      filter_linux: filterLinux
    });
    // Adjust the URL to match your backend endpoint.
    const res = await fetch(`/unknown-messages?${params.toString()}`);
    const data = await res.json();
    unknownMessages = data.unknown_messages;
    groupMessages();
  }

  // Group messages by error (message text) and compute unique hosts and apps.
  function groupMessages() {
    const groups = {};
    unknownMessages.forEach(msg => {
      const error = msg.message;
      if (!groups[error]) {
        groups[error] = {
          error,
          hosts: new Set(),
          apps: new Set(),
          totalCount: 0,
          expanded: true,
          showHosts: false,
          showApps: false
        };
      }
      groups[error].hosts.add(msg.host);
      groups[error].apps.add(msg.source);
      groups[error].totalCount++;
    });
    groupedMessages = Object.values(groups).map(group => ({
      error: group.error,
      hosts: Array.from(group.hosts),
      apps: Array.from(group.apps),
      totalCount: group.totalCount,
      expanded: group.expanded,
      showHosts: group.showHosts,
      showApps: group.showApps
    }));
  }

  // Update filters and reload messages.
  function updateFilters() {
    loadUnknownMessages();
  }

  // Global toggle functions.
  function collapseAllCards() {
    groupedMessages = groupedMessages.map(card => {
      card.expanded = false;
      card.showHosts = false;
      card.showApps = false;
      return card;
    });
  }

  function expandAllCards() {
    groupedMessages = groupedMessages.map(card => {
      card.expanded = true;
      return card;
    });
  }

  function toggleAllHosts() {
    showAllHosts = !showAllHosts;
    groupedMessages = groupedMessages.map(card => {
      card.showHosts = showAllHosts;
      return card;
    });
  }

  function toggleAllApps() {
    showAllApps = !showAllApps;
    groupedMessages = groupedMessages.map(card => {
      card.showApps = showAllApps;
      return card;
    });
  }

  // Individual card toggle functions.
  function toggleCard(card) {
    card.expanded = !card.expanded;
    groupedMessages = [...groupedMessages];
  }
  function toggleHosts(card) {
    card.showHosts = !card.showHosts;
    groupedMessages = [...groupedMessages];
  }
  function toggleApps(card) {
    card.showApps = !card.showApps;
    groupedMessages = [...groupedMessages];
  }

  // Dark mode toggle.
  function toggleDarkMode() {
    darkMode = !darkMode;
    if (darkMode) {
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
    }
  }

  // Dummy logout function.
  function logout() {
    window.location.href = '/logout';
  }

  // Dummy undo/redo functions.
  function undoAction() { /* ... */ }
  function redoAction() { /* ... */ }

  onMount(() => {
    loadUnknownMessages();
  });
</script>

<svelte:head>
  <title>Unknown Messages</title>
  <!-- Bootstrap CSS & Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/css/bootstrap.min.css" crossorigin="anonymous" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" crossorigin="anonymous" />
  <style>
    /* Base styling (matching the incidents page) */
    body {
      background-color: #f0f2f5;
      color: #333;
    }
    body.dark-mode {
      background-color: #333;
      color: #eee;
    }
    body.dark-mode .form-control {
      background-color: #555;
      border-color: #777;
      color: #eee;
    }
    body.dark-mode .dropdown-menu {
      background-color: #444;
      border-color: #666;
      color: #eee;
    }
    .container-custom {
      max-width: 1500px;
      margin: 0 auto;
    }
    /* Card-style layout for unknown messages (inspired by main alerts) */
    .unknown-card {
      background-color: #e9f7fe;
      border: 1px solid #007bff;
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .unknown-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
    }
    .unknown-card-body {
      margin-top: 0.5rem;
    }
    .unknown-card-body ul {
      list-style-type: none;
      padding-left: 0;
    }
    .unknown-card-body li {
      padding: 0.25rem 0;
      border-bottom: 1px solid #ddd;
    }
    .toggle-buttons {
      margin-bottom: 1rem;
    }
    .count {
      font-weight: bold;
      cursor: pointer;
    }
    /* Filter form styling */
    .filter-form {
      margin-bottom: 2rem;
    }
  </style>
</svelte:head>

<!-- Navbar
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <a class="navbar-brand" href="/" on:click|preventDefault>Infra Incident Management</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarContent"
          aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarContent"> -->
    <!-- Left navigation links 
    <ul class="navbar-nav mr-auto">
      <li class="nav-item">
        <a class="nav-link" href="/">Incidents</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/unknown-messages" on:click|preventDefault>Unknown Messages</a>
      </li>
    </ul> -->
    <!-- Right-side controls 
    <div class="ml-auto d-flex align-items-center">
      <button on:click={undoAction} class="btn btn-secondary mr-2" aria-label="Undo">
        <i class="bi bi-arrow-counterclockwise"></i>
      </button>
      <button on:click={redoAction} class="btn btn-secondary mr-2" aria-label="Redo">
        <i class="bi bi-arrow-clockwise"></i>
      </button>
      <button class="btn btn-secondary mr-2" on:click={toggleDarkMode} aria-label="Toggle Dark Mode">
        {#if darkMode}
          <i class="bi bi-sun-fill"></i>
        {:else}
          <i class="bi bi-sun"></i>
        {/if}
      </button>
      <div class="dropdown ml-2">
        <button class="btn btn-secondary dropdown-toggle" type="button" on:click={() => showUserMenu = !showUserMenu} aria-label="User Menu">
          {userProfile.fullName}
        </button>
        {#if showUserMenu}
          <div class="dropdown-menu dropdown-menu-right">
            <h6 class="dropdown-header">Profile Info</h6>
            <span class="dropdown-item-text">Full Name: {userProfile.fullName}</span>
            <span class="dropdown-item-text">Role: {userProfile.role}</span>
            <span class="dropdown-item-text">App Version: {userProfile.appVersion}</span>
            {#if userProfile.role === "Admin"}
              <a class="dropdown-item" href="/">Admin URL</a>
            {/if}
            <div class="dropdown-divider"></div>
            <button class="dropdown-item" on:click={logout}>Logout</button>
          </div>
        {/if}
      </div>
    </div>
  </div>
</nav>-->

<div class="container container-custom">
  <!-- Filter Controls -->
  <form on:submit|preventDefault={updateFilters} class="filter-form">
    <div class="form-row">
      <div class="form-group col-md-3">
        <label for="hostFilter">Host:</label>
        <input type="text" class="form-control" id="hostFilter" bind:value={hostFilter} placeholder="Enter host">
      </div>
      <div class="form-group col-md-3">
        <label for="sourcesFilter">Sources (comma separated):</label>
        <input type="text" class="form-control" id="sourcesFilter" bind:value={sourcesFilter} placeholder="e.g., app1, app2">
      </div>
      <div class="form-group col-md-3">
        <label for="startDate">Start Date:</label>
        <input type="date" class="form-control" id="startDate" bind:value={startDate}>
      </div>
      <div class="form-group col-md-3">
        <label for="endDate">End Date:</label>
        <input type="date" class="form-control" id="endDate" bind:value={endDate}>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group col-md-6">
        <label>Hide messages from:</label>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="checkbox" id="filterWindows" bind:checked={filterWindows}>
          <label class="form-check-label" for="filterWindows">Windows</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="checkbox" id="filterLinux" bind:checked={filterLinux}>
          <label class="form-check-label" for="filterLinux">Linux</label>
        </div>
      </div>
      <div class="form-group col-md-6 d-flex align-items-end">
        <button type="submit" class="btn btn-primary">Update</button>
      </div>
    </div>
  </form>
  
  <!-- Global Toggle Buttons -->
  <div class="toggle-buttons mb-3">
    <button class="btn btn-primary mr-2" on:click={collapseAllCards}>Collapse All Cards</button>
    <button class="btn btn-primary mr-2" on:click={expandAllCards}>Expand All Cards</button>
    <button class="btn btn-info mr-2" on:click={toggleAllHosts}>
      {showAllHosts ? 'Hide All Hosts' : 'Show All Hosts'}
    </button>
    <button class="btn btn-info" on:click={toggleAllApps}>
      {showAllApps ? 'Hide All Apps' : 'Show All Apps'}
    </button>
  </div>
  
  <!-- Unknown Messages Cards -->
  {#if groupedMessages.length > 0}
    {#each groupedMessages as card (card.error)}
      <div class="unknown-card">
        <div class="unknown-card-header" on:click={() => toggleCard(card)}>
          <div>
            <h5 class="mb-0">{card.error}</h5>
            <small>{card.totalCount} messages</small>
          </div>
          <div>
            <span class="mr-3 count" on:click|stopPropagation={() => toggleHosts(card)}>
              Hosts: {card.hosts.length}
            </span>
            <span class="count" on:click|stopPropagation={() => toggleApps(card)}>
              Apps: {card.apps.length}
            </span>
          </div>
        </div>
        {#if card.expanded}
          <div class="unknown-card-body">
            {#if card.showHosts}
              <div>
                <strong>Hosts:</strong>
                <ul>
                  {#each card.hosts as host}
                    <li>{host}</li>
                  {/each}
                </ul>
              </div>
            {/if}
            {#if card.showApps}
              <div>
                <strong>Apps:</strong>
                <ul>
                  {#each card.apps as app}
                    <li>{app}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {/each}
  {:else}
    <p>No unknown messages found.</p>
  {/if}
</div>
