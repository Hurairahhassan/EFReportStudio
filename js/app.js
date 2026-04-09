// ═══════════════════════════════════════════════════
// EF Report Studio — Core Application Logic
// ═══════════════════════════════════════════════════

class App {
  constructor() {
    this.init();
  }

  init() {
    this.createToastContainer();
  }

  // ── Toast System ─────────────────────────────────
  createToastContainer() {
    if (document.getElementById('toast-container')) return;
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' };
    toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i> ${message}`;
    container.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // ── Formatting & Calculations ────────────────────
  formatCurrency(value) {
    if (isNaN(value) || value === null || value === undefined) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  }

  parseCurrency(value) {
    if (!value) return 0;
    return Number(String(value).replace(/[^0-9.\-]+/g, '')) || 0;
  }

  calculateAge(dobString) {
    if (!dobString) return '';
    const today = new Date();
    const birthDate = new Date(dobString);
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  }

  // ── Confirm Modal ────────────────────────────────
  showConfirm(title, message) {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.innerHTML = `
        <div class="modal-box">
          <h3>${title}</h3>
          <p>${message}</p>
          <div class="modal-actions">
            <button class="btn btn-secondary" id="modal-cancel">Cancel</button>
            <button class="btn btn-danger" id="modal-confirm">Confirm</button>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      overlay.querySelector('#modal-cancel').addEventListener('click', () => {
        overlay.remove();
        resolve(false);
      });
      overlay.querySelector('#modal-confirm').addEventListener('click', () => {
        overlay.remove();
        resolve(true);
      });
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          overlay.remove();
          resolve(false);
        }
      });
    });
  }
}

// ═══════════════════════════════════════════════════
// Data Manager — REST API Client (replaces localStorage)
// ═══════════════════════════════════════════════════

class DataManager {
  constructor() {
    this.API_BASE = '/api';
  }

  // ── Helper — JSON fetch with error handling ──
  async _fetch(url, options = {}) {
    try {
      const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      console.error(`API Error [${url}]:`, err);
      throw err;
    }
  }

  // ── Clients ──────────────────────────────────────
  async getClients() {
    return this._fetch(`${this.API_BASE}/clients`);
  }

  async getClient(id) {
    return this._fetch(`${this.API_BASE}/clients/${id}`);
  }

  async saveClient(clientData) {
    if (clientData.id) {
      // Update existing
      return this._fetch(`${this.API_BASE}/clients/${clientData.id}`, {
        method: 'PUT',
        body: JSON.stringify(clientData),
      });
    } else {
      // Create new
      return this._fetch(`${this.API_BASE}/clients`, {
        method: 'POST',
        body: JSON.stringify(clientData),
      });
    }
  }

  async deleteClient(id) {
    return this._fetch(`${this.API_BASE}/clients/${id}`, {
      method: 'DELETE',
    });
  }

  // ── Reports ──────────────────────────────────────
  async getReportHistory(clientId) {
    return this._fetch(`${this.API_BASE}/clients/${clientId}/reports`);
  }

  async saveReport(clientId, reportData) {
    return this._fetch(`${this.API_BASE}/clients/${clientId}/reports`, {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  }

  async getLatestReport(clientId) {
    return this._fetch(`${this.API_BASE}/clients/${clientId}/reports/latest`);
  }

  // ── Dashboard Stats ──────────────────────────────
  async getStats() {
    return this._fetch(`${this.API_BASE}/stats`);
  }

  // ── Current Report Data (session-only, for page transitions) ──
  setCurrentReport(data) {
    sessionStorage.setItem('currentReport', JSON.stringify(data));
  }

  getCurrentReport() {
    return JSON.parse(sessionStorage.getItem('currentReport') || 'null');
  }

  clearCurrentReport() {
    sessionStorage.removeItem('currentReport');
  }
}

const app = new App();
const dataManager = new DataManager();