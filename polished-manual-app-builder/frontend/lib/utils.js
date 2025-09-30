// Utility functions for the frontend service

export function cn(...classes) {
    return classes.filter(Boolean).join(' ');
}

export function sanitizeAppName(name) {
    return name
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, '')
        .replace(/\s+/g, '-')
        .trim();
}

export function generateUniqueId() {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export function validateAppDescription(description) {
    if (!description || typeof description !== 'string') {
        return { valid: false, error: 'Description is required' };
    }
    
    if (description.length < 10) {
        return { valid: false, error: 'Description must be at least 10 characters' };
    }
    
    if (description.length > 1000) {
        return { valid: false, error: 'Description must be less than 1000 characters' };
    }
    
    return { valid: true };
}