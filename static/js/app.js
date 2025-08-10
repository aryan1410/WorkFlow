// Academic Project Tracker - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize application
    initializeApp();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize components
    initializeComponents();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Academic Project Tracker initialized');
    
    // Set current date for comparisons
    window.currentDate = new Date();
    
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
}

/**
 * Set up global event listeners
 */
function setupEventListeners() {
    // Form validation
    setupFormValidation();
    
    // Confirmation dialogs
    setupConfirmationDialogs();
    
    // Auto-save functionality
    setupAutoSave();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Loading states
    setupLoadingStates();
}

/**
 * Initialize Bootstrap and custom components
 */
function initializeComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-focus first form input
    const firstInput = document.querySelector('form input:not([type="hidden"]):not([readonly])');
    if (firstInput) {
        firstInput.focus();
    }
}

/**
 * Form validation setup
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Focus first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.checkValidity()) {
                    this.classList.remove('is-invalid');
                }
            });
        });
    });
}

/**
 * Confirmation dialog setup
 */
function setupConfirmationDialogs() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Delete confirmations
    const deleteButtons = document.querySelectorAll('button[type="submit"]');
    deleteButtons.forEach(function(button) {
        if (button.textContent.includes('Delete') && !button.hasAttribute('data-confirm')) {
            button.addEventListener('click', function(e) {
                const itemName = this.getAttribute('data-item-name') || 'this item';
                if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                    e.preventDefault();
                    return false;
                }
            });
        }
    });
}

/**
 * Auto-save functionality for forms
 */
function setupAutoSave() {
    const autoSaveForms = document.querySelectorAll('form[data-autosave]');
    
    autoSaveForms.forEach(function(form) {
        const formId = form.getAttribute('data-autosave') || 'default';
        const inputs = form.querySelectorAll('input, textarea, select');
        
        // Load saved data
        inputs.forEach(function(input) {
            const savedValue = localStorage.getItem(`autosave_${formId}_${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Save data on change
        inputs.forEach(function(input) {
            input.addEventListener('input', debounce(function() {
                localStorage.setItem(`autosave_${formId}_${input.name}`, input.value);
            }, 500));
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            inputs.forEach(function(input) {
                localStorage.removeItem(`autosave_${formId}_${input.name}`);
            });
        });
    });
}

/**
 * Keyboard shortcuts setup
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+N or Cmd+N for new project
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const newProjectBtn = document.querySelector('a[href*="project/new"]');
            if (newProjectBtn) {
                newProjectBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
        
        // Enter to submit forms (if not textarea)
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
            const form = e.target.closest('form');
            if (form && !e.target.closest('[data-no-enter-submit]')) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }
    });
}

/**
 * Loading states for buttons and forms
 */
function setupLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
    
    // Loading states for action buttons
    const actionButtons = document.querySelectorAll('[data-loading]');
    actionButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            this.classList.add('loading');
            this.disabled = true;
        });
    });
}

/**
 * Utility Functions
 */

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format date for display
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        ...options
    };
    
    return new Date(date).toLocaleDateString(undefined, defaultOptions);
}

/**
 * Format relative time (e.g., "2 days ago")
 */
function formatRelativeTime(date) {
    const now = new Date();
    const past = new Date(date);
    const diffTime = Math.abs(now - past);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.ceil(diffDays / 30)} months ago`;
    return `${Math.ceil(diffDays / 365)} years ago`;
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 4 seconds
    setTimeout(function() {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 4000);
}

/**
 * Calculate project progress
 */
function calculateProgress(completed, total) {
    if (total === 0) return 0;
    return Math.round((completed / total) * 100);
}

/**
 * Check if date is overdue
 */
function isOverdue(deadline, status = null) {
    if (!deadline) return false;
    if (status === 'Completed') return false;
    
    const now = new Date();
    const due = new Date(deadline);
    return due < now;
}

/**
 * Get status color class
 */
function getStatusColorClass(status) {
    const statusColors = {
        'Not Started': 'secondary',
        'In Progress': 'primary',
        'On Hold': 'warning',
        'Completed': 'success',
        'To Do': 'info',
        'Done': 'success'
    };
    
    return `bg-${statusColors[status] || 'secondary'}`;
}

/**
 * Get priority color class
 */
function getPriorityColorClass(priority) {
    const priorityColors = {
        'Low': 'info',
        'Medium': 'warning',
        'High': 'danger'
    };
    
    return `bg-${priorityColors[priority] || 'secondary'}`;
}

// Export functions for global use
window.ProjectTracker = {
    showNotification,
    formatDate,
    formatRelativeTime,
    calculateProgress,
    isOverdue,
    getStatusColorClass,
    getPriorityColorClass,
    debounce
};

// Page-specific initializations
if (window.location.pathname === '/') {
    // Dashboard specific code
    initializeDashboard();
} else if (window.location.pathname.includes('/project/')) {
    // Project detail specific code
    initializeProjectDetail();
}

function initializeDashboard() {
    // Update any real-time elements
    updateProjectCards();
}

function initializeProjectDetail() {
    // Initialize task management features
    setupTaskManagement();
}

function updateProjectCards() {
    // Update overdue indicators and progress bars
    const projectCards = document.querySelectorAll('[data-project-id]');
    projectCards.forEach(function(card) {
        // Add any real-time updates here
    });
}

function setupTaskManagement() {
    // Task-specific functionality
    const taskItems = document.querySelectorAll('.list-group-item[data-task-id]');
    taskItems.forEach(function(item) {
        // Add drag-and-drop or other task management features here
    });
}
