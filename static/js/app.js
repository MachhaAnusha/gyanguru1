/**
 * GyanGuru - AI-Powered ML Learning Assistant
 * Main JavaScript Application
 */

// ============================================================================
// Mobile Navigation
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }
});

// ============================================================================
// Toast Notifications
// ============================================================================

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - Type of toast: 'success', 'error', or 'warning'
 * @param {number} duration - Duration in milliseconds (default: 4000)
 */
function showToast(message, type = 'success', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.success}</span>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
    
    // Click to dismiss
    toast.addEventListener('click', () => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    });
}

// ============================================================================
// API Helpers
// ============================================================================

/**
 * Make a POST request to the API
 * @param {string} endpoint - API endpoint URL
 * @param {object} data - Request body data
 * @returns {Promise<object>} Response data
 */
async function apiPost(endpoint, data) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    
    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.error || `HTTP error! status: ${response.status}`);
    }
    
    return result;
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {string} successMessage - Message to show on success
 */
async function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    try {
        await navigator.clipboard.writeText(text);
        showToast(successMessage, 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy to clipboard', 'error');
    }
}

/**
 * Format file size in human readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size string
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
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
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================================================
// Loading States
// ============================================================================

/**
 * Set button to loading state
 * @param {HTMLElement} button - Button element
 * @param {boolean} isLoading - Whether to show loading state
 */
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

// ============================================================================
// Smooth Scroll
// ============================================================================

/**
 * Smooth scroll to element
 * @param {HTMLElement} element - Element to scroll to
 * @param {string} behavior - Scroll behavior
 */
function scrollToElement(element, behavior = 'smooth') {
    if (element) {
        element.scrollIntoView({ behavior, block: 'start' });
    }
}

// ============================================================================
// Local Storage Helpers
// ============================================================================

/**
 * Save data to local storage
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
    }
}

/**
 * Get data from local storage
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key doesn't exist
 * @returns {any} Stored value or default
 */
function getFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Failed to get from localStorage:', e);
        return defaultValue;
    }
}

// ============================================================================
// History Management
// ============================================================================

/**
 * Add item to generation history
 * @param {string} type - Type of generation (text, code, audio, image)
 * @param {object} data - Generation data
 */
function addToHistory(type, data) {
    const history = getFromStorage('gyanguru_history', []);
    history.unshift({
        type,
        data,
        timestamp: new Date().toISOString()
    });
    // Keep only last 50 items
    saveToStorage('gyanguru_history', history.slice(0, 50));
}

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.querySelector('.generation-form');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                activeForm.dispatchEvent(new Event('submit'));
            }
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modal = document.querySelector('.fullscreen-modal.active');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
});

// ============================================================================
// Prism.js Enhancements
// ============================================================================

/**
 * Highlight code in an element
 * @param {HTMLElement} element - Element containing code
 */
function highlightCode(element) {
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(element);
    }
}

/**
 * Highlight all code blocks in a container
 * @param {HTMLElement} container - Container element
 */
function highlightAllCode(container) {
    if (typeof Prism !== 'undefined') {
        container.querySelectorAll('pre code').forEach(block => {
            Prism.highlightElement(block);
        });
    }
}

// ============================================================================
// Marked.js Configuration
// ============================================================================

if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true,
        gfm: true,
        highlight: function(code, lang) {
            if (typeof Prism !== 'undefined' && Prism.languages[lang]) {
                return Prism.highlight(code, Prism.languages[lang], lang);
            }
            return code;
        }
    });
}

// ============================================================================
// Error Handling
// ============================================================================

/**
 * Handle API errors
 * @param {Error} error - Error object
 */
function handleApiError(error) {
    console.error('API Error:', error);
    
    let message = error.message || 'An unexpected error occurred';
    
    // Handle specific error cases
    if (message.includes('API key')) {
        message = 'API key not configured. Please set your Gemini API key.';
    } else if (message.includes('rate limit') || message.includes('429')) {
        message = 'Rate limit exceeded. Please wait a moment and try again.';
    } else if (message.includes('network') || message.includes('fetch')) {
        message = 'Network error. Please check your connection.';
    }
    
    showToast(message, 'error', 6000);
}

// ============================================================================
// Page Visibility API
// ============================================================================

document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Pause any ongoing operations when page is hidden
        console.log('Page hidden - pausing operations');
    } else {
        // Resume operations when page becomes visible
        console.log('Page visible - resuming operations');
    }
});

// ============================================================================
// Console Welcome Message
// ============================================================================

console.log(
    '%c🧠 GyanGuru - AI-Powered ML Learning Assistant',
    'font-size: 18px; font-weight: bold; color: #3b82f6;'
);
console.log(
    '%cPowered by Google Gemini AI',
    'font-size: 12px; color: #8b5cf6;'
);
