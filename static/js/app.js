/* ===================================================================
   PMS Generator - Multi-Step Wizard Application (8-Step)
   =================================================================== */

const App = {
    currentStep: 1,
    totalSteps: 7,
    _materialIdCounter: 0,
    data: {
        metadata: {},
        msr: {},
        spec_code: {},
        line_list: {},
        thickness: {},
        schedule: {},
        fittings: {},
        flanges: {},
        valves: {},
        validation: [],
    },

    init() {
        this.loadPMSReference();
        this.bindEvents();
        this.showStep(1);
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

    // -- Navigation ----------------------------------------------------
    showStep(step) {
        document.querySelectorAll('.step-section').forEach(s => s.classList.remove('active'));
        const target = document.getElementById(`step-${step}`);
        if (target) target.classList.add('active');

        document.querySelectorAll('.step').forEach((s, i) => {
            s.classList.remove('active');
            if (i + 1 < step) s.classList.add('completed');
            else s.classList.remove('completed');
            if (i + 1 === step) s.classList.add('active');
        });

        const progress = ((step - 1) / (this.totalSteps - 1)) * 100;
        document.querySelector('.stepper-progress').style.width = `calc(${progress}% - 0px)`;

        this.currentStep = step;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    nextStep() {
        if (this.validateStep(this.currentStep)) {
            this.saveStepData(this.currentStep);
            if (this.currentStep < this.totalSteps) {
                this.onStepEnter(this.currentStep + 1);
                this.showStep(this.currentStep + 1);
            }
        }
    },

    prevStep() {
        if (this.currentStep > 1) {
            this.showStep(this.currentStep - 1);
        }
    },

    // -- Events --------------------------------------------------------
    bindEvents() {
        document.querySelectorAll('.step').forEach((s, i) => {
            s.addEventListener('click', () => {
                if (i + 1 <= this.currentStep) this.showStep(i + 1);
            });
        });

        // Real-time field validation on blur
        document.addEventListener('focusout', (e) => {
            if (e.target.tagName === 'INPUT' && e.target.type === 'number') {
                this.validateField(e.target);
            }
            // CA advisory when fluid field changes (now in Step 1)
            if (e.target.id === 'fluid-service') {
                this.showCAAdvisory();
            }
        });
    },

    // -- CA Advisory Display (Step 1) ------------------------------------
    showCAAdvisory() {
        const box = document.getElementById('ca-advisory-box');
        if (!box) return;
        const fluid = document.getElementById('fluid-service')?.value || '';
        const caVal = parseFloat(document.getElementById('pms-ca')?.value);
        if (!fluid || isNaN(caVal)) { box.style.display = 'none'; return; }

        const CA_RECS = {
            'Process Water': [1.5, 2.0], 'Seawater': [3.0, 6.0], 'Steam': [0.0, 1.5],
            'Crude Oil': [1.5, 3.0], 'Natural Gas': [1.0, 1.5], 'Caustic': [1.5, 3.0],
            'Acid': [3.0, 6.0], 'Instrument Air': [0.0, 0.0], 'Cooling Water': [1.5, 2.5],
            'Demineralized Water': [0.0, 1.0], 'Produced Water': [3.0, 6.0],
            'Diesel': [1.0, 2.0], 'Ammonia': [1.5, 3.0], 'Nitrogen': [0.0, 0.0],
            'Hydrogen': [0.0, 1.5], 'Lube Oil': [0.5, 1.5],
        };

        // Keyword match
        let match = null;
        const fluidLower = fluid.toLowerCase();
        for (const [key, range] of Object.entries(CA_RECS)) {
            if (fluidLower.includes(key.toLowerCase()) || key.toLowerCase().includes(fluidLower)) {
                match = { fluid: key, low: range[0], high: range[1] };
                break;
            }
        }

        if (!match) { box.style.display = 'none'; return; }

        if (caVal > match.high) {
            box.style.display = 'block';
            box.style.borderColor = '#f39c12';
            box.style.background = '#fef9e7';
            box.innerHTML = `<strong>CA Advisory:</strong> CA of ${caVal} mm is conservative for <strong>${match.fluid}</strong>. Typical range: ${match.low} - ${match.high} mm. Consider reviewing.`;
        } else if (caVal < match.low) {
            box.style.display = 'block';
            box.style.borderColor = '#e74c3c';
            box.style.background = '#fdf2f2';
            box.innerHTML = `<strong>CA Warning:</strong> CA of ${caVal} mm may be insufficient for <strong>${match.fluid}</strong>. Typical range: ${match.low} - ${match.high} mm.`;
        } else {
            box.style.display = 'block';
            box.style.borderColor = '#27ae60';
            box.style.background = '#e8f8f0';
            box.innerHTML = `<strong>CA OK:</strong> CA of ${caVal} mm is within typical range (${match.low} - ${match.high} mm) for <strong>${match.fluid}</strong>.`;
        }
    },

    validateField(input) {
        const group = input.closest('.form-group');
        if (!group) return;
        const val = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);
        let error = '';

        if (input.id === 'design-pressure' && (isNaN(val) || val <= 0)) {
            error = 'Pressure must be greater than 0';
        } else if (!isNaN(min) && !isNaN(val) && val < min) {
            error = `Minimum value is ${min}`;
        } else if (!isNaN(max) && !isNaN(val) && val > max) {
            error = `Maximum value is ${max}`;
        }

        group.classList.remove('has-error');
        const existing = group.querySelector('.form-error');
        if (existing) existing.remove();

        if (error) {
            group.classList.add('has-error');
            const errEl = document.createElement('div');
            errEl.className = 'form-error';
            errEl.textContent = error;
            group.appendChild(errEl);
        }
    },

    // -- Step 1: PMS Code & Material Selection ----------------------------
    _pmsRefData: null,
    _pmsMaterialMap: null,
    _materialTypeGrades: null,

    async loadPMSReference() {
        try {
            const refRes = await fetch('/api/pms_code/reference');
            this._pmsRefData = await refRes.json();
            this._materialTypeGrades = this._pmsRefData.material_type_grades || {};
            this.populatePMSDropdowns(this._pmsRefData);
        } catch (e) {
            console.error('Failed to load PMS reference data:', e);
            this.showToast('Failed to load PMS reference data. Check server.', 'error');
        }
    },

    populatePMSDropdowns(ref) {
        // Part 1 - Pressure Rating (keep placeholder as first option)
        const p1 = document.getElementById('pms-part1');
        p1.innerHTML = '<option value="" disabled selected>Please select Pressure Rating</option>' +
            Object.entries(ref.part1_options)
            .map(([code, info]) => `<option value="${code}">${code} &mdash; ${info.rating}</option>`)
            .join('');
        p1.value = '';  // reset to placeholder

        // Part 2 - Material (unique material types)
        const materialMap = {};
        for (const [code, info] of Object.entries(ref.part2_options)) {
            if (!materialMap[info.material_type]) {
                materialMap[info.material_type] = { description: info.description, codes: [] };
            }
            materialMap[info.material_type].codes.push({ code: parseInt(code), ca_mm: info.ca_mm });
        }
        this._pmsMaterialMap = materialMap;

        // Populate material dropdown (starts with placeholder)
        this._populateMaterialDropdown();

        // Part 2 - CA (starts with placeholder)
        this.updateCAOptions();

        // Part 3 - Show/hide correct section based on initial Part 1
        const isTubing = document.getElementById('pms-part1').value === 'T';
        const checkboxSection = document.getElementById('part3-checkboxes');
        const tubingSection = document.getElementById('part3-tubing');
        if (checkboxSection) checkboxSection.style.display = isTubing ? 'none' : 'block';
        if (tubingSection) tubingSection.style.display = isTubing ? 'block' : 'none';
    },

    _populateMaterialDropdown(selectTubing) {
        const matSel = document.getElementById('pms-material');
        const isTubing = selectTubing !== undefined ? selectTubing : document.getElementById('pms-part1').value === 'T';
        const materialMap = this._pmsMaterialMap || {};

        matSel.innerHTML = '<option value="" disabled selected>Please select Material Type</option>' +
            Object.entries(materialMap)
            .filter(([type]) => isTubing ? type.includes('Tubing') : !type.includes('Tubing'))
            .map(([type, info]) => {
                const gradeInfo = this._materialTypeGrades?.[type];
                const displayName = gradeInfo?.display_name || info.description;
                return `<option value="${type}">${type} (${displayName})</option>`;
            })
            .join('');
        matSel.value = '';  // reset to placeholder
    },

    updateCAOptions() {
        const matType = document.getElementById('pms-material').value;
        const caSel = document.getElementById('pms-ca');
        const matData = this._pmsMaterialMap ? this._pmsMaterialMap[matType] : null;

        if (!matData) {
            caSel.innerHTML = '<option value="" disabled selected>Please select CA</option>';
            caSel.value = '';
            return;
        }

        const caOptions = matData.codes.sort((a, b) => a.ca_mm - b.ca_mm);
        caSel.innerHTML = '<option value="" disabled selected>Please select CA</option>' +
            caOptions.map(c =>
                `<option value="${c.ca_mm}">${c.ca_mm > 0 ? c.ca_mm + ' mm' : 'None (0 mm)'}</option>`
            ).join('');
        caSel.value = '';  // reset to placeholder
    },

    // Part 3 is now checkboxes (L/N) + radio (A/B/C) — no dropdown to populate.
    // resolvePart3() reads the UI state; onPart3Change() triggers revalidation.

    resolvePart3() {
        const isTubing = document.getElementById('pms-part1').value === 'T';
        if (isTubing) {
            const sel = document.querySelector('input[name="tubing-pressure"]:checked');
            return sel && sel.value ? sel.value : null;
        }
        let part3 = '';
        if (document.getElementById('opt-low-temp')?.checked) part3 += 'L';
        if (document.getElementById('opt-nace')?.checked) part3 += 'N';
        return part3 || null;
    },

    onPart3Change() {
        this.onPMSPartChange();
    },

    resolvePart2Code() {
        const matType = document.getElementById('pms-material').value;
        const caMm = parseFloat(document.getElementById('pms-ca').value);
        if (!this._pmsMaterialMap || !this._pmsMaterialMap[matType]) return null;

        const match = this._pmsMaterialMap[matType].codes.find(c => c.ca_mm === caMm);
        return match ? match.code : null;
    },

    resolveMSRFromMaterialType() {
        const matType = document.getElementById('pms-material').value;
        if (!this._materialTypeGrades || !this._materialTypeGrades[matType]) return;

        const gradeInfo = this._materialTypeGrades[matType];
        this.data.msr = {
            material_grade: gradeInfo.grade || matType,
            material_type: gradeInfo.base_type || matType,
            material_spec: gradeInfo.spec || '',
            smts_psi: gradeInfo.smts || 0,
            smys_psi: gradeInfo.smys || 0,
            pms_material_type: matType,
        };
    },

    onPMSPart1Change() {
        // Reset Step 2 design condition inputs so new defaults are applied for the new class
        const dpInput   = document.getElementById('input-design-pressure');
        const dtInput   = document.getElementById('input-design-temp');
        const mdmtInput = document.getElementById('input-mdmt');
        if (dpInput)   dpInput.value   = '';
        if (dtInput)   dtInput.value   = '';
        if (mdmtInput) mdmtInput.value = '';
        this._ptData = null;  // Clear cached P-T data

        const isTubing = document.getElementById('pms-part1').value === 'T';

        // Show/hide Part 3 sections
        const checkboxSection = document.getElementById('part3-checkboxes');
        const tubingSection = document.getElementById('part3-tubing');
        if (checkboxSection) checkboxSection.style.display = isTubing ? 'none' : 'block';
        if (tubingSection) tubingSection.style.display = isTubing ? 'block' : 'none';

        // Reset Part 3 selections when switching
        if (isTubing) {
            // Reset checkboxes
            const optLow = document.getElementById('opt-low-temp');
            const optNace = document.getElementById('opt-nace');
            if (optLow) optLow.checked = false;
            if (optNace) optNace.checked = false;
            // Reset tubing radio to "None"
            const noneRadio = document.querySelector('input[name="tubing-pressure"][value=""]');
            if (noneRadio) noneRadio.checked = true;
        } else {
            // Reset tubing radio
            const noneRadio = document.querySelector('input[name="tubing-pressure"][value=""]');
            if (noneRadio) noneRadio.checked = true;
        }

        // Rebuild material dropdown to show only tubing or non-tubing materials
        this._populateMaterialDropdown(isTubing);
        this.updateCAOptions();
        this.resolveMSRFromMaterialType();

        // Auto-set Low Temp and NACE for non-tubing materials
        if (!isTubing) {
            const matType = document.getElementById('pms-material').value;
            const gradeInfo = this._materialTypeGrades?.[matType];
            if (gradeInfo) {
                const optLow = document.getElementById('opt-low-temp');
                const optNace = document.getElementById('opt-nace');
                if (optLow) optLow.checked = !!gradeInfo.is_low_temp;
                if (optNace) optNace.checked = !!gradeInfo.is_nace;
            }
        }

        this.onPMSPartChange();
    },

    onPMSMaterialChange() {
        this.updateCAOptions();
        // If tubing material selected, auto-set Part 1 to T and show tubing radios
        const matType = document.getElementById('pms-material').value;
        if (matType.includes('Tubing')) {
            document.getElementById('pms-part1').value = 'T';
            // Show tubing section, hide checkboxes
            const checkboxSection = document.getElementById('part3-checkboxes');
            const tubingSection = document.getElementById('part3-tubing');
            if (checkboxSection) checkboxSection.style.display = 'none';
            if (tubingSection) tubingSection.style.display = 'block';
        } else {
            // Ensure checkboxes shown, tubing hidden (unless Part1 is T)
            const isTubing = document.getElementById('pms-part1').value === 'T';
            if (!isTubing) {
                const checkboxSection = document.getElementById('part3-checkboxes');
                const tubingSection = document.getElementById('part3-tubing');
                if (checkboxSection) checkboxSection.style.display = 'block';
                if (tubingSection) tubingSection.style.display = 'none';
            }
            // Auto-select Low Temp and NACE checkboxes based on material properties
            const gradeInfo = this._materialTypeGrades?.[matType];
            if (gradeInfo) {
                const optLow = document.getElementById('opt-low-temp');
                const optNace = document.getElementById('opt-nace');
                if (optLow) optLow.checked = !!gradeInfo.is_low_temp;
                if (optNace) optNace.checked = !!gradeInfo.is_nace;
            }
        }
        // Resolve ASTM grade from material type
        this.resolveMSRFromMaterialType();
        this.showCAAdvisory();
        this.onPMSPartChange();
    },

    async onPMSPartChange() {
        const part1 = document.getElementById('pms-part1').value;
        const part2 = this.resolvePart2Code();
        const part3 = this.resolvePart3();

        if (!part1 || part2 === null) {
            document.getElementById('pms-code-value').textContent = '--';
            document.getElementById('pms-code-description').textContent = '';
            document.getElementById('pms-code-reference').textContent = '';
            document.getElementById('material-id-table').style.display = 'none';
            return;
        }

        try {
            const res = await fetch('/api/pms_code/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ part1, part2, part3 }),
            });
            const data = await res.json();

            // Update live code display
            const codeEl = document.getElementById('pms-code-value');
            codeEl.textContent = data.code.pms_code;
            codeEl.className = data.validation.valid ? '' : 'invalid';
            document.getElementById('pms-code-description').textContent = data.code.description;
            document.getElementById('pms-code-reference').textContent = data.code.pms_reference;

            // Update validation panel
            this.renderPMSValidation(data.validation);

            // Update suggestions
            this.renderPMSSuggestions(data.suggestions);

            // Store in App.data (backward-compatible shape)
            this.data.spec_code = {
                spec_code: data.code.pms_code,
                pms_code: data.code.pms_code,
                pms_reference: data.code.pms_reference,
                description: data.code.description,
                part1: data.code.part1,
                part2: data.code.part2,
                part3: data.code.part3,
                part3_code: data.code.part3,
                part1_info: data.code.part1_info,
                part2_info: data.code.part2_info,
                part3_info: data.code.part3_info,
                is_nace: !!document.getElementById('opt-nace')?.checked,
                is_low_temp: !!document.getElementById('opt-low-temp')?.checked,
            };

            // Enable/disable Next button
            const nextBtn = document.getElementById('pms-next-btn');
            if (nextBtn) nextBtn.disabled = !data.validation.valid;

            // Update Material ID table
            this.updateMaterialIDTable(data);

            // Update CA advisory
            this.showCAAdvisory();

        } catch (e) {
            console.error(e);
        }
    },

    updateMaterialIDTable(data) {
        const tableDiv = document.getElementById('material-id-table');
        const tbody = document.getElementById('material-id-tbody');
        if (!tableDiv || !tbody) return;

        if (!data.validation.valid) {
            tableDiv.style.display = 'none';
            return;
        }

        const matType = document.getElementById('pms-material').value;
        const caMm = document.getElementById('pms-ca').value;
        const service = document.getElementById('fluid-service')?.value || '';
        const matData = this._pmsMaterialMap ? this._pmsMaterialMap[matType] : null;

        this._materialIdCounter = 1;
        const materialId = `MAT-${String(this._materialIdCounter).padStart(3, '0')}`;

        tbody.innerHTML = `
            <tr>
                <td><strong>${materialId}</strong></td>
                <td><code style="font-size:1.1rem;color:#1a5276;font-weight:bold;">${data.code.pms_code}</code></td>
                <td>${matType}</td>
                <td>${matData ? matData.description : ''}</td>
                <td>${parseFloat(caMm) > 0 ? caMm + ' mm' : 'None'}</td>
                <td>${service}</td>
            </tr>
        `;
        tableDiv.style.display = 'block';
    },

    renderPMSValidation(validation) {
        const panel = document.getElementById('pms-validation-panel');
        if (validation.valid && validation.warnings.length === 0) {
            panel.innerHTML = `
                <div class="verification-box pass">
                    <strong>Valid PMS Code</strong>
                    <p>No conflicts detected. All rules pass.</p>
                </div>`;
            return;
        }

        let html = '';
        if (!validation.valid) {
            html += `<div class="verification-box fail"><strong>Invalid Combination</strong>`;
            html += validation.errors.map(e => `<p>${e}</p>`).join('');
            html += `</div>`;
        }
        if (validation.warnings.length > 0) {
            html += `<div class="verification-box" style="border-color:#f39c12;background:#fef9e7;">
                <strong style="color:#f39c12;">Warnings</strong>`;
            html += validation.warnings.map(w => `<p>${w}</p>`).join('');
            html += `</div>`;
        }
        panel.innerHTML = html;
    },

    renderPMSSuggestions(suggestions) {
        const panel = document.getElementById('pms-suggestions-panel');
        const list = document.getElementById('pms-suggestions-list');
        if (!suggestions || suggestions.length === 0) {
            panel.style.display = 'none';
            return;
        }
        panel.style.display = 'block';
        list.innerHTML = suggestions.map(s => `
            <div class="pms-suggestion-chip" title="${s.reason}">
                <strong>${s.pms_code}</strong>
                <span style="font-size:0.85rem;color:#666;margin-left:6px;">${s.reason}</span>
            </div>
        `).join('');
    },

    // -- Step Validation -----------------------------------------------
    validateStep(step) {
        switch (step) {
            case 1: {
                const part1 = document.getElementById('pms-part1').value;
                const matType = document.getElementById('pms-material').value;
                if (!part1) { this.showToast('Please select a Pressure Rating.', 'error'); return false; }
                if (!matType) { this.showToast('Please select a Material Type.', 'error'); return false; }
                // Validate PMS code is set and valid
                const pmsCode = document.getElementById('pms-code-value')?.textContent;
                if (!pmsCode || pmsCode === '--') { this.showToast('PMS code must be generated. Check your selections.', 'error'); return false; }
                const pmsEl = document.getElementById('pms-code-value');
                if (pmsEl && pmsEl.classList.contains('invalid')) { this.showToast('PMS code combination is invalid. Fix the errors.', 'error'); return false; }
                return true;
            }
            case 2: {
                const dp = parseFloat(document.getElementById('input-design-pressure')?.value);
                const dt = parseFloat(document.getElementById('input-design-temp')?.value);
                if (!dp || dp <= 0) {
                    this.showToast('Please enter the actual Design Pressure (barg).', 'error');
                    return false;
                }
                if (isNaN(dt)) {
                    this.showToast('Please enter the actual Design Temperature (°C).', 'error');
                    return false;
                }
                return true;
            }
            default:
                return true;
        }
    },

    // -- Save Step Data ------------------------------------------------
    saveStepData(step) {
        switch (step) {
            case 1: {
                // Save CA from PMS CA dropdown
                const caMm = parseFloat(document.getElementById('pms-ca').value) || 0;
                this.data.msr.corrosion_allowance_mm = caMm;
                this.data.msr.corrosion_allowance_in = parseFloat((caMm / 25.4).toFixed(4));
                // Save service
                this.data.msr.fluid_service = document.getElementById('fluid-service')?.value || 'Process Water';

                // Store a placeholder for _derivedDesign — actual values are entered
                // by the user in Step 2 (Design Pressure barg + Design Temperature °C).
                // Only initialise if not already set (don't overwrite user-entered values).
                const isLowTemp = document.getElementById('opt-low-temp')?.checked || false;
                const isNace    = document.getElementById('opt-nace')?.checked    || false;
                const mdmt = (isLowTemp || isNace) ? -20 : 0;
                if (!this._derivedDesign) {
                    this._derivedDesign = {
                        designP: 150, testP: 225, designT: 300,
                        operP: 120, operT: 240, mdmt,
                        jointType: 'seamless'
                    };
                } else {
                    this._derivedDesign.mdmt = mdmt;
                }
                break;
            }
            case 2: {
                // Read actual design conditions from user-input fields (Step 2)
                const dpBarg    = parseFloat(document.getElementById('input-design-pressure')?.value) || null;
                const dtC       = parseFloat(document.getElementById('input-design-temp')?.value) || null;
                const mdmtC     = parseFloat(document.getElementById('input-mdmt')?.value);
                const jointType = document.getElementById('input-joint-type')?.value || 'seamless';

                // Convert to imperial for internal calculations (ASME B31.3 uses psi/°F)
                const d = this._derivedDesign || {};
                const designP = dpBarg != null ? parseFloat((dpBarg / 0.0689476).toFixed(1))
                                               : (d.designP || 150);
                const designT = dtC != null    ? parseFloat((dtC * 9 / 5 + 32).toFixed(0))
                                               : (d.designT || 300);
                const dpBarSave = dpBarg != null ? dpBarg : parseFloat((designP * 0.0689476).toFixed(2));
                const testP  = parseFloat((designP * 1.5).toFixed(1));
                const operP  = Math.round(designP * 0.8);
                const operT  = Math.round(designT * 0.8);
                const mdmt   = isNaN(mdmtC) ? (d.mdmt !== undefined ? d.mdmt : -20)
                                            : parseFloat((mdmtC * 9 / 5 + 32).toFixed(0));
                const fluid  = this.data.msr.fluid_service || 'Process Water';

                this.data.line_list = {
                    fluid: fluid,
                    design_pressure_psig: designP,
                    design_pressure_barg: dpBarSave,
                    design_pressure_bar: dpBarSave,
                    test_pressure_psig: testP,
                    design_temp_f: designT,
                    design_temp_c: parseFloat(((designT - 32) * 5 / 9).toFixed(1)),
                    operating_pressure_psig: operP,
                    operating_temp_f: operT,
                    mdmt_f: mdmt,
                    mdmt_c: isNaN(mdmtC) ? parseFloat(((mdmt - 32) * 5 / 9).toFixed(1)) : mdmtC,
                    joint_type: jointType,
                };
                break;
            }
        }
    },

    // -- On Step Enter (auto-calculations) ----------------------------
    async onStepEnter(step) {
        switch (step) {
            case 2:
                await this.loadPipeSizes();
                await this.loadPTRatingTable();
                break;
            case 3:
                await this.calcFullScheduleTable();
                break;
            case 4:
                await this.calcFittings();
                break;
            case 5:
                await this.calcFlanges();
                break;
            case 6:
                await this.runReviewAndValidation();
                break;
            case 7:
                await this.generateFinalPMS();
                break;
        }
    },

    // -- Load Pipe Sizes -----------------------------------------------
    async loadPipeSizes() {
        const matType = this.data.msr.material_type || 'CS';
        const res = await fetch(`/api/pipe_sizes?material_type=${matType}`);
        this._availablePipeSizes = await res.json();
    },

    // -- Step 2: P-T Rating Table -------------------------------------
    async loadPTRatingTable() {
        const part1 = document.getElementById('pms-part1').value;
        const part1Info = this._pmsRefData?.part1_options?.[part1];
        if (!part1Info || !part1Info.pressure_psig) {
            document.getElementById('pt-rating-result').innerHTML =
                '<div class="info-box">P-T rating not applicable for Tubing.</div>';
            document.getElementById('step1-summary-panel').innerHTML = '';
            document.getElementById('derived-design-panel').innerHTML = '';
            return;
        }

        const pressureClass = part1Info.pressure_psig;
        const matType = this.data.msr.material_type || 'CS';

        // Render Step 1 summary panel
        this._renderStep1Summary(pressureClass, matType);

        try {
            const res = await fetch(`/api/pt_rating_table?pressure_class=${pressureClass}&material_type=${matType}`);
            const data = await res.json();

            // Store for later re-render
            this._ptData = data;

            if (data.pt_pairs && data.pt_pairs.length > 0) {
                const maxP = Math.max(...data.pt_pairs.map(pt => pt.pressure_psig));
                this._maxAllowablePressure = maxP;

                // Set sensible default design conditions only if the fields are empty
                const dpInput = document.getElementById('input-design-pressure');
                const dtInput = document.getElementById('input-design-temp');
                const mdmtInput = document.getElementById('input-mdmt');

                if (!dpInput.value) {
                    // Default: MAWP at 100°C for CS, 150°C for SS
                    const baseType = this._materialTypeGrades?.[matType]?.base_type || 'CS';
                    const defaultTempC = baseType === 'SS' ? 150 : 100;
                    const ptAtDefaultTemp = data.pt_pairs.find(p => p.temp_c >= defaultTempC)
                                        || data.pt_pairs[0];
                    dpInput.value = ptAtDefaultTemp ? ptAtDefaultTemp.pressure_barg : parseFloat((maxP * 0.0689476).toFixed(1));
                }
                if (!dtInput.value) {
                    const baseType = this._materialTypeGrades?.[matType]?.base_type || 'CS';
                    dtInput.value = baseType === 'SS' ? 150 : 100;
                }
                if (!mdmtInput.value) {
                    const isLowTemp = document.getElementById('opt-low-temp')?.checked;
                    const isNace = document.getElementById('opt-nace')?.checked;
                    mdmtInput.value = (isLowTemp || isNace) ? -46 : -29;
                }

                // Trigger update to populate _derivedDesign and line_list from inputs
                this.onDesignConditionsChange();
            }

            // Render derived design conditions panel
            this._renderDerivedDesignPanel();

            // Render P-T table
            this.renderPTRatingTable(data);
        } catch (e) {
            console.error('P-T rating fetch failed:', e);
        }
    },

    // -- On design conditions input change ----------------------------
    onDesignConditionsChange() {
        const dpBarg    = parseFloat(document.getElementById('input-design-pressure')?.value) || 0;
        const dtC       = parseFloat(document.getElementById('input-design-temp')?.value) || 100;
        const mdmtC     = parseFloat(document.getElementById('input-mdmt')?.value);
        const jointType = document.getElementById('input-joint-type')?.value || 'seamless';

        const dpPsig  = parseFloat((dpBarg / 0.0689476).toFixed(1));
        const dtF     = parseFloat((dtC * 9 / 5 + 32).toFixed(0));
        const mdmtF   = isNaN(mdmtC) ? -20 : parseFloat((mdmtC * 9 / 5 + 32).toFixed(0));

        // Update hint labels with imperial equivalents
        const dpHint    = document.getElementById('dp-psig-hint');
        const dtHint    = document.getElementById('dt-f-hint');
        const mdmtHint  = document.getElementById('mdmt-f-hint');
        const jointHint = document.getElementById('joint-e-hint');
        if (dpHint && dpBarg > 0)      dpHint.textContent   = `≈ ${Math.round(dpPsig)} psig`;
        if (dtHint && !isNaN(dtC))     dtHint.textContent   = `= ${Math.round(dtF)} °F`;
        if (mdmtHint && !isNaN(mdmtC)) mdmtHint.textContent = `= ${Math.round(mdmtF)} °F`;
        if (jointHint) {
            const eMap = { seamless: 'E = 1.00', erw: 'E = 0.85', furnace_butt: 'E = 0.60' };
            jointHint.textContent = `ASME B31.3 Table A-1B — ${eMap[jointType] || ''}`;
        }

        // Update _derivedDesign with user values
        if (!this._derivedDesign) this._derivedDesign = {};
        const testP  = parseFloat((dpPsig * 1.5).toFixed(1));
        const operP  = Math.round(dpPsig * 0.8);
        const operT  = Math.round(dtF * 0.8);
        this._derivedDesign.designP   = dpPsig;
        this._derivedDesign.designT   = dtF;
        this._derivedDesign.testP     = testP;
        this._derivedDesign.operP     = operP;
        this._derivedDesign.operT     = operT;
        this._derivedDesign.mdmt      = mdmtF;
        this._derivedDesign.jointType = jointType;

        // Re-save line_list with user values
        this.saveStepData(2);

        // Re-render derived panel and P-T table highlight
        this._renderDerivedDesignPanel();
        if (this._ptData) this.renderPTRatingTable(this._ptData);
    },

    _renderStep1Summary(pressureClass, matType) {
        const pmsCode = document.getElementById('pms-code-value')?.textContent || '--';
        const materialGrade = this.data.msr.material_grade || '--';
        const materialSpec = this.data.msr.material_spec || '--';
        const caMm = this.data.msr.corrosion_allowance_mm || 0;
        const service = this.data.msr.fluid_service || '--';
        const isLowTemp = document.getElementById('opt-low-temp')?.checked || false;
        const isNace = document.getElementById('opt-nace')?.checked || false;

        const panel = document.getElementById('step1-summary-panel');
        panel.innerHTML = `
            <div class="summary-grid" style="margin-bottom:15px">
                <div class="summary-panel">
                    <h4>PMS Inputs (from Step 1)</h4>
                    <div class="summary-row"><span class="label">PMS Code</span><span class="value" style="font-weight:bold;color:#1a5276;font-size:1.1rem">${pmsCode}</span></div>
                    <div class="summary-row"><span class="label">Pressure Rating</span><span class="value">${pressureClass}# (Class ${pressureClass})</span></div>
                    <div class="summary-row"><span class="label">Material Type</span><span class="value">${matType}</span></div>
                    <div class="summary-row"><span class="label">Material Grade</span><span class="value">${materialGrade} (${materialSpec})</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Service &amp; Material</h4>
                    <div class="summary-row"><span class="label">Service</span><span class="value">${service}</span></div>
                    <div class="summary-row"><span class="label">Corrosion Allowance</span><span class="value">${caMm} mm</span></div>
                    <div class="summary-row"><span class="label">Low Temperature</span><span class="value">${isLowTemp ? '<span style="color:#c0392b;font-weight:bold">Yes</span>' : 'No'}</span></div>
                    <div class="summary-row"><span class="label">NACE MR0175</span><span class="value">${isNace ? '<span style="color:#c0392b;font-weight:bold">Yes</span>' : 'No'}</span></div>
                    <div style="margin-top:8px;font-size:0.8rem;color:#7f8c8d">&darr; Enter actual process conditions below</div>
                </div>
            </div>
        `;
    },

    _renderDerivedDesignPanel() {
        const d = this._derivedDesign || {};

        // Read actual design P/T from user input fields (source of truth)
        const dpBarg  = parseFloat(document.getElementById('input-design-pressure')?.value) || 0;
        const dtC     = parseFloat(document.getElementById('input-design-temp')?.value) || 100;
        const mdmtC   = parseFloat(document.getElementById('input-mdmt')?.value);

        if (dpBarg <= 0) {
            document.getElementById('derived-design-panel').innerHTML = '';
            return;  // Don't render until user has entered a value
        }

        const designP = parseFloat((dpBarg / 0.0689476).toFixed(1));
        const designT = parseFloat((dtC * 9 / 5 + 32).toFixed(0));
        const testP   = parseFloat((designP * 1.5).toFixed(1));
        const operP   = Math.round(designP * 0.8);
        const operT   = Math.round(designT * 0.8);

        const testP_barg   = (testP * 0.0689476).toFixed(1);
        const operP_barg   = (operP * 0.0689476).toFixed(1);
        const operT_c      = ((operT - 32) * 5 / 9).toFixed(0);
        const mdmt_c_disp  = isNaN(mdmtC) ? ((d.mdmt || -20) - 32) * 5 / 9 : mdmtC;
        const mdmt_f_disp  = isNaN(mdmtC) ? (d.mdmt || -20) : parseFloat((mdmtC * 9 / 5 + 32).toFixed(0));

        const panel = document.getElementById('derived-design-panel');
        panel.innerHTML = `
            <div class="info-box formula" style="margin-bottom:15px">
                <strong>Derived Design Conditions</strong> (auto-calculated from your inputs above)
            </div>
            <div class="summary-grid" style="margin-bottom:15px">
                <div class="summary-panel">
                    <h4>Pressure</h4>
                    <div class="summary-row"><span class="label">Design Pressure</span><span class="value"><strong>${dpBarg} barg</strong> (${Math.round(designP)} psig)</span></div>
                    <div class="summary-row"><span class="label">Hydrotest (1.5&times;DP)</span><span class="value"><strong>${testP_barg} barg</strong> (${testP} psig)</span></div>
                    <div class="summary-row"><span class="label">Operating (est. 80% DP) <em style="color:#e67e22">&#9888;</em></span><span class="value">${operP_barg} barg (${operP} psig)</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Temperature</h4>
                    <div class="summary-row"><span class="label">Design Temperature</span><span class="value"><strong>${dtC}&deg;C</strong> (${Math.round(designT)}&deg;F)</span></div>
                    <div class="summary-row"><span class="label">Operating (est. 80% DT) <em style="color:#e67e22">&#9888;</em></span><span class="value">${Math.round(parseFloat(operT_c))}&deg;C (${operT}&deg;F)</span></div>
                    <div class="summary-row"><span class="label">MDMT</span><span class="value">${Math.round(mdmt_c_disp)}&deg;C (${Math.round(mdmt_f_disp)}&deg;F)</span></div>
                </div>
                <div style="grid-column:1/-1;font-size:0.78rem;color:#e67e22;padding:4px 2px">
                    &#9888; Operating conditions are placeholder estimates (80% of design). Replace with actual P&amp;ID / process data sheet values — especially for dynamic processes (reciprocating machinery, two-phase flow, surge).
                </div>
            </div>
        `;
    },

    renderPTRatingTable(data) {
        const container = document.getElementById('pt-rating-result');
        if (!data.pt_pairs || data.pt_pairs.length === 0) {
            container.innerHTML = '<div class="info-box">No P-T data available for this class.</div>';
            return;
        }

        // Use actual user-entered design conditions (from Step 2 inputs)
        const dpBarg  = parseFloat(document.getElementById('input-design-pressure')?.value) || 0;
        const dtC     = parseFloat(document.getElementById('input-design-temp')?.value) || 100;
        const designP = dpBarg > 0 ? parseFloat((dpBarg / 0.0689476).toFixed(1))
                                   : (this._derivedDesign?.designP || this._maxAllowablePressure || 150);
        const designT = parseFloat((dtC * 9 / 5 + 32).toFixed(0));
        const designP_barg = dpBarg > 0 ? dpBarg.toFixed(1) : (designP * 0.0689476).toFixed(1);
        const designT_c = dtC;

        // Find rating at design temperature (first pair where temp_c >= design temp)
        let maxPAtDesignT = null;
        for (let i = 0; i < data.pt_pairs.length; i++) {
            const pt = data.pt_pairs[i];
            if (pt.temp_c >= designT_c) {
                maxPAtDesignT = pt;
                break;
            }
        }
        if (!maxPAtDesignT) maxPAtDesignT = data.pt_pairs[data.pt_pairs.length - 1];

        // Compare in barg (native units from ASME B16.5 metric tables — more precise)
        const isAdequate = maxPAtDesignT && maxPAtDesignT.pressure_barg >= parseFloat(designP_barg);

        // Determine standard label
        const stdLabel = data.pressure_class <= 2500 ? 'ASME B16.5-2020' : 'API 6A';
        const groupLabel = data.material_type === 'SS' ? 'Group 2.3 (A182 F316/F316L)' : 'Group 1.1 (A105/A216 WCB)';

        // Build table rows — temperature as columns, pressure as rows
        let thCells = '';
        let tdBarg = '';
        for (const pt of data.pt_pairs) {
            const isDesignPoint = maxPAtDesignT && pt.temp_c === maxPAtDesignT.temp_c;
            const highlight = isDesignPoint ? ' style="background:#fff3cd;font-weight:bold"' : '';
            thCells += `<th${highlight}>${pt.temp_c}</th>`;
            tdBarg += `<td${highlight}>${pt.pressure_barg}</td>`;
        }

        const statusClass = isAdequate ? 'pass' : 'fail';
        const statusIcon = isAdequate ? '&#10003;' : '&#10007;';
        const maxP_barg = maxPAtDesignT ? maxPAtDesignT.pressure_barg : 0;
        const statusText = isAdequate
            ? `Class ${data.pressure_class}# is ADEQUATE: ${maxP_barg} barg ≥ Design ${designP_barg} barg at ${designT_c}°C`
            : `Class ${data.pressure_class}# may be INSUFFICIENT: ${maxP_barg} barg < Design ${designP_barg} barg at ${designT_c}°C`;

        container.innerHTML = `
            <div class="info-box" style="margin-bottom:10px">
                <strong>Standard:</strong> ${stdLabel} &nbsp;|&nbsp;
                <strong>Table:</strong> ${groupLabel} &nbsp;|&nbsp;
                <strong>Class:</strong> ${data.pressure_class}# &nbsp;|&nbsp;
                <strong>Material:</strong> ${data.material_type}
            </div>
            <h4 style="margin:10px 0 5px;color:#1a5276">Pressure–Temperature Rating Table</h4>
            <p style="font-size:0.82rem;color:#666;margin-bottom:8px">
                Units: Pressure in <strong>barg</strong>, Temperature in <strong>°C</strong>.
                <span style="background:#fff3cd;padding:2px 6px;border-radius:3px;margin-left:5px">Highlighted column</span> = rating at design temperature.
            </p>
            <div style="overflow-x:auto;margin-top:5px">
                <table class="result-table" style="font-size:0.82rem;white-space:nowrap">
                    <thead>
                        <tr style="background:#1a5276;color:#fff">
                            <th style="text-align:left">Temp (&deg;C)</th>${thCells}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="text-align:left;font-weight:bold">Press. (barg)</td>${tdBarg}
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="verification-box ${statusClass}" style="margin-top:12px">
                <span style="font-size:1.3rem">${statusIcon}</span>
                <strong style="margin-left:8px">${statusText}</strong>
            </div>
        `;
    },

    // -- Step 3: Full Schedule & Wall Thickness Table -------------------
    async calcFullScheduleTable() {
        this.showLoading('Calculating schedule & wall thickness for all NPS sizes...');
        try {
            const d = this._derivedDesign || {};
            // Use actual user-entered design conditions from line_list (set in Step 2)
            const designP = this.data.line_list?.design_pressure_psig || d.designP || 285;
            const designT = this.data.line_list?.design_temp_f        || d.designT || 300;

            // Get pressure class from Part 1 selection
            const part1     = document.getElementById('pms-part1')?.value || '';
            const part1Info = this._pmsRefData?.part1_options?.[part1];
            const pressureClass      = part1Info?.pressure_psig  || 150;
            const pressureRatingLabel = part1Info?.rating         || '150#';

            const res = await fetch('/api/full_schedule_table', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    material_type: this.data.msr.material_type,
                    material_grade: this.data.msr.material_grade,
                    design_pressure_psig: designP,
                    design_temp_f: designT,
                    ca_mm: this.data.msr.corrosion_allowance_mm || 3,
                    mech_allowance_mm: 0,
                    joint_type: this.data.line_list?.joint_type || d.jointType || 'seamless',
                    mill_tolerance_pct: 12.5,
                    y_factor: 0.4,
                    is_low_temp: !!document.getElementById('opt-low-temp')?.checked,
                    is_nace: !!document.getElementById('opt-nace')?.checked,
                    service: document.getElementById('fluid-service')?.value || '',
                    pressure_class: pressureClass,
                    pressure_rating_label: pressureRatingLabel,
                }),
            });
            this._fullScheduleData = await res.json();
            // DEBUG: log API response
            console.log('[Step3] API response rows:');
            (this._fullScheduleData.rows || []).forEach(r => {
                console.log(`  NPS ${r.nps}: Sch=${r.schedule}, WT=${r.wt_nom_mm}mm`);
            });
            this.renderFullScheduleTable();

            // Store thickness/schedule data for downstream steps (fittings, etc.)
            const rows = this._fullScheduleData.rows;
            const nps6 = rows.find(r => r.nps === '6') || rows[0];
            this.data.thickness = {
                design_pressure_psig: this._fullScheduleData.design_inputs.design_pressure_psig,
                pipe_od_in: parseFloat((nps6.od_mm / 25.4).toFixed(4)),
                id_in: parseFloat(((nps6.od_mm - 2 * nps6.wt_nom_mm) / 25.4).toFixed(4)),
                material_grade: this._fullScheduleData.design_inputs.material_grade,
                design_temp_f: this._fullScheduleData.design_inputs.design_temp_f,
                allowable_stress_psi: this._fullScheduleData.design_inputs.allowable_stress_psi,
                joint_efficiency: this._fullScheduleData.design_inputs.joint_efficiency,
                joint_type: this._fullScheduleData.design_inputs.joint_type,
                y_factor: this._fullScheduleData.design_inputs.y_factor,
                corrosion_allowance_in: this._fullScheduleData.design_inputs.ca_mm / 25.4,
                mill_tolerance_pct: this._fullScheduleData.design_inputs.mill_tolerance_pct,
                t_calculated_in: parseFloat((nps6.t_req_mm / 25.4).toFixed(4)),
                t_min_required_in: parseFloat((nps6.t_min_mm / 25.4).toFixed(4)),
                t_nominal_min_in: parseFloat((nps6.t_min_mm / 25.4).toFixed(4)),
                t_nominal_min_mm: nps6.t_min_mm,
                schedule_number: Math.round(1000 * this._fullScheduleData.design_inputs.design_pressure_psig / this._fullScheduleData.design_inputs.allowable_stress_psi),
            };
            this.data.schedule = {
                selected_schedule: nps6.schedule,
                selected_wall_thickness_in: nps6.wt_nom_mm / 25.4,
                selected_wall_thickness_mm: nps6.wt_nom_mm,
                standard: this._fullScheduleData.design_inputs.pipe_standard,
                // Per-NPS schedule/WT rows for Excel export
                schedule_rows: rows.map(r => ({
                    nps: r.nps,
                    od_mm: r.od_mm,
                    schedule: r.schedule,
                    wt_mm: r.wt_nom_mm,
                })),
            };
        } catch (e) {
            console.error(e);
            this.showToast('Schedule table calculation failed.', 'error');
        }
        this.hideLoading();
    },

    renderFullScheduleTable() {
        const data    = this._fullScheduleData;
        const di      = data.design_inputs;
        const sm      = data.summary;
        const sc      = data.service_classification || {};
        const flags   = data.engineering_flags      || [];
        const pmsCode = this.data.spec_code?.pms_code || '--';

        // ── 1. Service classification badges ─────────────────────────────
        const svcMap = [
            { key: 'is_sour',     label: 'Sour / H₂S',  color: '#922b21' },
            { key: 'is_hydrogen', label: 'Hydrogen',     color: '#7d6608' },
            { key: 'is_steam',    label: 'Steam',        color: '#1a5276' },
            { key: 'is_acid',     label: 'Acid / Amine', color: '#7b241c' },
            { key: 'is_cyclic',   label: 'Cyclic',       color: '#6c3483' },
            { key: 'is_chloride', label: 'Chloride',     color: '#0e6655' },
        ];
        const svcBadges = svcMap
            .filter(s => sc[s.key])
            .map(s => `<span style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.78rem;font-weight:700;color:#fff;background:${s.color};margin:2px 3px 2px 0">${s.label}</span>`)
            .join('');
        const svcLine = svcBadges
            ? `<div style="margin-bottom:10px"><span style="font-size:0.82rem;color:#555;margin-right:6px">Service:</span>${svcBadges}</div>`
            : '';

        // ── 2. Engineering flags panel ────────────────────────────────────
        const severityStyle = { CRITICAL: '#c0392b', MANDATORY: '#e67e22', WARNING: '#f39c12', NOTE: '#2471a3' };
        const severityBg    = { CRITICAL: '#fdecea',  MANDATORY: '#fef5ec', WARNING: '#fefce8', NOTE: '#eaf3fb' };
        const severityBorder= { CRITICAL: '#e74c3c',  MANDATORY: '#e67e22', WARNING: '#f39c12', NOTE: '#3498db' };
        let flagsHTML = '';
        for (const f of flags) {
            const sev  = f.severity || 'NOTE';
            const col  = severityStyle[sev]  || '#555';
            const bg   = severityBg[sev]     || '#f9f9f9';
            const bdr  = severityBorder[sev] || '#ccc';
            flagsHTML += `
            <div style="border-left:4px solid ${bdr};background:${bg};padding:10px 14px;margin-bottom:8px;border-radius:0 6px 6px 0">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                    <span style="font-size:0.7rem;font-weight:800;letter-spacing:1px;color:#fff;background:${col};padding:1px 7px;border-radius:10px">${sev}</span>
                    <strong style="color:${col};font-size:0.9rem">${f.title}</strong>
                </div>
                <div style="font-size:0.83rem;color:#444;line-height:1.5">${f.detail}</div>
            </div>`;
        }
        const flagsSection = flags.length > 0 ? `
            <div style="margin-bottom:18px">
                <h4 style="color:#922b21;margin:0 0 10px;font-size:0.95rem">&#9888; Engineering Requirements &amp; Flags</h4>
                ${flagsHTML}
            </div>` : '';

        // ── 3. Formula block (NPS 6" substitution example) ────────────────
        const refRow = data.rows.find(r => r.nps === '6') || data.rows[0];
        const P   = di.design_pressure_psig;
        const OD  = refRow ? refRow.od_mm / 25.4 : '—';
        const S   = di.allowable_stress_psi;
        const E   = di.joint_efficiency;
        const W   = di.w_factor     ?? 1.0;
        const Y   = di.y_factor;
        const c   = (di.ca_mm / 25.4).toFixed(4);
        const wBasis = di.w_factor_basis || '';
        const yBasis = di.y_factor_basis || '';
        const denom  = 2 * (S * E * W + P * Y);
        const tCalc  = denom > 0 ? ((P * OD) / denom).toFixed(4) : '—';

        // ── 4. Build table rows ───────────────────────────────────────────
        const tagColors = { NACE: '#922b21', LTCS: '#1a5276', 'H₂↑': '#7d6608', FAIL: '#c0392b', Pressure: '#1e8449' };
        let tableRows = '';
        for (const r of data.rows) {
            const isFail = r.status === 'FAIL';
            const rowBg  = isFail ? '#fdecea' : '';
            const tagBadges = (r.tags || []).map(tag => {
                const tc = tagColors[tag] || '#555';
                return `<span style="font-size:0.68rem;font-weight:700;color:#fff;background:${tc};padding:1px 5px;border-radius:8px;margin-left:2px">${tag}</span>`;
            }).join('');
            const govShort = (r.governs || '').replace('Pressure (ASME B31.3 Eq. 3a)', 'Eq. 3a')
                                               .replace('Pressure (exceeds service minimum)', 'Eq. 3a ↑')
                                               .replace('Service minimum — ', '')
                                               .replace('Hydrogen service (conservative — one schedule heavier)', 'H₂ conservative');
            tableRows += `<tr style="background:${rowBg}">
                <td><strong>${r.nps}"</strong></td>
                <td>${r.od_mm}</td>
                <td><strong>${r.schedule}</strong> ${tagBadges}</td>
                <td>${r.wt_nom_mm}</td>
                <td>${r.t_req_mm}</td>
                <td>${r.t_min_mm}</td>
                <td>${r.t_eff_mm}</td>
                <td><strong>${r.mawp_barg}</strong></td>
                <td>${r.margin_pct}%</td>
                <td>${r.util_pct}%</td>
                <td style="font-size:0.75rem;color:#555;max-width:120px;white-space:normal">${govShort}</td>
                <td style="font-weight:bold;color:${isFail ? '#c0392b' : '#27ae60'}">${r.status}</td>
            </tr>`;
        }

        const container = document.getElementById('schedule-table-result');
        container.innerHTML = `
            <!-- Formula Reference Block -->
            <div style="background:#eaf3fb;border:1px solid #3498db;border-radius:8px;padding:14px 18px;margin-bottom:15px;font-size:0.88rem">
                <div style="font-weight:700;color:#1a5276;margin-bottom:6px">ASME B31.3 §304.1.2 — Internal Pressure (Eq. 3a, enhanced with W-factor)</div>
                <div style="font-family:'Courier New',monospace;font-size:0.9rem;color:#2c3e50;margin-bottom:6px">
                    t<sub>req</sub> = (P &times; OD) / [2 &times; (S &times; E &times; W + P &times; Y)] &nbsp;+&nbsp; c
                </div>
                <div style="color:#555;font-size:0.83rem">
                    <strong>NPS 6" example:</strong>
                    &nbsp; P = ${P} psig &nbsp;|&nbsp;
                    OD = ${typeof OD === 'number' ? OD.toFixed(3) : OD}" &nbsp;|&nbsp;
                    S(T) = ${S.toLocaleString()} psi &nbsp;|&nbsp;
                    E = ${E} &nbsp;|&nbsp;
                    W = ${W} <em style="color:#888">(${wBasis})</em> &nbsp;|&nbsp;
                    Y = ${Y} <em style="color:#888">(${yBasis})</em> &nbsp;|&nbsp;
                    c = ${c}"
                    &nbsp; &rarr; &nbsp; t<sub>calc</sub> = <strong>${tCalc}"</strong>
                </div>
                <div style="margin-top:8px;color:#555;font-size:0.8rem">
                    &bull; t<sub>min</sub> = (t<sub>req</sub> + c) / (1 &minus; ${di.mill_tolerance_pct}%)
                    &nbsp;|&nbsp;
                    &bull; MAWP = [2&times;S&times;E&times;W&times;t<sub>eff</sub>] / [OD &minus; 2&times;Y&times;t<sub>eff</sub>]
                    &nbsp;|&nbsp;
                    &bull; t<sub>eff</sub> = WT<sub>nom</sub> &times; (1 &minus; mill%) &minus; c &minus; mech
                </div>
            </div>

            ${svcLine}

            <!-- Design Inputs Summary -->
            <div class="summary-grid" style="margin-bottom:15px">
                <div class="summary-panel">
                    <h4>Design Parameters</h4>
                    <div class="summary-row"><span class="label">PMS Class</span><span class="value"><strong>${pmsCode}</strong> (${di.pressure_rating_label || di.pressure_class + '#'})</span></div>
                    <div class="summary-row"><span class="label">Design Pressure (P)</span><span class="value">${di.design_pressure_psig} psig (${di.design_pressure_barg} barg)</span></div>
                    <div class="summary-row"><span class="label">Design Temperature</span><span class="value">${di.design_temp_f}&deg;F (${di.design_temp_c}&deg;C)</span></div>
                    <div class="summary-row"><span class="label">Material Grade</span><span class="value">${di.material_grade}</span></div>
                    <div class="summary-row"><span class="label">Material Spec</span><span class="value">${di.material_spec}</span></div>
                    <div class="summary-row"><span class="label">Allowable Stress S(T)</span><span class="value">${di.allowable_stress_psi.toLocaleString()} psi (${di.allowable_stress_mpa} MPa)</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Fabrication &amp; Code Factors</h4>
                    <div class="summary-row"><span class="label">Pipe Standard</span><span class="value">${di.pipe_standard}</span></div>
                    <div class="summary-row"><span class="label">Joint Type</span><span class="value">${di.joint_type}</span></div>
                    <div class="summary-row"><span class="label">Joint Efficiency (E)</span><span class="value">${di.joint_efficiency}</span></div>
                    <div class="summary-row"><span class="label">Y Coefficient</span><span class="value">${di.y_factor} <em style="color:#888;font-size:0.8rem">(${yBasis})</em></span></div>
                    <div class="summary-row"><span class="label">W-factor (Weld Str.)</span><span class="value">${W} <em style="color:#888;font-size:0.8rem">(${wBasis})</em></span></div>
                    <div class="summary-row"><span class="label">Corrosion Allow. (c)</span><span class="value">${di.ca_mm} mm</span></div>
                    <div class="summary-row"><span class="label">Mill Undertolerance</span><span class="value">${di.mill_tolerance_pct}%</span></div>
                </div>
            </div>

            ${flagsSection}

            <!-- Main Schedule Table -->
            <div style="overflow-x:auto">
                <table class="result-table" style="font-size:0.8rem;white-space:nowrap">
                    <thead>
                        <tr style="background:#1a5276;color:#fff">
                            <th>NPS (in)</th>
                            <th>OD (mm)</th>
                            <th>Schedule / Tags</th>
                            <th>WT nom (mm)</th>
                            <th>t<sub>req</sub> (mm)</th>
                            <th>t<sub>min</sub> (mm)</th>
                            <th>t<sub>eff</sub> (mm)</th>
                            <th>MAWP (barg)</th>
                            <th>Margin</th>
                            <th>Util.</th>
                            <th>Governs</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>${tableRows}</tbody>
                </table>
            </div>

            <!-- Summary Statistics -->
            <div class="summary-grid" style="margin-top:15px">
                <div class="summary-panel" style="background:#e8f8f0">
                    <h4>Summary Statistics</h4>
                    <div class="summary-row"><span class="label">Min MAWP</span><span class="value">${sm.min_mawp_barg} barg</span></div>
                    <div class="summary-row"><span class="label">Max MAWP</span><span class="value">${sm.max_mawp_barg} barg</span></div>
                    <div class="summary-row"><span class="label">Min Pressure Margin</span><span class="value">${sm.min_margin_pct}%</span></div>
                    <div class="summary-row"><span class="label">Hydrotest Pressure (1.5&times;P)</span><span class="value"><strong>${sm.hydro_test_barg} barg</strong></span></div>
                    <div class="summary-row"><span class="label">Total NPS Sizes</span><span class="value">${sm.total_sizes}</span></div>
                    ${sm.fail_count > 0 ? `<div class="summary-row" style="color:#c0392b"><span class="label">FAIL Count</span><span class="value"><strong>${sm.fail_count}</strong></span></div>` : ''}
                </div>
                <div class="summary-panel">
                    <h4>Tag Legend</h4>
                    <div style="font-size:0.83rem;line-height:1.9;color:#555">
                        <span style="font-size:0.75rem;font-weight:700;color:#fff;background:#922b21;padding:1px 6px;border-radius:8px">NACE</span>&nbsp; NACE MR0175 / ISO 15156 minimum schedule governs<br>
                        <span style="font-size:0.75rem;font-weight:700;color:#fff;background:#1a5276;padding:1px 6px;border-radius:8px">LTCS</span>&nbsp; Low-temperature service minimum governs<br>
                        <span style="font-size:0.75rem;font-weight:700;color:#fff;background:#7d6608;padding:1px 6px;border-radius:8px">H₂↑</span>&nbsp; Hydrogen service — one schedule heavier (conservative)<br>
                        <span style="font-size:0.75rem;font-weight:700;color:#fff;background:#1e8449;padding:1px 6px;border-radius:8px">Pressure</span>&nbsp; ASME B31.3 Eq. 3a governs<br>
                        <span style="font-size:0.75rem;font-weight:700;color:#fff;background:#c0392b;padding:1px 6px;border-radius:8px">FAIL</span>&nbsp; No standard schedule satisfies t<sub>min</sub>
                    </div>
                </div>
            </div>
        `;
    },

    // -- Step 4: Fittings ---------------------------------------------
    async calcFittings() {
        this.showLoading('Assigning fittings materials...');
        try {
            const body = (nps) => JSON.stringify({
                material_grade: this.data.msr.material_grade,
                pipe_size: nps,
                schedule: this.data.schedule.selected_schedule,
                material_type: this.data.msr.material_type,
            });
            const opts = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
            const [sbRes, lbRes] = await Promise.all([
                fetch('/api/assign_fittings', { ...opts, body: body('1.5') }),
                fetch('/api/assign_fittings', { ...opts, body: body('6') }),
            ]);
            this.data.fittings = {
                small_bore: await sbRes.json(),
                large_bore: await lbRes.json(),
            };
            this.renderFittings();
            // Fetch and render the branch table for the selected material
            this.fetchBranchTable();
        } catch (e) {
            console.error(e);
            this.showToast('Fittings assignment failed.', 'error');
        }
        this.hideLoading();
    },

    async fetchBranchTable() {
        try {
            const matType = this.data.msr.material_type || 'CS';
            const res = await fetch('/api/branch_table', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ material_type: matType }),
            });
            const chart = await res.json();
            if (chart.error) {
                console.warn('Branch table:', chart.error);
                return;
            }
            this.data.branch_chart = chart;
            this.renderBranchTable(chart);
        } catch (e) {
            console.error('Branch table fetch failed:', e);
        }
    },

    renderBranchTable(chart) {
        const section = document.getElementById('branch-table-section');
        if (!section) return;
        section.style.display = 'block';

        // Title
        document.getElementById('branch-chart-title').textContent = chart.title + ' — Branch Table as per API RP 14E';

        // Legend
        const legendEl = document.getElementById('branch-legend');
        const legendParts = Object.entries(chart.legend).map(([code, name]) => {
            const colors = { W: '#2c3e50', T: '#1a6b3c', H: '#8b4513', S: '#6c3483', RT: '#d4a017', '-': '#999' };
            const bg = { W: '#eaf2f8', T: '#e8f8f0', H: '#fdf2e9', S: '#f4ecf7', RT: '#fef9e7', '-': '#f0f0f0' };
            return `<span style="display:inline-block;margin:2px 10px 2px 0;padding:3px 10px;border-radius:4px;background:${bg[code]||'#f0f0f0'};border:1px solid ${colors[code]||'#ccc'};font-weight:600;font-size:0.85em;">
                <span style="color:${colors[code]||'#333'}">${code}</span> = ${name}</span>`;
        });
        legendEl.innerHTML = '<strong>Legend:</strong> ' + legendParts.join('');

        // Matrix table
        const branches = chart.branch_sizes;
        let html = '<table class="result-table" style="font-size:0.82em;text-align:center;border-collapse:collapse;width:auto;">';

        // Header row: Branch Pipe sizes
        html += '<thead><tr><th style="background:#1a5276;color:#fff;padding:6px 8px;position:sticky;left:0;z-index:2;">Run \\ Branch</th>';
        for (const b of branches) {
            const lbl = b <= 1 ? '\u22641' : String(b);
            html += `<th style="background:#1a5276;color:#fff;padding:6px 6px;min-width:36px;font-size:0.9em;">${lbl}</th>`;
        }
        html += '</tr></thead><tbody>';

        // Data rows
        const cellColors = { W: '#2c3e50', T: '#1a6b3c', H: '#8b4513', S: '#6c3483', RT: '#d4a017', '-': '#bbb' };
        const cellBg =     { W: '#eaf2f8', T: '#e8f8f0', H: '#fdf2e9', S: '#f4ecf7', RT: '#fef9e7', '-': '#f9f9f9' };

        for (const row of chart.rows) {
            const runLabel = row.run_nps <= 1 ? '\u22641' : String(row.run_nps);
            html += `<tr><td style="background:#f0f4f7;font-weight:700;padding:5px 8px;text-align:left;position:sticky;left:0;z-index:1;border-right:2px solid #1a5276;">${runLabel}</td>`;
            for (let i = 0; i < branches.length; i++) {
                const val = row.cells[i];
                if (val && branches[i] <= row.run_nps) {
                    const bg = cellBg[val] || '#fff';
                    const fg = cellColors[val] || '#333';
                    const isDiag = branches[i] === row.run_nps;
                    const border = isDiag ? 'border:2px solid #1a5276;' : '';
                    html += `<td style="background:${bg};color:${fg};font-weight:700;padding:4px 2px;${border}">${val}</td>`;
                } else {
                    html += '<td style="background:#f7f7f7;"></td>';
                }
            }
            html += '</tr>';
        }
        html += '</tbody></table>';

        // Labels
        html += '<div style="display:flex;justify-content:space-between;margin-top:6px;font-size:0.8em;color:#666;">';
        html += '<span>\u2191 <strong>RUN PIPE</strong></span>';
        html += '<span><strong>BRANCH PIPE</strong> \u2192</span>';
        html += '</div>';

        document.getElementById('branch-table-container').innerHTML = html;
    },

    renderFittings() {
        const buildSection = (f, label, npsRange) => {
            const items = [
                ['Pipe', f.pipe],
                ['90\u00b0 LR Elbow', f.elbow_90],
                ['45\u00b0 Elbow', f.elbow_45],
                ['Equal Tee', f.tee_equal],
                ['Reducing Tee', f.tee_reducing],
                ['Concentric Reducer', f.reducer_concentric],
                ['Eccentric Reducer', f.reducer_eccentric],
                ['Pipe Cap', f.cap],
            ];
            if (f.small_bore_fittings) {
                items.push(['Coupling (SW)', f.small_bore_fittings.coupling]);
                items.push(['Half-Coupling (SW)', f.small_bore_fittings.half_coupling]);
            }
            const rows = items.map(([name, d]) => `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td>${d?.material || 'N/A'}</td>
                    <td>${d?.schedule || d?.standard || ''}</td>
                    <td>${d?.standard || 'ASTM'}</td>
                </tr>`).join('');
            const branch = f.branch_connections || {};
            const branchRows = Object.entries(branch).map(([k, v]) =>
                `<tr><td>${k.replace(/_/g, ' ')}</td><td colspan="3">${v}</td></tr>`).join('');
            return `
                <h4 style="margin:18px 0 8px;color:#1a5276;border-bottom:2px solid #1a5276;padding-bottom:4px">
                    ${label} <small style="color:#666;font-weight:normal">(NPS ${npsRange})</small>
                </h4>
                <div class="info-box" style="margin-bottom:8px">
                    <strong>Connection:</strong> ${f.pipe?.connection || 'Butt Weld'} &nbsp;|&nbsp;
                    <strong>Schedule:</strong> ${f.pipe?.schedule || ''}
                </div>
                <table class="result-table">
                    <thead><tr><th>Component</th><th>Material</th><th>Schedule/Class</th><th>Standard</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
                <h5 style="margin:12px 0 4px;color:#555">Branch Connection Guide</h5>
                <table class="result-table">
                    <thead><tr><th>Size Difference</th><th colspan="3">Connection Type</th></tr></thead>
                    <tbody>${branchRows}</tbody>
                </table>`;
        };

        const sb = this.data.fittings.small_bore;
        const lb = this.data.fittings.large_bore;
        document.getElementById('fittings-result').innerHTML =
            buildSection(sb, 'Small Bore', '\u00bd\u2033 \u2013 2\u2033') +
            buildSection(lb, 'Large Bore', '2\u00bd\u2033 \u2013 36\u2033');
    },

    // -- Step 6: Flanges + Valves ------------------------------------
    async calcFlanges() {
        this.showLoading('Selecting flanges, gaskets, bolting & valves...');
        try {
            // Get the spec code pressure class (Part 1) — this is the authoritative class
            const part1 = document.getElementById('pms-part1').value;
            const part1Info = this._pmsRefData?.part1_options?.[part1];
            const specPressureClass = part1Info?.pressure_psig || 150;  // e.g. 150 for "A"

            // Guard: ensure design_pressure_psig is a valid positive number
            const dp = parseFloat(this.data.line_list?.design_pressure_psig) || 1;
            const dt = parseFloat(this.data.line_list?.design_temp_f) || 70;

            let res = await fetch('/api/select_flanges', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    material_grade: this.data.msr.material_grade || 'A106 Gr.B',
                    material_type: this.data.msr.material_type || 'CS',
                    // Use spec code class max pressure at ambient (not design temp)
                    // to ensure the auto-selected class matches the spec code Part 1
                    design_pressure: dp,
                    design_temp: dt,
                }),
            });
            this.data.flanges = await res.json();

            // Force flange class to match spec code Part 1 — the spec code defines
            // the pressure class, it should NOT be re-derived from auto-selection
            if (this.data.flanges && this.data.flanges.flange) {
                this.data.flanges.flange.class = specPressureClass;
                // Update face type based on the correct spec code class
                if (specPressureClass <= 600) {
                    this.data.flanges.flange.face_type = 'Raised Face (RF)';
                    this.data.flanges.flange.face_finish = '125-250 AARH';
                } else {
                    this.data.flanges.flange.face_type = 'Ring Type Joint (RTJ)';
                    this.data.flanges.flange.face_finish = 'Per ASME B16.5';
                }
            }

            const valveOpts = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
            const valveBody = (nps) => JSON.stringify({
                material_type: this.data.msr.material_type,
                flange_class: this.data.flanges.flange.class,
                pipe_size: nps,
                spec_code: this.data.spec_code.spec_code,
                line_number: this.data.line_list.line_number || '',
            });
            const [sbValves, lbValves] = await Promise.all([
                fetch('/api/select_valves', { ...valveOpts, body: valveBody('1.5') }),
                fetch('/api/select_valves', { ...valveOpts, body: valveBody('6') }),
            ]);
            this.data.valves = {
                small_bore: await sbValves.json(),
                large_bore: await lbValves.json(),
            };

            this.renderFlangesAndValves();
        } catch (e) {
            console.error(e);
            this.showToast('Flanges/valves selection failed.', 'error');
        }
        this.hideLoading();
    },

    renderFlangesAndValves() {
        const fl = this.data.flanges.flange || {};
        const gk = this.data.flanges.gasket || {};
        const bl = this.data.flanges.bolting || {};

        const buildValveSection = (vData, label, npsRange) => {
            if (!vData) return '';
            const valves = vData.valves || {};
            const cards = Object.entries(valves).map(([vtype, v]) => `
                <div class="valve-card selected">
                    <h4>${vtype} Valve</h4>
                    <div class="detail"><strong>Trim:</strong> ${v.trim}</div>
                    <div class="detail"><strong>Seat:</strong> ${v.seat}</div>
                    <div class="detail"><strong>End:</strong> ${v.end_connection}</div>
                    <div class="vds-tag">${v.vds_tag}</div>
                </div>`).join('');
            return `
                <h4 style="margin:16px 0 6px;color:#1a5276;border-bottom:2px solid #1a5276;padding-bottom:4px">
                    ${label} <small style="color:#666;font-weight:normal">(NPS ${npsRange})</small>
                </h4>
                <div class="info-box" style="margin-bottom:8px">
                    <strong>End Connection:</strong> ${vData.end_connection} &nbsp;|&nbsp;
                    <strong>Pressure Class:</strong> #${vData.pressure_class}
                </div>
                <div class="valve-grid">${cards}</div>`;
        };

        document.getElementById('flanges-result').innerHTML = `
            <div class="summary-grid">
                <div class="summary-panel">
                    <h4>Flanges (ASME B16.5)</h4>
                    <div class="summary-row"><span class="label">Pressure Class</span><span class="value" style="font-size:1.2rem;color:#1a5276">#${fl.class}</span></div>
                    <div class="summary-row"><span class="label">Material</span><span class="value">${fl.material}</span></div>
                    <div class="summary-row"><span class="label">Types</span><span class="value">${fl.types}</span></div>
                    <div class="summary-row"><span class="label">Face Type</span><span class="value">${fl.face_type}</span></div>
                    <div class="summary-row"><span class="label">Face Finish</span><span class="value">${fl.face_finish}</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Gasket (ASME B16.20)</h4>
                    <div class="summary-row"><span class="label">Type</span><span class="value">${gk.type}</span></div>
                    <div class="summary-row"><span class="label">Material</span><span class="value">${gk.material}</span></div>
                    <div class="summary-row"><span class="label">Inner Ring</span><span class="value">${gk.inner_ring}</span></div>
                    <div class="summary-row"><span class="label">Filler</span><span class="value">${gk.filler}</span></div>
                </div>
            </div>
            <div class="summary-panel" style="margin-top:15px">
                <h4>Bolting</h4>
                <div class="summary-grid">
                    <div>
                        <div class="summary-row"><span class="label">Stud Bolt</span><span class="value">${bl.stud_bolt}</span></div>
                        <div class="summary-row"><span class="label">Nut</span><span class="value">${bl.nut}</span></div>
                    </div>
                    <div>
                        <div class="summary-row"><span class="label">Temp Range</span><span class="value">${bl.temp_range}</span></div>
                        <div class="summary-row"><span class="label">Standard</span><span class="value">${bl.standard}</span></div>
                    </div>
                </div>
            </div>
            <h3 style="margin-top:25px;color:#1a5276">Valve Selection</h3>
            ${buildValveSection(this.data.valves.small_bore, 'Small Bore', '\u00bd\u2033 \u2013 2\u2033')}
            ${buildValveSection(this.data.valves.large_bore, 'Large Bore', '2\u00bd\u2033 \u2013 36\u2033')}
        `;
    },

    // -- Step 7: Review & Validate ------------------------------------
    async runReviewAndValidation() {
        this.showLoading('Running engineering validation...');
        try {
            this.renderReviewSummary();

            const pmsData = {
                msr: this.data.msr,
                spec_code: this.data.spec_code,
                line_list: this.data.line_list,
                thickness: this.data.thickness,
                schedule: this.data.schedule,
                fittings: this.data.fittings,
                flanges: this.data.flanges,
                valves: this.data.valves,
                service: {
                    service_description: this.data.msr?.fluid_service || '',
                    design_pressure: this.data.line_list?.design_pressure_barg || null,
                    design_temperature: this.data.line_list?.design_temp_c || null,
                },
            };

            const res = await fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pmsData),
            });
            this.data.validation = await res.json();
            this.renderValidationResults();
        } catch (e) {
            console.error(e);
            this.showToast('Validation request failed.', 'error');
        }
        this.hideLoading();
    },

    renderReviewSummary() {
        const msr = this.data.msr;
        const sc = this.data.spec_code;
        const ll = this.data.line_list;
        const th = this.data.thickness;
        const sch = this.data.schedule;
        const fl = this.data.flanges;

        document.getElementById('review-summary').innerHTML = `
            <div class="summary-grid">
                <div class="summary-panel">
                    <h4>Material & Spec</h4>
                    <div class="summary-row"><span class="label">Material Type</span><span class="value">${msr.pms_material_type || msr.material_type}</span></div>
                    <div class="summary-row"><span class="label">Material Grade</span><span class="value">${msr.material_grade} (${msr.material_type})</span></div>
                    <div class="summary-row"><span class="label">PMS Code</span><span class="value" style="font-size:1.1rem;color:#1a5276">${sc.spec_code}</span></div>
                    <div class="summary-row"><span class="label">Corrosion Allowance</span><span class="value">${msr.corrosion_allowance_mm} mm</span></div>
                    <div class="summary-row"><span class="label">Service</span><span class="value">${msr.fluid_service || ll.fluid || 'N/A'}</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Design Conditions</h4>
                    <div class="summary-row"><span class="label">Design Pressure</span><span class="value">${ll.design_pressure_psig} psig</span></div>
                    <div class="summary-row"><span class="label">Design Temperature</span><span class="value">${ll.design_temp_f}\u00b0F</span></div>
                    <div class="summary-row"><span class="label">Fluid</span><span class="value">${ll.fluid}</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Pipe & Schedule</h4>
                    <div class="summary-row"><span class="label">Schedule</span><span class="value">${sch.selected_schedule}</span></div>
                    <div class="summary-row"><span class="label">Wall Thickness</span><span class="value">${sch.selected_wall_thickness_in} in</span></div>
                    <div class="summary-row"><span class="label">Min Required</span><span class="value">${th.t_nominal_min_in} in</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Flanges & Gasket</h4>
                    <div class="summary-row"><span class="label">Flange Class</span><span class="value">#${fl.flange?.class}</span></div>
                    <div class="summary-row"><span class="label">Material</span><span class="value">${fl.flange?.material}</span></div>
                    <div class="summary-row"><span class="label">Gasket</span><span class="value">${fl.gasket?.type}</span></div>
                </div>
                <div class="summary-panel">
                    <h4>Operating Conditions</h4>
                    <div class="summary-row"><span class="label">Operating Pressure</span><span class="value">${ll.operating_pressure_psig || 0} psig</span></div>
                    <div class="summary-row"><span class="label">Operating Temperature</span><span class="value">${ll.operating_temp_f || 0} &deg;F</span></div>
                    <div class="summary-row"><span class="label">LDMT</span><span class="value">${ll.mdmt_f}&deg;F (${ll.mdmt_c}&deg;C)</span></div>
                </div>
            </div>
        `;
    },

    renderValidationResults() {
        const results = this.data.validation;
        const listEl = document.querySelector('#validation-results .validation-list');
        if (!listEl) return;

        const allPassed = results.every(r => r.valid);

        let html = results.map(r => {
            let cls = 'pass';
            let icon = '\u2713';
            if (!r.valid && r.severity === 'error') { cls = 'fail'; icon = '\u2717'; }
            else if (!r.valid && r.severity === 'warning') { cls = 'warn'; icon = '!'; }
            return `
                <div class="validation-item ${cls}">
                    <span class="validation-icon">${icon}</span>
                    <div class="validation-detail">
                        <strong>${r.rule}</strong>
                        <p>${r.message}</p>
                    </div>
                </div>
            `;
        }).join('');

        if (allPassed) {
            html += `<div class="info-box success" style="margin-top:15px">
                <strong>All validation checks passed.</strong> You may proceed to generate the final PMS document.
            </div>`;
            this.showToast('All validation checks passed!', 'success');
        } else {
            html += `<div class="info-box" style="margin-top:15px;border-color:#e74c3c;background:#fdf2f2">
                <strong>Some checks did not pass.</strong> Review the warnings/errors above. You may still proceed, but consider revising inputs.
            </div>`;
            this.showToast('Validation found issues. Review before proceeding.', 'warning');
        }

        listEl.innerHTML = html;
    },

    // -- Step 8: Generate Final PMS -----------------------------------
    async generateFinalPMS() {
        this.data.metadata = {
            project: document.getElementById('project-name')?.value || 'PMS Project',
            doc_number: document.getElementById('doc-number')?.value || 'PMS-001',
            revision: document.getElementById('revision')?.value || '0',
            date: new Date().toISOString().split('T')[0],
        };

        this.renderPMSPreview();
    },

    renderPMSPreview() {
        const m = this.data.metadata;
        const msr = this.data.msr;
        const sc = this.data.spec_code;
        const ll = this.data.line_list;
        const th = this.data.thickness;
        const sch = this.data.schedule;
        const ft = this.data.fittings;
        const fl = this.data.flanges;
        const vl = this.data.valves;

        // Fittings: large bore is the primary reference for the PMS table
        const lb = ft.large_bore || {};
        const sb = ft.small_bore || {};
        const fittingItems = [
            ['Pipe',                lb.pipe],
            ['90\u00b0 LR Elbow',  lb.elbow_90],
            ['45\u00b0 Elbow',     lb.elbow_45],
            ['Equal Tee',          lb.tee_equal],
            ['Reducing Tee',       lb.tee_reducing],
            ['Concentric Reducer', lb.reducer_concentric],
            ['Eccentric Reducer',  lb.reducer_eccentric],
            ['Pipe Cap',           lb.cap],
        ];
        if (sb.small_bore_fittings) {
            const toObj = v => typeof v === 'string' ? { material: v, standard: 'ASME B16.11' } : v;
            fittingItems.push(['Coupling (SW \u00bd\u2033\u20132\u2033)',      toObj(sb.small_bore_fittings.coupling)]);
            fittingItems.push(['Half-Coupling (SW \u00bd\u2033\u20132\u2033)', toObj(sb.small_bore_fittings.half_coupling)]);
        }
        const fittingRows = fittingItems.map(([n, d]) =>
            `<tr><td>${n}</td><td>${d?.material || 'N/A'}</td><td>${d?.standard || 'ASTM'}</td></tr>`
        ).join('');

        // Valves: merge small bore (SW/NPT) and large bore (Flanged) with label
        const sbValves = vl.small_bore?.valves || {};
        const lbValves = vl.large_bore?.valves || {};
        const allValveTypes = new Set([...Object.keys(sbValves), ...Object.keys(lbValves)]);
        const valveRows = [...allValveTypes].map(vt => {
            const sv = sbValves[vt]; const lv = lbValves[vt];
            if (sv && lv && sv.vds_tag !== lv.vds_tag) {
                return `<tr>
                    <td>${vt}</td><td>${lv.trim}</td><td>${lv.seat}</td>
                    <td><code>${sv.vds_tag}</code> <small style="color:#888">(½\u2033\u20132\u2033)</small><br>
                        <code>${lv.vds_tag}</code> <small style="color:#888">(2½\u2033\u201336\u2033)</small></td>
                </tr>`;
            }
            const v = lv || sv;
            return `<tr><td>${vt}</td><td>${v.trim}</td><td>${v.seat}</td><td><code>${v.vds_tag}</code></td></tr>`;
        }).join('');

        document.getElementById('pms-preview').innerHTML = `
            <div class="pms-preview">
                <div class="pms-header">
                    <h2>PIPING MATERIAL SPECIFICATION</h2>
                    <p>${m.project} | ${m.doc_number} | Rev. ${m.revision} | ${m.date}</p>
                    <p style="margin-top:5px;font-size:1.1rem"><strong>Spec Code: ${sc.spec_code} (${sc.pms_reference})</strong></p>
                </div>

                <div class="pms-section">
                    <div class="pms-section-title">1. General Information</div>
                    <table class="pms-table">
                        <tr><td>Material Type</td><td>${msr.pms_material_type || msr.material_type}</td></tr>
                        <tr><td>Base Material Grade</td><td>${msr.material_grade}</td></tr>
                        <tr><td>Specification</td><td>${msr.material_spec}</td></tr>
                        <tr><td>Corrosion Allowance</td><td>${msr.corrosion_allowance_mm} mm (${msr.corrosion_allowance_in} in)</td></tr>
                        <tr><td>Service / Fluid</td><td>${msr.fluid_service || ll.fluid || 'N/A'}</td></tr>
                    </table>
                </div>

                <div class="pms-section">
                    <div class="pms-section-title">2. Design Conditions</div>
                    <table class="pms-table">
                        <tr><td>Size Range</td><td>NPS \u00bd\u2033 \u2013 36\u2033 (all sizes)</td></tr>
                        <tr><td>Design Pressure</td><td>${ll.design_pressure_psig} psig (${ll.design_pressure_bar} bar)</td></tr>
                        <tr><td>Test Pressure</td><td>${ll.test_pressure_psig} psig</td></tr>
                        <tr><td>Design Temperature</td><td>${ll.design_temp_f}\u00b0F (${ll.design_temp_c}\u00b0C)</td></tr>
                        <tr><td>Operating Pressure</td><td>${ll.operating_pressure_psig} psig</td></tr>
                        <tr><td>Operating Temperature</td><td>${ll.operating_temp_f}\u00b0F</td></tr>
                        <tr><td>LDMT</td><td>${ll.mdmt_f}\u00b0F (${ll.mdmt_c}\u00b0C)</td></tr>
                    </table>
                </div>

                <div class="pms-section">
                    <div class="pms-section-title">3. Pipe Wall Thickness & Schedule</div>
                    <table class="pms-table">
                        <tr><td>Code</td><td>ASME B31.3</td></tr>
                        <tr><td>Allowable Stress</td><td>${th.allowable_stress_psi?.toLocaleString()} psi @ ${th.design_temp_f}\u00b0F</td></tr>
                        <tr><td>Joint Efficiency</td><td>${th.joint_efficiency} (${th.joint_type})</td></tr>
                        <tr><td>Calc. Thickness</td><td>${th.t_calculated_in} in</td></tr>
                        <tr><td>Min Required (with CA)</td><td>${th.t_min_required_in} in</td></tr>
                        <tr><td>Schedule Standard</td><td>${sch.standard}</td></tr>
                        <tr><td>Selected Schedule</td><td><strong>${sch.selected_schedule}</strong></td></tr>
                        <tr><td>Wall Thickness</td><td>${sch.selected_wall_thickness_in} in (${sch.selected_wall_thickness_mm} mm)</td></tr>
                        <tr><td>Pipe OD / ID (NPS 6" ref)</td><td>${th.pipe_od_in} in / ${th.id_in} in</td></tr>
                    </table>
                </div>

                <div class="pms-section">
                    <div class="pms-section-title">4. Pipe & Fittings</div>
                    <table class="result-table">
                        <thead><tr><th>Component</th><th>Material</th><th>Standard</th></tr></thead>
                        <tbody>${fittingRows}</tbody>
                    </table>
                </div>

                <div class="pms-section">
                    <div class="pms-section-title">5. Flanges, Gaskets & Bolting</div>
                    <table class="pms-table">
                        <tr><td colspan="2" style="color:#1a5276;font-weight:700;background:#f0f7ff">FLANGES</td></tr>
                        <tr><td>Pressure Class</td><td>#${fl.flange?.class}</td></tr>
                        <tr><td>Material</td><td>${fl.flange?.material}</td></tr>
                        <tr><td>Types</td><td>${fl.flange?.types}</td></tr>
                        <tr><td>Face Type</td><td>${fl.flange?.face_type}</td></tr>
                        <tr><td colspan="2" style="color:#1a5276;font-weight:700;background:#f0f7ff">GASKET</td></tr>
                        <tr><td>Type / Material</td><td>${fl.gasket?.type} - ${fl.gasket?.material}</td></tr>
                        <tr><td>Standard</td><td>${fl.gasket?.standard}</td></tr>
                        <tr><td colspan="2" style="color:#1a5276;font-weight:700;background:#f0f7ff">BOLTING</td></tr>
                        <tr><td>Stud Bolt</td><td>${fl.bolting?.stud_bolt}</td></tr>
                        <tr><td>Nut</td><td>${fl.bolting?.nut}</td></tr>
                        <tr><td>Temp Range</td><td>${fl.bolting?.temp_range}</td></tr>
                    </table>
                </div>

                <div class="pms-section">
                    <div class="pms-section-title">6. Valves</div>
                    <table class="result-table">
                        <thead><tr><th>Type</th><th>Trim</th><th>Seat</th><th>VDS Tag</th></tr></thead>
                        <tbody>${valveRows}</tbody>
                    </table>
                    <div style="margin-top:8px;font-size:0.85rem;color:#7f8c8d">
                        ½\u2033\u20132\u2033: ${vl.small_bore?.end_connection || 'Socket Weld / NPT'} &nbsp;|&nbsp;
                        2½\u2033\u201336\u2033: ${vl.large_bore?.end_connection || 'Flanged RF'} &nbsp;|&nbsp;
                        Pressure Class: #${vl.large_bore?.pressure_class || vl.small_bore?.pressure_class || ''}
                    </div>
                </div>
            </div>
        `;
    },

    // -- Download Excel -----------------------------------------------
    async downloadExcel() {
        this.showLoading('Generating Excel PMS document...');
        try {
            const pmsData = {
                metadata: this.data.metadata,
                msr: this.data.msr,
                spec_code: this.data.spec_code,
                line_list: this.data.line_list,
                thickness: this.data.thickness,
                schedule: this.data.schedule,
                fittings: this.data.fittings,
                flanges: this.data.flanges,
                valves: this.data.valves,
                // Include actual design conditions for DB storage
                service: {
                    service_description: this.data.msr?.fluid_service || '',
                    design_pressure: this.data.line_list?.design_pressure_barg || null,
                    design_temperature: this.data.line_list?.design_temp_c || null,
                },
            };

            // DEBUG: log what schedule_rows are being sent to Excel generator
            console.log('[Excel] schedule_rows being sent:');
            (pmsData.schedule?.schedule_rows || []).forEach(r => {
                console.log(`  NPS ${r.nps}: Sch=${r.schedule}, WT=${r.wt_mm}mm`);
            });
            const res = await fetch('/api/generate_pms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pmsData),
            });
            const result = await res.json();

            if (result.success && result.filename) {
                window.location.href = `/api/download/${result.filename}`;
                document.getElementById('download-status').innerHTML = `
                    <div class="info-box success" style="margin-top:15px">
                        <strong>Download started!</strong> File: ${result.filename}
                    </div>
                `;
                this.showToast('Excel PMS document generated successfully!', 'success');
            } else {
                const errMsg = result.error || 'Unknown error';
                document.getElementById('download-status').innerHTML = `
                    <div class="info-box" style="margin-top:15px;border-color:#c0392b;background:#fdecea">
                        <strong>Generation failed:</strong> ${errMsg}
                    </div>`;
                this.showToast(`Excel generation failed: ${errMsg}`, 'error');
            }
        } catch (e) {
            console.error(e);
            this.showToast(`Error generating Excel file: ${e.message}`, 'error');
        }
        this.hideLoading();
    },

    // -- Loading -------------------------------------------------------
    showLoading(text) {
        const overlay = document.getElementById('loading-overlay');
        overlay.querySelector('.loading-text').textContent = text || 'Processing...';
        overlay.classList.add('show');
    },

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    },

    // -- Auto-fill Test Pressure (Hydro = 1.5 * max allowable pressure) --
    updateTestPressure() {
        const maxP = this._maxAllowablePressure;
        if (maxP) {
            document.getElementById('test-pressure').value = (maxP * 1.5).toFixed(1);
        } else {
            // Fallback to 1.5 * design pressure if P-T data not loaded yet
            const dp = parseFloat(document.getElementById('design-pressure').value);
            if (!isNaN(dp)) {
                document.getElementById('test-pressure').value = (dp * 1.5).toFixed(1);
            }
        }
    },
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => App.init());
