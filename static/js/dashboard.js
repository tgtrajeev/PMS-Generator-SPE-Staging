/* ===================================================================
   PMS Generator - Dashboard
   =================================================================== */

const Dashboard = {
    specs: [],
    filteredSpecs: [],
    deleteTarget: null,

    async init() {
        await this.loadSpecs();
    },

    // -- Toast Notifications -------------------------------------------
    showToast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    // -- Load Specs ---------------------------------------------------
    async loadSpecs() {
        try {
            const res = await fetch('/api/specs');
            this.specs = await res.json();
            this.filteredSpecs = [...this.specs];
            this.renderTable();
            this.renderStats();
        } catch (e) {
            console.error('Failed to load specs:', e);
            this.showToast('Failed to load saved specifications.', 'error');
        }
    },

    // -- Render Table -------------------------------------------------
    renderTable() {
        const tbody = document.getElementById('specs-tbody');
        const emptyState = document.getElementById('empty-state');
        const tableContainer = document.getElementById('specs-table-container');

        if (this.filteredSpecs.length === 0) {
            tableContainer.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        tableContainer.style.display = 'block';
        emptyState.style.display = 'none';

        tbody.innerHTML = this.filteredSpecs.map(spec => {
            const createdDate = spec.created_at ? new Date(spec.created_at).toLocaleDateString() : 'N/A';

            // Prefer dedicated DB columns; fall back to nested pms_data JSON
            const data   = spec.pms_data || {};
            const msr    = data.msr || {};
            const sc     = data.spec_code || {};

            const specCode     = spec.spec_code || sc.spec_code || 'N/A';
            const matGrade     = spec.material_grade || msr.material_grade || 'N/A';
            const matType      = spec.material_type  || msr.material_type  || '';
            const ca           = spec.corrosion_allowance != null ? spec.corrosion_allowance + ' mm' : 'N/A';
            const flangeClass  = spec.flange_class ? spec.flange_class + '#' : 'N/A';
            const service      = spec.service || data.service?.service_description || 'N/A';
            const pressure     = spec.design_pressure_barg != null ? spec.design_pressure_barg + ' barg' : 'N/A';
            const temp         = spec.design_temp_c != null ? spec.design_temp_c + ' °C' : 'N/A';

            // Badges for NACE / Low Temp
            const badges = [
                spec.is_nace     ? `<span style="background:#c0392b;color:#fff;font-size:0.7rem;padding:1px 5px;border-radius:3px;margin-left:4px">NACE</span>` : '',
                spec.is_low_temp ? `<span style="background:#2980b9;color:#fff;font-size:0.7rem;padding:1px 5px;border-radius:3px;margin-left:4px">LT</span>` : '',
            ].join('');

            // Download button — grey out if file no longer on disk
            const dlBtn = spec.excel_filename
                ? spec.file_exists
                    ? `<button class="btn btn-sm btn-success" onclick="Dashboard.downloadSpec('${spec.excel_filename}')" title="Download Excel">⬇ Download</button>`
                    : `<button class="btn btn-sm btn-secondary" disabled title="Excel file no longer on disk">File Missing</button>`
                : '';

            return `
                <tr>
                    <td>
                        <strong>${spec.project_name || 'Unnamed'}</strong>
                        <div style="font-size:0.8rem;color:var(--text-light)">${spec.doc_number || ''} Rev.${spec.revision || '0'}</div>
                    </td>
                    <td>
                        <span style="font-weight:600;color:var(--primary);font-family:monospace">${specCode}</span>
                        ${badges}
                    </td>
                    <td>
                        ${matGrade}
                        <div style="font-size:0.8rem;color:var(--text-light)">${matType}</div>
                    </td>
                    <td>${flangeClass}</td>
                    <td>${ca}</td>
                    <td style="max-width:160px;font-size:0.85rem">${service}</td>
                    <td>${pressure}<div style="font-size:0.8rem;color:var(--text-light)">${temp}</div></td>
                    <td>${createdDate}</td>
                    <td>
                        <div style="display:flex;gap:6px;flex-wrap:wrap;">
                            ${dlBtn}
                            <button class="btn btn-sm btn-secondary" onclick="Dashboard.showDeleteModal(${spec.id}, '${(spec.project_name || 'Unnamed').replace(/'/g, "\\'")}')" title="Delete">🗑 Delete</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },

    // -- Render Stats -------------------------------------------------
    renderStats() {
        const total = this.specs.length;
        let cs = 0, ss = 0, other = 0;

        this.specs.forEach(spec => {
            const matType = (spec.material_type || spec.pms_data?.msr?.material_type || '').toUpperCase();
            if (matType === 'CS' || matType === 'CS-LT') cs++;
            else if (matType === 'SS') ss++;
            else other++;
        });

        document.getElementById('stat-total').textContent = total;
        document.getElementById('stat-cs').textContent = cs;
        document.getElementById('stat-ss').textContent = ss;
        document.getElementById('stat-other').textContent = other;
    },

    // -- Filter Specs -------------------------------------------------
    filterSpecs(query) {
        const q = query.toLowerCase().trim();
        if (!q) {
            this.filteredSpecs = [...this.specs];
        } else {
            this.filteredSpecs = this.specs.filter(spec => {
                const searchStr = [
                    spec.project_name,
                    spec.spec_code,
                    spec.doc_number,
                    spec.material_grade,
                    spec.material_type,
                    spec.service,
                    spec.flange_class,
                ].filter(Boolean).join(' ').toLowerCase();
                return searchStr.includes(q);
            });
        }
        this.renderTable();
    },

    // -- Download Spec ------------------------------------------------
    downloadSpec(filename) {
        window.location.href = `/api/download/${filename}`;
        this.showToast('Download started!', 'success');
    },

    // -- Delete Spec --------------------------------------------------
    showDeleteModal(id, name) {
        this.deleteTarget = id;
        document.getElementById('delete-modal-text').textContent = `Are you sure you want to delete "${name}"? This action cannot be undone.`;
        document.getElementById('delete-modal').style.display = 'flex';
    },

    closeDeleteModal() {
        this.deleteTarget = null;
        document.getElementById('delete-modal').style.display = 'none';
    },

    async confirmDelete() {
        if (!this.deleteTarget) return;
        try {
            const res = await fetch(`/api/specs/${this.deleteTarget}`, { method: 'DELETE' });
            if (res.ok) {
                this.showToast('Specification deleted.', 'success');
                this.closeDeleteModal();
                await this.loadSpecs();
            } else {
                this.showToast('Failed to delete specification.', 'error');
            }
        } catch (e) {
            console.error(e);
            this.showToast('Error deleting specification.', 'error');
        }
    },
};

// Initialize
document.addEventListener('DOMContentLoaded', () => Dashboard.init());
