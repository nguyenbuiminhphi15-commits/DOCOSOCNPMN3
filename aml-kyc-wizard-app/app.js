/**
 * AEGIS SECURE BANKING - AML/KYC SYSTEM JS LOGIC
 * State Management, Wizard Navigation, Liveness Check, Document Auto-suggestions, and AML Risk Scoring Simulation.
 */

// ==========================================================================
// 1. APPLICATION STATE
// ==========================================================================
const appState = {
    // Current layout step ID
    currentStep: 'register-step1',
    
    // User profile details (Updated during Part 1)
    user: {
        fullname: '',
        email: '',
        phone: '',
        dob: '',
        doctype: 'cccd_chip',
        nationality: 'Việt Nam',
        permanentAddress: '',
        currentAddress: '',
        isKycVerified: false,
        isLoggedIn: false,
        
        // Risk EDD info
        occupation: '',
        company: '',
        income: '',
        isPep: 'no'
    },
    
    // Transaction Details (Updated during Part 2 & 3)
    transaction: {
        senderAccount: 'acct_1',
        receiverName: '',
        receiverAccount: '',
        receiverBank: '',
        receiverBranch: '',
        receiverCountry: 'VN',
        swiftCode: '',
        receiverAddress: '',
        amount: 0,
        currency: 'VND',
        relationship: '',
        purpose: '',
        sourceOfFunds: '',
        description: '',
        uploadedFiles: [],
        docNotes: '',
        otpVerified: false,
        biometricVerified: false,
        riskScore: 0,
        triggeredRules: [],
        status: 'Pending' // Pending, Approved, Review
    },

    // UI Configuration
    constants: {
        CTR_THRESHOLD_VND: 400000000, // 400 Million VND threshold
        EXCHANGE_RATES: {
            VND: 1,
            USD: 25000,
            EUR: 27000,
            KRW: 18.5,
            JPY: 160,
            MYR: 5300
        }
    }
};

// Document requirements dictionary based on transaction purpose
const documentRequirements = {
    study: [
        "Giấy thông báo học phí chính thức (Tuition Fee Invoice) kèm thông tin tài khoản thụ hưởng của nhà trường.",
        "Visa du học (Study Permit) hoặc thư mời nhập học bản gốc.",
        "CCCD của thân nhân gửi tiền chứng minh quan hệ nhân thân (nếu chuyển thay)."
    ],
    medical: [
        "Giấy tiếp nhận khám chữa bệnh của bệnh viện nước ngoài hoặc hóa đơn ước tính chi phí y tế.",
        "Hồ sơ bệnh án bản dịch thuật công chứng (nếu có).",
        "Quyết định cử đi chữa bệnh (nếu chuyển bằng nguồn ngân sách công ty)."
    ],
    family_support: [
        "Giấy tờ chứng minh quan hệ thân nhân (Giấy khai sinh, Sổ hộ khẩu cũ có tên người nhận, Đăng ký kết hôn...).",
        "Giấy xác nhận cư trú hợp pháp của thân nhân ở nước ngoài (Visa cư trú, Thẻ định cư xanh, Hộ chiếu nước ngoài).",
        "Cam kết dòng tiền trích từ thu nhập hợp pháp tại Việt Nam."
    ],
    investment: [
        "Giấy phép phê duyệt đầu tư ra nước ngoài do Bộ Kế hoạch và Đầu tư cấp.",
        "Hợp đồng mua bán cổ phần hoặc tài liệu chứng minh quyền góp vốn ngoại.",
        "Báo cáo kiểm toán chứng minh năng lực tài chính nguồn tiền chuyển."
    ],
    real_estate: [
        "Hợp đồng chuyển nhượng/Mua bán bất động sản có công chứng dịch thuật.",
        "Hồ sơ sở hữu đất đai/Giấy phép quy hoạch của chính quyền sở tại.",
        "Chứng từ thuế phát sinh liên quan đến bất động sản đó."
    ],
    commerce: [
        "Hợp đồng thương mại mua bán hàng hóa đã ký giữa 2 bên (Commercial Contract).",
        "Hóa đơn yêu cầu thanh toán (Commercial Invoice).",
        "Tờ khai hải quan thông quan xuất/nhập khẩu (Customs Declaration) nếu hàng đã giao."
    ],
    savings: [
        "Đơn đề nghị mở tài khoản tiết kiệm ngoại tệ đứng tên người chuyển.",
        "Giấy xác nhận nguồn tiền tích lũy hợp pháp từ lương hoặc thu nhập chịu thuế."
    ]
};

// Global variables for active media streams
let localStream = null;
let livenessTimer = null;
let otp2faCountdown = null;

// ==========================================================================
// 2. INITIALIZATION & ELEMENT SELECTORS
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
    addLog("Hệ thống AML/KYC đã khởi tạo thành công. Sẵn sàng giám sát...", "system");
});

function initApp() {
    // Reset all form inputs to default values
    document.querySelectorAll('form').forEach(form => form.reset());
    updateUserBadge();
    
    // Default: Unlock only group 1
    unlockGroup('group-auth');
    lockGroup('group-transaction');
    lockGroup('group-auth-tx');

    // Display first step
    showStep('register-step1');
}

// Write line to log console on the right
function addLog(message, type = 'info') {
    const consoleEl = document.getElementById('logs-console');
    if (!consoleEl) return;
    
    const time = new Date().toLocaleTimeString();
    const logLine = document.createElement('div');
    logLine.className = `log-line ${type}`;
    logLine.innerHTML = `<span style="color: var(--text-muted)">[${time}]</span> ${message}`;
    
    consoleEl.appendChild(logLine);
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

// Lock/Unlock stepper navigation groups
function unlockGroup(groupId) {
    const el = document.getElementById(groupId);
    if (el) el.classList.remove('locked');
}

function lockGroup(groupId) {
    const el = document.getElementById(groupId);
    if (el) el.classList.add('locked');
}

// ==========================================================================
// 3. WIZARD STEP NAVIGATION ENGINE
// ==========================================================================
const stepSequence = [
    'register-step1',
    'register-step2',
    'login-form',
    'risk-profile',
    'tx-initiation',
    'tx-purpose',
    'tx-documents',
    'tx-review',
    'tx-approval',
    'tx-status'
];

function showStep(stepId) {
    // 1. Hide all steps
    document.querySelectorAll('.wizard-step').forEach(step => {
        step.classList.remove('active');
    });

    // 2. Show target step
    const targetStepEl = document.getElementById(`step-${stepId}`);
    if (targetStepEl) {
        targetStepEl.classList.add('active');
    }

    // 3. Update stepper list highlights
    document.querySelectorAll('.step-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeNavItem = document.getElementById(`nav-${stepId}`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
        
        // Add completed states to previous steps
        let currentIdx = stepSequence.indexOf(stepId);
        for (let i = 0; i < currentIdx; i++) {
            const prevNav = document.getElementById(`nav-${stepSequence[i]}`);
            if (prevNav) prevNav.classList.add('completed');
        }
        // Remove completed state for future steps
        for (let i = currentIdx; i < stepSequence.length; i++) {
            const nextNav = document.getElementById(`nav-${stepSequence[i]}`);
            if (nextNav) nextNav.classList.remove('completed');
        }
    }

    // 4. Update section indicators in sidebar
    const currentSectionTitle = document.getElementById('current-section-title');
    if (stepId.startsWith('register') || stepId === 'login-form' || stepId === 'risk-profile') {
        currentSectionTitle.innerText = "Bảo mật & KYC";
    } else if (stepId.startsWith('tx-initiation') || stepId.startsWith('tx-purpose') || stepId.startsWith('tx-documents')) {
        currentSectionTitle.innerText = "Giao dịch lớn";
    } else {
        currentSectionTitle.innerText = "Xác nhận & Duyệt";
    }

    appState.currentStep = stepId;
    addLog(`Chuyển hướng màn hình: Trình Wizard qua bước [${stepId}]`, 'system');

    // Trigger step-specific logic
    if (stepId === 'tx-review') {
        populateReviewPage();
    }
}

// User status banner updater
function updateUserBadge() {
    const badgeName = document.querySelector('#current-user-badge .user-name');
    const badgeRole = document.querySelector('#current-user-badge .user-role');
    const avatar = document.querySelector('#current-user-badge .avatar');

    if (appState.user.isLoggedIn) {
        badgeName.innerText = appState.user.fullname || "Khách Hàng Đã Đăng Nhập";
        avatar.innerText = (appState.user.fullname || "U").charAt(0).toUpperCase();
        
        if (appState.user.isKycVerified) {
            badgeRole.innerText = `Định danh e-KYC | PEP: ${appState.user.isPep.toUpperCase()}`;
            badgeRole.style.color = "var(--primary)";
        } else {
            badgeRole.innerText = "Chờ định danh e-KYC";
            badgeRole.style.color = "var(--warning)";
        }
    } else {
        badgeName.innerText = "Khách vãng lai";
        badgeRole.innerText = "Chưa định danh (Unverified)";
        badgeRole.style.color = "var(--text-muted)";
        avatar.innerText = "U";
    }
}

// Form validation utility
function validateFormInputs(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        // Special case for hidden/custom fields or files
        if (input.type === 'file') {
            const dropzone = input.closest('.upload-dropzone');
            if (input.files.length === 0 && !input.disabled) {
                if (dropzone) dropzone.classList.add('invalid');
                isValid = false;
            } else {
                if (dropzone) dropzone.classList.remove('invalid');
            }
            return;
        }

        // Standard validation
        if (!input.checkValidity() || input.value.trim() === '') {
            input.classList.add('invalid');
            isValid = false;
        } else {
            input.classList.remove('invalid');
        }

        // Custom validation match password
        if (input.id === 'reg-confirmpassword') {
            const pass = document.getElementById('reg-password').value;
            if (input.value !== pass) {
                input.classList.add('invalid');
                isValid = false;
            }
        }
    });

    return isValid;
}

// ==========================================================================
// 4. EVENT LISTENERS
// ==========================================================================
function setupEventListeners() {
    // Theme switch toggle
    document.getElementById('checkbox-theme').addEventListener('change', (e) => {
        if (e.target.checked) {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            addLog("Chuyển sang Chế độ sáng (Light Mode)", "system");
        } else {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            addLog("Chuyển sang Chế độ tối (Dark Mode)", "system");
        }
    });

    // Reset app
    document.getElementById('btn-reset-app').addEventListener('click', () => {
        if (confirm("Bạn có chắc chắn muốn đặt lại tất cả dữ liệu giả lập về trạng thái ban đầu?")) {
            initApp();
            addLog("Đã đặt lại toàn bộ hệ thống demo.", "system");
        }
    });

    // Help modals
    document.getElementById('btn-show-guide').addEventListener('click', () => {
        document.getElementById('modal-guide').classList.remove('hidden');
    });
    document.getElementById('btn-close-guide').addEventListener('click', () => {
        document.getElementById('modal-guide').classList.add('hidden');
    });
    document.getElementById('btn-close-guide-footer').addEventListener('click', () => {
        document.getElementById('modal-guide').classList.add('hidden');
    });

    // Back buttons
    document.querySelectorAll('.btn-prev').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const prevIdx = stepSequence.indexOf(appState.currentStep) - 1;
            if (prevIdx >= 0) {
                showStep(stepSequence[prevIdx]);
            }
        });
    });

    // --- FORM 1: REGISTER STEP 1 ---
    const regForm1 = document.getElementById('form-register-step1');
    regForm1.addEventListener('submit', (e) => {
        e.preventDefault();
        if (validateFormInputs('form-register-step1')) {
            appState.user.fullname = document.getElementById('reg-fullname').value.toUpperCase();
            appState.user.email = document.getElementById('reg-email').value;
            appState.user.phone = document.getElementById('reg-phone').value;
            
            addLog(`Đăng ký cơ bản thành công: ${appState.user.fullname} | ${appState.user.email}`, 'success');
            showStep('register-step2');
        } else {
            addLog("Lỗi validation: Vui lòng kiểm tra lại các trường nhập liệu.", 'danger');
        }
    });

    // --- FORM 1: REGISTER STEP 2 (e-KYC) ---
    // Same address checkbox toggle
    document.getElementById('kyc-same-address').addEventListener('change', (e) => {
        const currentAddrGroup = document.getElementById('current-address-group');
        const currentAddrInput = document.getElementById('kyc-current-address');
        if (e.target.checked) {
            currentAddrGroup.classList.add('hidden');
            currentAddrInput.removeAttribute('required');
        } else {
            currentAddrGroup.classList.remove('hidden');
            currentAddrInput.setAttribute('required', 'required');
        }
    });

    // Drag-over Dropzones Front/Back
    setupDragDropzone('dropzone-front', 'file-front', 'preview-front');
    setupDragDropzone('dropzone-back', 'file-back', 'preview-back');

    // Liveness Camera Button
    document.getElementById('btn-start-liveness').addEventListener('click', startLivenessCheck);
    document.getElementById('file-video').addEventListener('change', handleLivenessVideoUpload);

    // Register Form 2 (e-KYC Submit)
    const regForm2 = document.getElementById('form-register-step2');
    regForm2.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = validateFormInputs('form-register-step2');

        // Check if files are uploaded
        const frontInput = document.getElementById('file-front');
        const backInput = document.getElementById('file-back');
        if (frontInput.files.length === 0) {
            document.getElementById('dropzone-front').classList.add('invalid');
            isValid = false;
        }
        if (backInput.files.length === 0) {
            document.getElementById('dropzone-back').classList.add('invalid');
            isValid = false;
        }

        // Check liveness state
        if (!appState.user.isKycVerified) {
            document.getElementById('liveness-error').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('liveness-error').style.display = 'none';
        }

        if (isValid) {
            appState.user.dob = document.getElementById('kyc-dob').value;
            appState.user.nationality = document.getElementById('kyc-nationality').value;
            appState.user.permanentAddress = document.getElementById('kyc-permanent-address').value;
            
            const sameAddr = document.getElementById('kyc-same-address').checked;
            appState.user.currentAddress = sameAddr ? appState.user.permanentAddress : document.getElementById('kyc-current-address').value;

            addLog("Định danh định tử e-KYC thành công. Đã thu thập hình ảnh và video thực thể sống.", 'success');
            // Complete KYC simulation
            appState.user.isLoggedIn = true;
            updateUserBadge();

            // Next: Login confirmation
            showStep('login-form');
        } else {
            addLog("Lỗi validation e-KYC: Thiếu tài liệu hoặc chưa xác thực khuôn mặt động.", 'danger');
        }
    });

    // Custom back override for reg step 2 back
    document.getElementById('btn-reg2-back').addEventListener('click', () => {
        showStep('register-step1');
    });

    // --- FORM 2: LOGIN ---
    const loginForm = document.getElementById('form-login');
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (validateFormInputs('form-login')) {
            const username = document.getElementById('login-username').value;
            addLog(`Xác thực mật khẩu thành công cho tài khoản: [${username}]. Khởi động xác thực lớp thứ hai 2FA...`, 'info');
            
            // Swap Form fields with 2FA digit grid
            loginForm.classList.add('hidden');
            document.getElementById('login-2fa-section').classList.remove('hidden');
            
            // Start 2FA Timer
            start2faTimer();
            
            // Focus on first input
            setTimeout(() => {
                document.querySelector('.otp-field').focus();
            }, 100);
        }
    });

    // 2FA Key movement
    setupOtpInputJumping('otp-field');

    // 2FA Verify Button
    document.getElementById('btn-verify-2fa').addEventListener('click', () => {
        let otpCode = "";
        document.querySelectorAll('.otp-field').forEach(input => {
            otpCode += input.value;
        });

        if (otpCode.length === 6) {
            clearInterval(otp2faCountdown);
            addLog(`Xác thực OTP 2FA thành công. Mã [${otpCode}] khớp hoàn toàn.`, 'success');
            
            // Set verification state
            appState.user.isLoggedIn = true;
            updateUserBadge();

            // Next: Risk profile updates
            showStep('risk-profile');
        } else {
            addLog("Mã 2FA không đủ 6 chữ số.", 'danger');
            document.querySelectorAll('.otp-field').forEach(i => i.classList.add('invalid'));
        }
    });

    document.getElementById('btn-resend-2fa').addEventListener('click', () => {
        start2faTimer();
        addLog("Đã gửi lại mã 2FA mới qua SMS/Authenticator (Giả lập: Nhập 6 số bất kỳ).", 'info');
    });

    // --- FORM 3: RISK PROFILE ---
    const riskForm = document.getElementById('form-risk-profile');
    riskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (validateFormInputs('form-risk-profile')) {
            appState.user.occupation = document.getElementById('edd-occupation').value;
            appState.user.company = document.getElementById('edd-company').value;
            appState.user.income = document.getElementById('edd-income').value;
            appState.user.isPep = document.querySelector('input[name="edd-pep"]:checked').value;

            addLog(`Hồ sơ rủi ro EDD cập nhật thành công: PEP = ${appState.user.isPep.toUpperCase()}`, 'success');
            
            // Unlock transaction group
            unlockGroup('group-transaction');
            updateUserBadge();

            // Auto transition to transaction flow
            showStep('tx-initiation');
        }
    });

    // --- FORM 4: TRANSACTION INITIATION ---
    // Monitor money amount for warnings
    const amountInput = document.getElementById('tx-amount');
    const currencySelect = document.getElementById('tx-currency');
    
    amountInput.addEventListener('input', checkTransactionThreshold);
    currencySelect.addEventListener('change', (e) => {
        document.getElementById('currency-display-unit').innerText = e.target.value;
        checkTransactionThreshold();
    });

    // Verify Swift length if provided
    const swiftInput = document.getElementById('tx-swift');
    swiftInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        if (val !== "" && (val.length < 8 || val.length > 11)) {
            swiftInput.classList.add('invalid');
        } else {
            swiftInput.classList.remove('invalid');
        }
    });

    const txForm1 = document.getElementById('form-tx-initiation');
    txForm1.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = validateFormInputs('form-tx-initiation');
        const swiftVal = swiftInput.value.trim();
        if (swiftVal !== "" && (swiftVal.length < 8 || swiftVal.length > 11)) {
            swiftInput.classList.add('invalid');
            isValid = false;
        }

        if (isValid) {
            appState.transaction.senderAccount = document.getElementById('tx-sender-account').value;
            appState.transaction.receiverName = document.getElementById('tx-receiver-name').value.toUpperCase();
            appState.transaction.receiverAccount = document.getElementById('tx-receiver-account').value;
            appState.transaction.receiverBank = document.getElementById('tx-receiver-bank').value;
            appState.transaction.receiverBranch = document.getElementById('tx-receiver-branch').value;
            appState.transaction.receiverCountry = document.getElementById('tx-receiver-country').value;
            appState.transaction.swiftCode = swiftVal;
            appState.transaction.receiverAddress = document.getElementById('tx-receiver-address').value;
            appState.transaction.amount = parseFloat(amountInput.value);
            appState.transaction.currency = currencySelect.value;

            addLog(`Khởi tạo giao dịch: Chuyển ${appState.transaction.amount.toLocaleString()} ${appState.transaction.currency} đến ${appState.transaction.receiverName} (${appState.transaction.receiverCountry})`, 'success');
            
            // Setup details on step 5 (Purpose)
            showStep('tx-purpose');
        } else {
            addLog("Lỗi validation giao dịch: Vui lòng nhập đầy đủ thông tin thụ hưởng.", 'danger');
        }
    });

    // --- FORM 5: SOURCE & PURPOSE ---
    const purposeSelect = document.getElementById('tx-purpose');
    const descTextarea = document.getElementById('tx-description');
    
    // Character counter for textarea
    descTextarea.addEventListener('input', (e) => {
        const count = e.target.value.length;
        document.getElementById('char-count').innerText = count;
        if (count >= 15) {
            descTextarea.classList.remove('invalid');
        }
    });

    // Trigger document hint updates when purpose changes
    purposeSelect.addEventListener('change', updateDocumentSuggestions);

    const txForm2 = document.getElementById('form-tx-purpose');
    txForm2.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = validateFormInputs('form-tx-purpose');
        if (descTextarea.value.length < 15) {
            descTextarea.classList.add('invalid');
            isValid = false;
        }

        if (isValid) {
            appState.transaction.relationship = document.getElementById('tx-relationship').value;
            appState.transaction.purpose = purposeSelect.value;
            appState.transaction.sourceOfFunds = document.getElementById('tx-source').value;
            appState.transaction.description = descTextarea.value;

            addLog(`Khai báo nguồn tiền: [${appState.transaction.sourceOfFunds}] | Mục đích: [${appState.transaction.purpose}]`, 'success');
            
            // Pre-fill Step 6 document hints
            updateDocumentSuggestions();
            showStep('tx-documents');
        } else {
            addLog("Lỗi validation khai báo: Vui lòng điền chi tiết nguồn tiền và mục đích (tối thiểu 15 ký tự mô tả).", 'danger');
        }
    });

    document.getElementById('btn-purpose-back').addEventListener('click', () => {
        showStep('tx-initiation');
    });

    // --- FORM 6: DOCUMENT UPLOAD ---
    setupMultiDragDropzone('dropzone-documents', 'file-documents', 'file-list-preview');

    const txForm3 = document.getElementById('form-tx-documents');
    txForm3.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isValid = true;
        // Require at least 1 document for high transactions or foreign transfers
        const totalVnd = appState.transaction.amount * appState.constants.EXCHANGE_RATES[appState.transaction.currency];
        const isInternational = appState.transaction.receiverCountry !== 'VN';
        
        if ((totalVnd >= appState.constants.CTR_THRESHOLD_VND || isInternational) && appState.transaction.uploadedFiles.length === 0) {
            document.getElementById('documents-error').style.display = 'block';
            document.getElementById('dropzone-documents').classList.add('invalid');
            isValid = false;
        } else {
            document.getElementById('documents-error').style.display = 'none';
            document.getElementById('dropzone-documents').classList.remove('invalid');
        }

        if (isValid) {
            appState.transaction.docNotes = document.getElementById('tx-doc-notes').value;
            addLog(`Đính kèm tài liệu thành công: Đã tải lên ${appState.transaction.uploadedFiles.length} tệp chứng từ chứng minh nguồn gốc.`, 'success');
            
            // Unlock step 3 group
            unlockGroup('group-auth-tx');
            showStep('tx-review');
        } else {
            addLog("Lỗi đính kèm hồ sơ: Luật chống rửa tiền yêu cầu hồ sơ pháp lý đối với giao dịch nước ngoài hoặc chuyển khoản giá trị lớn.", 'danger');
        }
    });

    document.getElementById('btn-documents-back').addEventListener('click', () => {
        showStep('tx-purpose');
    });

    // --- FORM 7: TRANSACTION REVIEW ---
    const txReviewForm = document.getElementById('form-tx-review');
    txReviewForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const legalOk = document.getElementById('commit-legal').checked;
        const truthOk = document.getElementById('commit-truth').checked;
        const termsOk = document.getElementById('commit-terms').checked;

        if (legalOk && truthOk && termsOk) {
            addLog("Cam kết pháp lý đã được ký nhận bằng khóa riêng tư khách hàng.", 'success');
            showStep('tx-approval');
        } else {
            addLog("Lỗi: Quý khách bắt buộc phải đọc và tích chọn cam kết pháp lý chống rửa tiền trước khi tiến hành.", 'danger');
        }
    });

    document.getElementById('btn-review-back').addEventListener('click', () => {
        showStep('tx-documents');
    });

    // --- FORM 8: FINAL APPROVAL ---
    setupOtpInputJumping('otp-field-smart');
    
    // Autofill Smart OTP mẫu
    document.getElementById('btn-autofill-otp').addEventListener('click', () => {
        const fields = document.querySelectorAll('.otp-field-smart');
        const code = "888888";
        fields.forEach((field, idx) => {
            field.value = code[idx];
        });
        document.getElementById('btn-confirm-transaction').removeAttribute('disabled');
        addLog("Đã điền mã Smart OTP mẫu [888888] thành công.", 'info');
    });

    // Biometric Auth Modal simulation
    document.getElementById('btn-biometric-auth').addEventListener('click', () => {
        const modal = document.getElementById('biometric-simulation');
        modal.classList.remove('hidden');
        addLog("Khởi tạo API WebAuthn trên thiết bị. Yêu cầu khóa sinh trắc học...", "system");

        setTimeout(() => {
            modal.classList.add('hidden');
            appState.transaction.biometricVerified = true;
            addLog("WebAuthn: Xác minh sinh trắc học vân tay/khuôn mặt thành công qua Windows Hello.", "success");
            
            // Auto complete OTP boxes
            document.querySelectorAll('.otp-field-smart').forEach(f => f.value = "9");
            document.getElementById('btn-confirm-transaction').removeAttribute('disabled');
            
            // Trigger confirmation click directly
            document.getElementById('btn-confirm-transaction').click();
        }, 2200);
    });

    // Submit transaction to AML scoring engine
    document.getElementById('btn-confirm-transaction').addEventListener('click', () => {
        addLog("Lệnh giao dịch đã ký khóa số thành công. Bắt đầu gửi lệnh kiểm toán chống rửa tiền.", "system");
        showStep('tx-status');
        runAmlAuditScoring();
    });

    document.getElementById('btn-approval-back').addEventListener('click', () => {
        showStep('tx-review');
    });

    // --- FORM 9: RESULTS STATUS ---
    document.getElementById('btn-success-new').addEventListener('click', () => {
        resetTransactionState();
        showStep('tx-initiation');
    });

    document.getElementById('btn-pending-edit').addEventListener('click', () => {
        showStep('tx-documents');
    });

    document.getElementById('btn-pending-home').addEventListener('click', () => {
        resetTransactionState();
        showStep('tx-initiation');
    });

    // --- QUICK DEMO PRESETS PANEL ---
    document.getElementById('demo-fill-normal').addEventListener('click', () => fillDemoScenario('normal'));
    document.getElementById('demo-fill-high-amount').addEventListener('click', () => fillDemoScenario('high_amount'));
    document.getElementById('demo-fill-sanction').addEventListener('click', () => fillDemoScenario('sanction'));
}

// Helper: Setup navigation check trigger for OTP
function setupOtpInputJumping(className) {
    const fields = document.querySelectorAll(`.${className}`);
    fields.forEach((field, index) => {
        field.addEventListener('input', (e) => {
            // Numbers only
            field.value = field.value.replace(/[^0-9]/g, '');

            if (field.value.length === 1 && index < fields.length - 1) {
                fields[index + 1].focus();
            }

            // Check if all fields filled
            checkAllOtpFieldsFilled(className);
        });

        field.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && field.value.length === 0 && index > 0) {
                fields[index - 1].focus();
            }
        });
    });
}

function checkAllOtpFieldsFilled(className) {
    const fields = document.querySelectorAll(`.${className}`);
    let filled = true;
    fields.forEach(f => {
        if (f.value === "") filled = false;
    });

    if (className === 'otp-field-smart') {
        const confirmBtn = document.getElementById('btn-confirm-transaction');
        if (filled) {
            confirmBtn.removeAttribute('disabled');
        } else {
            confirmBtn.setAttribute('disabled', 'disabled');
        }
    }
}

// ==========================================================================
// 5. REGULATION CHECKERS & SUGGESTIONS
// ==========================================================================
function checkTransactionThreshold() {
    const amountVal = parseFloat(document.getElementById('tx-amount').value) || 0;
    const currency = document.getElementById('tx-currency').value;
    const exchangeRate = appState.constants.EXCHANGE_RATES[currency] || 1;
    const totalVnd = amountVal * exchangeRate;

    const warningBox = document.getElementById('large-tx-warning');
    if (totalVnd >= appState.constants.CTR_THRESHOLD_VND) {
        warningBox.classList.remove('hidden');
        // Dynamic warn text
        const amountFormatted = amountVal.toLocaleString() + ' ' + currency;
        const vndFormatted = totalVnd.toLocaleString() + ' VND';
        document.getElementById('warning-text').innerHTML = `Số tiền bạn yêu cầu chuyển (<b>${amountFormatted}</b> quy đổi ~ <b>${vndFormatted}</b>) vượt ngưỡng quy định báo cáo giao dịch giá trị lớn (CTR) từ 400 triệu VND trở lên theo quyết định của Ngân hàng Nhà nước Việt Nam. Bạn có nghĩa vụ giải trình dòng tiền này ở các bước tiếp theo.`;
        
        addLog(`[AML CHECK] Cảnh báo: Số tiền giao dịch quy đổi đạt ${vndFormatted}. Kích hoạt quy tắc báo cáo giao dịch lớn CTR (NHNN).`, 'warning');
    } else {
        warningBox.classList.add('hidden');
    }
}

function updateDocumentSuggestions() {
    const purpose = document.getElementById('tx-purpose').value;
    const hintTitle = document.getElementById('doc-hint-purpose-title');
    const hintList = document.getElementById('doc-hint-list');
    
    if (!purpose) {
        hintTitle.innerText = "Chưa chọn mục đích";
        hintList.innerHTML = "<li>Vui lòng chọn mục đích chuyển tiền ở bước trước để xem gợi ý tài liệu phù hợp.</li>";
        return;
    }

    // Translate English keys for display
    const translations = {
        study: "Thanh toán học phí (Du học)",
        medical: "Thanh toán viện phí / Khám chữa bệnh",
        family_support: "Trợ cấp thân nhân ở nước ngoài",
        investment: "Đầu tư tài chính / Mua cổ phiếu ngoại",
        real_estate: "Mua bất động sản / Nhà đất nước ngoài",
        commerce: "Thanh toán hợp đồng thương mại",
        savings: "Gửi tiết kiệm / Chuyển khoản cùng chủ tài khoản"
    };

    hintTitle.innerText = translations[purpose] || purpose;
    
    const docs = documentRequirements[purpose] || ["Hồ sơ tự do chứng minh tính chất giao dịch."];
    hintList.innerHTML = "";
    docs.forEach(doc => {
        const li = document.createElement('li');
        li.innerText = doc;
        hintList.appendChild(li);
    });

    addLog(`Cập nhật gợi ý danh mục chứng từ tự động cho mục đích: [${translations[purpose]}]`, 'info');
}

// ==========================================================================
// 6. MOCK INTERACTIVE UTILITIES (WEBCAM & FILE UPLOADS)
// ==========================================================================

// Simple single file drag and drop helper
function setupDragDropzone(zoneId, inputId, previewId) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    zone.addEventListener('click', () => input.click());

    input.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0], zone, preview);
        }
    });

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            input.files = e.dataTransfer.files;
            handleFileSelect(e.dataTransfer.files[0], zone, preview);
        }
    });
}

function handleFileSelect(file, zone, preview) {
    if (!file.type.startsWith('image/')) {
        alert("Chỉ chấp nhận tệp hình ảnh (.jpg, .png)");
        return;
    }
    
    // Check size limit (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert("Hình ảnh vượt quá dung lượng cho phép (tối đa 5MB)");
        return;
    }

    zone.classList.remove('invalid');
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.style.backgroundImage = `url('${e.target.result}')`;
        preview.classList.remove('hidden');
        
        // Add delete badge
        const badge = document.createElement('span');
        badge.className = 'preview-remove-badge';
        badge.innerText = 'Xóa và Tải lại';
        badge.onclick = (event) => {
            event.stopPropagation();
            preview.classList.add('hidden');
            preview.innerHTML = '';
            // Reset input
            const input = zone.querySelector('input[type="file"]');
            if (input) input.value = '';
            addLog(`Đã xóa ảnh giấy tờ tải lên.`, 'info');
        };
        preview.appendChild(badge);
    };
    reader.readAsDataURL(file);
    addLog(`Đã tải lên tệp ảnh giấy tờ: ${file.name} (${(file.size/1024).toFixed(1)} KB)`, 'info');
}

// Multi-file drag and drop helper for step 6 (documents)
function setupMultiDragDropzone(zoneId, inputId, previewListId) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const previewList = document.getElementById(previewListId);

    zone.addEventListener('click', () => input.click());

    input.addEventListener('change', (e) => {
        handleMultiFilesSelect(e.target.files, previewList);
    });

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleMultiFilesSelect(e.dataTransfer.files, previewList);
        }
    });
}

function handleMultiFilesSelect(files, previewList) {
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Accept image or pdf
        const isPdf = file.type === 'application/pdf';
        const isImg = file.type.startsWith('image/');
        if (!isPdf && !isImg) {
            alert("Hệ thống chỉ chấp nhận tài liệu dạng ảnh hoặc PDF");
            continue;
        }

        // Limit size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert(`File ${file.name} vượt dung lượng tối đa 10MB.`);
            continue;
        }

        // Push to state
        appState.transaction.uploadedFiles.push(file);

        // Add visual element
        const item = document.createElement('div');
        item.className = 'file-preview-item';
        item.setAttribute('data-filename', file.name);
        
        const info = document.createElement('div');
        info.className = 'file-name-info';
        
        // Custom SVG for file type
        info.innerHTML = `
            <svg class="file-type-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
            </svg>
            <span>${file.name} (${(file.size/(1024*1024)).toFixed(2)} MB)</span>
        `;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'file-delete-btn';
        deleteBtn.innerText = 'Xóa';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            item.remove();
            appState.transaction.uploadedFiles = appState.transaction.uploadedFiles.filter(f => f.name !== file.name);
            if (appState.transaction.uploadedFiles.length === 0) {
                previewList.classList.add('hidden');
            }
            addLog(`Đã xóa chứng từ đính kèm: ${file.name}`, 'info');
        };

        item.appendChild(info);
        item.appendChild(deleteBtn);
        previewList.appendChild(item);
    }

    if (appState.transaction.uploadedFiles.length > 0) {
        previewList.classList.remove('hidden');
        document.getElementById('dropzone-documents').classList.remove('invalid');
        document.getElementById('documents-error').style.display = 'none';
    }

    addLog(`Đã đăng ký tài liệu chứng từ mới vào hồ sơ giao dịch.`, 'info');
}

// e-KYC Simulated Liveness Check
function startLivenessCheck() {
    const placeholder = document.getElementById('camera-placeholder');
    const cameraActive = document.getElementById('camera-active');
    const video = document.getElementById('webcam');
    const prompt = document.getElementById('gesture-prompt');

    addLog("Đang kết nối thiết bị ghi hình (Webcam Camera)...", "system");

    // Try accessing camera
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(stream => {
                localStream = stream;
                video.srcObject = stream;
                placeholder.classList.add('hidden');
                cameraActive.classList.remove('hidden');
                runLivenessTimeline();
            })
            .catch(err => {
                addLog("Không thể mở Webcam (Quyền truy cập bị từ chối hoặc không có thiết bị). Chuyển sang mô phỏng video tự động...", "warning");
                simulateLivenessCheck();
            });
    } else {
        addLog("Trình duyệt không hỗ trợ Media API. Chuyển sang mô phỏng video...", "warning");
        simulateLivenessCheck();
    }
}

// Timeline sequence of head gestures
function runLivenessTimeline() {
    const prompt = document.getElementById('gesture-prompt');
    const steps = [
        { msg: "Vui lòng giữ nguyên đầu vào khung tròn...", time: 2000 },
        { msg: "Quay đầu từ từ sang TRÁI...", time: 2000 },
        { msg: "Quay đầu từ từ sang PHẢI...", time: 2000 },
        { msg: "Nhìn thẳng vào camera và MỈM CƯỜI...", time: 2000 },
        { msg: "Định danh Liveness thành công!", time: 1000 }
    ];

    let currentStepIdx = 0;
    
    function nextGesture() {
        if (currentStepIdx < steps.length) {
            const step = steps[currentStepIdx];
            prompt.innerText = step.msg;
            addLog(`[Liveness Step] ${step.msg}`, 'info');
            
            currentStepIdx++;
            livenessTimer = setTimeout(nextGesture, step.time);
        } else {
            // Liveness Pass!
            stopCameraStream();
            appState.user.isKycVerified = true;
            addLog("e-KYC Liveness Check: Khớp khuôn mặt thực thể 99.8%. Chứng minh thực thể sống PASSED.", "success");
            
            // Show successful message in webcam placeholder
            const placeholder = document.getElementById('camera-placeholder');
            const cameraActive = document.getElementById('camera-active');
            cameraActive.classList.add('hidden');
            placeholder.classList.remove('hidden');
            placeholder.innerHTML = `
                <div style="color: var(--success); display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
                    <svg style="width: 48px; height: 48px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    <p style="font-weight: 700;">LIVENESS VERIFIED PASSED</p>
                    <span style="font-size: 0.75rem; color: var(--text-secondary)">Quét khuôn mặt chống Deepfake thành công.</span>
                </div>
            `;
            document.getElementById('liveness-error').style.display = 'none';
        }
    }

    nextGesture();
}

function simulateLivenessCheck() {
    const placeholder = document.getElementById('camera-placeholder');
    placeholder.innerHTML = `
        <div class="loading-spinner-huge" style="width: 40px; height: 40px; margin-bottom: 0.5rem;"></div>
        <p style="font-weight: 600; color: var(--warning)">Đang quét mô phỏng khuôn mặt...</p>
        <span style="font-size: 0.75rem; color: var(--text-muted)">Hệ thống đang chạy tập lệnh mô phỏng sinh trắc học cử chỉ.</span>
    `;

    setTimeout(() => {
        appState.user.isKycVerified = true;
        addLog("e-KYC Liveness: Sử dụng tập lệnh video mô phỏng để thay thế camera. Kết quả PASSED.", "success");
        placeholder.innerHTML = `
            <div style="color: var(--success); display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
                <svg style="width: 48px; height: 48px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <p style="font-weight: 700;">MÔ PHỎNG LIVENESS THÀNH CÔNG</p>
                <span style="font-size: 0.75rem; color: var(--text-secondary)">Trình mô phỏng đã hoàn tất xác thực sinh trắc.</span>
            </div>
        `;
        document.getElementById('liveness-error').style.display = 'none';
    }, 4000);
}

function handleLivenessVideoUpload(e) {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        addLog(`Đang phân tích tệp Video cử chỉ tải lên: ${file.name}...`, 'info');
        simulateLivenessCheck();
    }
}

function stopCameraStream() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    if (livenessTimer) {
        clearTimeout(livenessTimer);
    }
}

// 2FA Timer
function start2faTimer() {
    if (otp2faCountdown) clearInterval(otp2faCountdown);
    
    let secondsLeft = 120;
    const timerText = document.getElementById('2fa-timer-count');
    
    otp2faCountdown = setInterval(() => {
        secondsLeft--;
        timerText.innerText = secondsLeft;
        
        if (secondsLeft <= 0) {
            clearInterval(otp2faCountdown);
            addLog("Mã xác thực 2FA đã hết hạn. Vui lòng bấm Gửi lại để nhận mã mới.", "warning");
        }
    }, 1000);
}

// ==========================================================================
// 7. COMPILING REVIEWS & SCORES
// ==========================================================================
function populateReviewPage() {
    document.getElementById('rev-sender').innerText = appState.transaction.senderAccount === 'acct_1' ? "Tài khoản thanh toán VND - 1092837465" : "Tài khoản Đô la Mỹ USD - 9901837465";
    document.getElementById('rev-receiver-name').innerText = appState.transaction.receiverName;
    document.getElementById('rev-receiver-account').innerText = appState.transaction.receiverAccount;
    
    const branchText = appState.transaction.receiverBranch ? ` - ${appState.transaction.receiverBranch}` : "";
    document.getElementById('rev-bank').innerText = `${appState.transaction.receiverBank}${branchText}`;
    
    const countries = {
        VN: "Việt Nam (Nội địa)",
        US: "Hoa Kỳ (Mỹ)",
        SG: "Singapore",
        KR: "Hàn Quốc",
        JP: "Nhật Bản",
        MY: "Malaysia",
        EU: "Khu vực Châu Âu (Eurozone)",
        IR: "Iran (Quốc gia cấm vận)",
        KP: "Triều Tiên (Quốc gia cấm vận)",
        RU: "Nga (Quốc gia rủi ro cao)"
    };
    document.getElementById('rev-country').innerText = countries[appState.transaction.receiverCountry] || appState.transaction.receiverCountry;
    document.getElementById('rev-swift').innerText = appState.transaction.swiftCode || "Không có (Nội địa)";
    document.getElementById('rev-receiver-address').innerText = appState.transaction.receiverAddress;
    
    // Amount formatting
    document.getElementById('rev-amount').innerText = `${appState.transaction.amount.toLocaleString()} ${appState.transaction.currency}`;
    
    const relations = {
        self: "Bản thân",
        family: "Người thân",
        business: "Đối tác kinh doanh",
        friend: "Bạn bè / Người quen",
        stranger: "Không quen biết"
    };
    document.getElementById('rev-relationship').innerText = relations[appState.transaction.relationship] || appState.transaction.relationship;
    
    const purposes = {
        study: "Thanh toán học phí (Du học)",
        medical: "Khám chữa bệnh nước ngoài",
        family_support: "Trợ cấp thân nhân",
        investment: "Đầu tư tài chính",
        real_estate: "Mua bất động sản / Nhà đất",
        commerce: "Hợp đồng thương mại",
        savings: "Gửi tiết kiệm / Chuyển khoản cùng chủ tài khoản"
    };
    document.getElementById('rev-purpose').innerText = purposes[appState.transaction.purpose] || appState.transaction.purpose;

    const sources = {
        salary: "Lương / Thu nhập công việc",
        real_estate_sale: "Tiền bán bất động sản",
        inheritance: "Thừa kế / Tặng cho",
        business_profit: "Lợi nhuận kinh doanh / Cổ tức",
        loan: "Khoản vay ngân hàng",
        other: "Nguồn gốc hợp pháp khác"
    };
    document.getElementById('rev-source').innerText = sources[appState.transaction.sourceOfFunds] || appState.transaction.sourceOfFunds;
    document.getElementById('rev-description').innerText = `"${appState.transaction.description}"`;

    // Files list
    const fileListEl = document.getElementById('rev-files');
    if (appState.transaction.uploadedFiles.length > 0) {
        fileListEl.innerHTML = appState.transaction.uploadedFiles.map(f => `<span style="display:inline-block; margin-right: 8px; padding: 2px 6px; background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); border-radius:4px; font-size: 0.75rem;">${f.name}</span>`).join('');
    } else {
        fileListEl.innerText = "Không đính kèm tài liệu";
    }

    addLog("Đã biên soạn trang tóm tắt đánh giá giao dịch. Yêu cầu ký cam kết số.", "info");
}

// --- AML RISK SCORING ENGINE (AI SIMULATOR) ---
function runAmlAuditScoring() {
    const processingEl = document.getElementById('status-processing');
    const approvedEl = document.getElementById('status-approved');
    const pendingEl = document.getElementById('status-pending');

    processingEl.classList.remove('hidden');
    approvedEl.classList.add('hidden');
    pendingEl.classList.add('hidden');

    const substeps = [
        { id: 'substep-sanction', text: 'Quét danh sách cấm vận trừng phạt' },
        { id: 'substep-pep', text: 'Kiểm tra liên kết chính trị PEP' },
        { id: 'substep-aml', text: 'Phân tích cấu trúc giao dịch & Chứng từ chứng minh' },
        { id: 'substep-ai', text: 'Chạy thuật toán AI chấm điểm rủi ro hành vi' }
    ];

    let currentSub = 0;
    
    // Clear checking statuses
    substeps.forEach(s => {
        const el = document.getElementById(s.id);
        el.className = "substep";
    });

    function runSubstep() {
        if (currentSub < substeps.length) {
            const step = substeps[currentSub];
            const el = document.getElementById(step.id);
            el.className = "substep checking";
            
            addLog(`[AML ENGINE] Bắt đầu bước: ${step.text}...`, 'info');
            
            // Generate some dynamic checks in the logger
            if (step.id === 'substep-sanction') {
                const sanctionCountries = ['IR', 'KP'];
                const isSanctioned = sanctionCountries.includes(appState.transaction.receiverCountry);
                setTimeout(() => {
                    if (isSanctioned) {
                        el.className = "substep failed";
                        addLog(`[AML ALARM] QUÉT CẤM VẬN: Phát hiện thụ hưởng tại quốc gia cấm vận: ${appState.transaction.receiverCountry}!`, 'danger');
                    } else {
                        el.className = "substep passed";
                        addLog(`[AML PASS] QUÉT CẤM VẬN: Không nằm trong danh sách đen trừng phạt.`, 'success');
                    }
                    currentSub++;
                    runSubstep();
                }, 1200);
            } 
            else if (step.id === 'substep-pep') {
                const isPep = appState.user.isPep === 'yes';
                setTimeout(() => {
                    if (isPep) {
                        el.className = "substep checking"; // Warning but not absolute block
                        addLog(`[AML WARNING] KIỂM TRA PEP: Khách hàng thuộc đối tượng chính trị cấp cao PEP.`, 'warning');
                    } else {
                        el.className = "substep passed";
                        addLog(`[AML PASS] KIỂM TRA PEP: Khách hàng không thuộc diện PEP chính trị.`, 'success');
                    }
                    currentSub++;
                    runSubstep();
                }, 1200);
            }
            else if (step.id === 'substep-aml') {
                const totalVnd = appState.transaction.amount * appState.constants.EXCHANGE_RATES[appState.transaction.currency];
                const needsDocs = totalVnd >= appState.constants.CTR_THRESHOLD_VND || appState.transaction.receiverCountry !== 'VN';
                const hasDocs = appState.transaction.uploadedFiles.length > 0;
                
                setTimeout(() => {
                    if (needsDocs && !hasDocs) {
                        el.className = "substep failed";
                        addLog(`[AML ALARM] KIỂM TRA CHỨNG TỪ: Thiếu hồ sơ đính kèm bắt buộc đối với giao dịch lớn/nước ngoài.`, 'danger');
                    } else if (needsDocs && hasDocs) {
                        el.className = "substep passed";
                        addLog(`[AML PASS] KIỂM TRA CHỨNG TỪ: Có đính kèm ${appState.transaction.uploadedFiles.length} tài liệu hợp lệ.`, 'success');
                    } else {
                        el.className = "substep passed";
                        addLog(`[AML PASS] KIỂM TRA CHỨNG TỪ: Số tiền nhỏ, không bắt buộc đính kèm hồ sơ.`, 'success');
                    }
                    currentSub++;
                    runSubstep();
                }, 1200);
            }
            else if (step.id === 'substep-ai') {
                setTimeout(() => {
                    el.className = "substep passed";
                    calculateFinalAmlScore();
                }, 1200);
            }
        }
    }

    runSubstep();
}

async function calculateFinalAmlScore() {
    const processingEl = document.getElementById('status-processing');
    const approvedEl = document.getElementById('status-approved');
    const pendingEl = document.getElementById('status-pending');

    let tx_type = 'TRANSFER';
    if (appState.transaction.purpose === 'commerce') tx_type = 'PAYMENT';
    if (appState.transaction.purpose === 'savings' || appState.transaction.purpose === 'study') tx_type = 'TRANSFER';
    
    let is_vpn = 0;
    let login_hr = 14; 
    let is_new_dev = 0;
    
    if (appState.transaction.receiverCountry === 'IR') {
        is_vpn = 1;
        tx_type = 'CASH_OUT';
    }
    if (appState.transaction.amount > 500000000) {
        login_hr = 3; 
        is_new_dev = 1;
    }

    const payload = {
        type: tx_type,
        amount: appState.transaction.amount * appState.constants.EXCHANGE_RATES[appState.transaction.currency],
        oldbalanceOrg: 1000000000,
        newbalanceOrig: 1000000000 - (appState.transaction.amount * appState.constants.EXCHANGE_RATES[appState.transaction.currency]),
        oldbalanceDest: 0,
        newbalanceDest: appState.transaction.amount * appState.constants.EXCHANGE_RATES[appState.transaction.currency],
        tx_frequency_1m: appState.transaction.amount > 500000000 ? 5 : 1,
        login_hour: login_hr,
        is_new_device: is_new_dev,
        is_vpn_proxy: is_vpn,
        failed_login_count: 0,
        distance_from_last_login: is_vpn ? 500.0 : 5.0,
        time_since_last_login: 120.0
    };

    try {
        const response = await fetch('/api/ai/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Lỗi Server API");
        const result = await response.json();

        const score = result.risk_score;
        const rules = result.fraud_reasons;
        const blockHash = result.blockchain_hash;

        appState.transaction.riskScore = score;
        appState.transaction.triggeredRules = rules;

        processingEl.classList.add('hidden');

        const refNumber = `TXN-${Math.floor(100000 + Math.random() * 900000)}-AEGIS`;
        const formatAmount = appState.transaction.amount.toLocaleString() + ' ' + appState.transaction.currency;
        const formatTime = new Date().toLocaleString('vi-VN');

        if (result.alert_level === 'HIGH' || result.alert_level === 'CRITICAL') {
            appState.transaction.status = 'Blocked';
            pendingEl.classList.remove('hidden');
            
            document.getElementById('pending-ref-num').innerText = blockHash;
            document.getElementById('pending-amount').innerText = formatAmount;
            document.getElementById('pending-risk-score').innerText = `${score} / 100 (${getRiskLevelText(score)})`;
            
            const badge = document.getElementById('pending-risk-score');
            badge.className = 'risk-badge badge-red';

            const rulesList = document.getElementById('pending-rules-list');
            rulesList.innerHTML = "";
            rules.forEach(r => {
                const li = document.createElement('li');
                li.innerText = r;
                rulesList.appendChild(li);
            });

            addLog(`[AML ALARM] Bị chặn bởi AI. Điểm: ${score}/100. Lưu Blockchain Hash: ${blockHash.substring(0, 16)}...`, 'danger');
        } else {
            appState.transaction.status = 'Approved';
            approvedEl.classList.remove('hidden');

            document.getElementById('receipt-ref-num').innerText = blockHash;
            document.getElementById('receipt-amount').innerText = formatAmount;
            document.getElementById('receipt-receiver').innerText = appState.transaction.receiverName;
            document.getElementById('receipt-time').innerText = formatTime;
            document.getElementById('receipt-risk-score').innerText = `${score} / 100 (${getRiskLevelText(score)})`;
            
            const badge = document.getElementById('receipt-risk-score');
            badge.className = 'risk-badge badge-green';

            addLog(`[AML PASS] Giao dịch an toàn. AI duyệt với điểm số rủi ro cực thấp.`, 'success');
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (err) {
        addLog(`[LỖI KẾT NỐI] Không thể gọi API AI Backend. Lỗi: ${err.message}`, 'danger');
        processingEl.classList.add('hidden');
        alert("Lỗi kết nối Backend: Server AI hiện không phản hồi!");
    }
}

function getRiskLevelText(score) {
    if (score < 40) return "Rủi ro thấp";
    if (score < 70) return "Rủi ro trung bình";
    return "Rủi ro cao (Nguy hiểm)";
}

// Reset transaction states for a new one
function resetTransactionState() {
    appState.transaction = {
        senderAccount: 'acct_1',
        receiverName: '',
        receiverAccount: '',
        receiverBank: '',
        receiverBranch: '',
        receiverCountry: 'VN',
        swiftCode: '',
        receiverAddress: '',
        amount: 0,
        currency: 'VND',
        relationship: '',
        purpose: '',
        sourceOfFunds: '',
        description: '',
        uploadedFiles: [],
        docNotes: '',
        otpVerified: false,
        biometricVerified: false,
        riskScore: 0,
        triggeredRules: [],
        status: 'Pending'
    };

    // Reset Forms
    document.getElementById('form-tx-initiation').reset();
    document.getElementById('form-tx-purpose').reset();
    document.getElementById('form-tx-documents').reset();
    document.getElementById('form-tx-review').reset();
    
    // Clear document files list
    document.getElementById('file-list-preview').innerHTML = "";
    document.getElementById('file-list-preview').classList.add('hidden');
    
    // Reset OTP boxes
    document.querySelectorAll('.otp-field-smart').forEach(f => f.value = "");
    document.getElementById('btn-confirm-transaction').setAttribute('disabled', 'disabled');

    // Reset warnings
    document.getElementById('large-tx-warning').classList.add('hidden');
    document.getElementById('char-count').innerText = "0";

    addLog("Đã khởi tạo lại biểu mẫu giao dịch mới.", "system");
}

// ==========================================================================
// 8. SCENARIOS QUICK AUTOFILL PANEL (DEMO SUITE)
// ==========================================================================
function fillDemoScenario(type) {
    addLog(`Đang kích hoạt Kịch bản Demo: [${type.toUpperCase()}]`, 'system');
    
    // 1. Force registration & Login simulation
    appState.user = {
        fullname: 'NGUYỄN VĂN A',
        email: 'demo.user@aegis-secure.vn',
        phone: '0987654321',
        dob: '1990-05-15',
        doctype: 'cccd_chip',
        nationality: 'Việt Nam',
        permanentAddress: '88 Láng Hạ, Đống Đa, Hà Nội',
        currentAddress: '88 Láng Hạ, Đống Đa, Hà Nội',
        isKycVerified: true,
        isLoggedIn: true,
        occupation: 'Trưởng phòng kinh doanh',
        company: 'FPT Software',
        income: '50m_100m',
        isPep: type === 'high_amount' ? 'yes' : 'no' // PEP in scenario B
    };
    updateUserBadge();

    // 2. Unlock all groups
    unlockGroup('group-auth');
    unlockGroup('group-transaction');
    unlockGroup('group-auth-tx');

    // 3. Fill transaction data
    resetTransactionState();

    if (type === 'normal') {
        appState.transaction.receiverName = "TRẦN THỊ B";
        appState.transaction.receiverAccount = "190293847565";
        appState.transaction.receiverBank = "Vietcombank";
        appState.transaction.receiverBranch = "Chi nhánh Tân Bình";
        appState.transaction.receiverCountry = "VN";
        appState.transaction.receiverAddress = "456 Nguyễn Huệ, Quận 1, TP. HCM";
        appState.transaction.amount = 50000000;
        appState.transaction.currency = "VND";
        appState.transaction.relationship = "family";
        appState.transaction.purpose = "savings";
        appState.transaction.sourceOfFunds = "salary";
        appState.transaction.description = "Chuyển tiền tiết kiệm cá nhân hàng tháng cho người thân.";
        
        // Mock a document upload
        appState.transaction.uploadedFiles = [
            { name: "cam_ket_nguon_tien.pdf", size: 1204850, type: "application/pdf" }
        ];
    } 
    else if (type === 'high_amount') {
        appState.transaction.receiverName = "CÔNG TY BẤT ĐỘNG SẢN HOÀNG GIA";
        appState.transaction.receiverAccount = "998877665544";
        appState.transaction.receiverBank = "BIDV";
        appState.transaction.receiverBranch = "Chi nhánh Sở Giao Dịch 1";
        appState.transaction.receiverCountry = "VN";
        appState.transaction.receiverAddress = "12 Lê Duẩn, Quận 1, TP. HCM";
        appState.transaction.amount = 550000000; // 550 Million VND > 400M Threshold
        appState.transaction.currency = "VND";
        appState.transaction.relationship = "business";
        appState.transaction.purpose = "real_estate";
        appState.transaction.sourceOfFunds = "real_estate_sale";
        appState.transaction.description = "Chuyển tiền đặt cọc mua căn hộ chung cư cao cấp Hoàng Gia Luxury theo hợp đồng số 102/HĐĐC.";
        
        appState.transaction.uploadedFiles = [
            { name: "hop_dong_dat_coc.pdf", size: 4509180, type: "application/pdf" },
            { name: "giay_nop_thue_truoc_ba.jpg", size: 1890200, type: "image/jpeg" }
        ];
    }
    else if (type === 'sanction') {
        appState.transaction.receiverName = "SADJAD INTERNATIONAL TRADING CO";
        appState.transaction.receiverAccount = "IR8899882200112233";
        appState.transaction.receiverBank = "Melli Bank Iran";
        appState.transaction.receiverBranch = "Tehran Main Branch";
        appState.transaction.receiverCountry = "IR"; // Iran (Sanctioned country)
        appState.transaction.swiftCode = "MELIIRTHXXX";
        appState.transaction.receiverAddress = "15 Vali Asr Street, Tehran, Iran";
        appState.transaction.amount = 150000000;
        appState.transaction.currency = "VND";
        appState.transaction.relationship = "business";
        appState.transaction.purpose = "commerce";
        appState.transaction.sourceOfFunds = "business_profit";
        appState.transaction.description = "Thanh toán hợp đồng mua hạt dẻ cười nhập khẩu theo hóa đơn thương mại số INV-90283.";
        
        appState.transaction.uploadedFiles = [
            { name: "hoa_don_thuong_mai_inv90283.pdf", size: 2190300, type: "application/pdf" }
        ];
    }

    // 4. Synchronize all inputs in fields (so fields show correct data if users go backward)
    syncStateToInputs();

    // 5. Instantly jump to review step for user verification
    showStep('tx-review');
    addLog(`Đã điền sẵn và chuyển thẳng đến Bước 7 [Xác nhận thông tin] để bạn tiện kiểm duyệt kết quả AML.`, 'success');
}

function syncStateToInputs() {
    // Basic info
    document.getElementById('reg-fullname').value = appState.user.fullname;
    document.getElementById('reg-email').value = appState.user.email;
    document.getElementById('reg-phone').value = appState.user.phone;
    
    // KYC
    document.getElementById('kyc-dob').value = appState.user.dob;
    document.getElementById('kyc-doctype').value = appState.user.doctype;
    document.getElementById('kyc-nationality').value = appState.user.nationality;
    document.getElementById('kyc-permanent-address').value = appState.user.permanentAddress;
    document.getElementById('kyc-same-address').checked = true;
    document.getElementById('current-address-group').classList.add('hidden');
    
    // Previews (Use fake image backgrounds for demo)
    document.getElementById('preview-front').style.backgroundImage = "url('https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?auto=format&fit=crop&q=80&w=400')";
    document.getElementById('preview-front').classList.remove('hidden');
    document.getElementById('preview-back').style.backgroundImage = "url('https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?auto=format&fit=crop&q=80&w=400')";
    document.getElementById('preview-back').classList.remove('hidden');
    
    // Risk profile
    document.getElementById('edd-occupation').value = appState.user.occupation;
    document.getElementById('edd-company').value = appState.user.company;
    document.getElementById('edd-income').value = appState.user.income;
    const pepRadios = document.getElementsByName('edd-pep');
    pepRadios.forEach(radio => {
        if (radio.value === appState.user.isPep) radio.checked = true;
    });

    // Transaction
    document.getElementById('tx-sender-account').value = appState.transaction.senderAccount;
    document.getElementById('tx-receiver-name').value = appState.transaction.receiverName;
    document.getElementById('tx-receiver-account').value = appState.transaction.receiverAccount;
    document.getElementById('tx-receiver-bank').value = appState.transaction.receiverBank;
    document.getElementById('tx-receiver-branch').value = appState.transaction.receiverBranch;
    document.getElementById('tx-receiver-country').value = appState.transaction.receiverCountry;
    document.getElementById('tx-swift').value = appState.transaction.swiftCode;
    document.getElementById('tx-receiver-address').value = appState.transaction.receiverAddress;
    document.getElementById('tx-amount').value = appState.transaction.amount;
    document.getElementById('tx-currency').value = appState.transaction.currency;
    document.getElementById('currency-display-unit').innerText = appState.transaction.currency;

    // Check threshold alert
    checkTransactionThreshold();

    // Purpose
    document.getElementById('tx-relationship').value = appState.transaction.relationship;
    document.getElementById('tx-purpose').value = appState.transaction.purpose;
    document.getElementById('tx-source').value = appState.transaction.sourceOfFunds;
    document.getElementById('tx-description').value = appState.transaction.description;
    document.getElementById('char-count').innerText = appState.transaction.description.length;

    // Files list
    const previewList = document.getElementById('file-list-preview');
    previewList.innerHTML = "";
    appState.transaction.uploadedFiles.forEach(file => {
        const item = document.createElement('div');
        item.className = 'file-preview-item';
        item.innerHTML = `
            <div class="file-name-info">
                <svg class="file-type-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                </svg>
                <span>${file.name} (Demo File)</span>
            </div>
            <button type="button" class="file-delete-btn" onclick="this.closest('.file-preview-item').remove(); alert('Chức năng xóa tệp demo');">Đã khóa</button>
        `;
        previewList.appendChild(item);
    });
    if (appState.transaction.uploadedFiles.length > 0) {
        previewList.classList.remove('hidden');
    }
    
    document.getElementById('tx-doc-notes').value = appState.transaction.docNotes;
}
