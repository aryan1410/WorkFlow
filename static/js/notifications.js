// Desktop Notifications for Academic Project Tracker
// Provides study session reminders, deadline alerts, and task completion notifications

class NotificationManager {
    constructor() {
        this.permission = Notification.permission;
        this.enabled = false;
        this.init();
    }

    async init() {
        // Check if notifications are supported
        if (!('Notification' in window)) {
            console.log('Desktop notifications not supported');
            return;
        }

        // Request permission if needed
        if (this.permission === 'default') {
            this.permission = await Notification.requestPermission();
        }

        this.enabled = this.permission === 'granted';
        
        if (this.enabled) {
            console.log('Desktop notifications enabled');
        }
    }

    canNotify() {
        return this.enabled && 'Notification' in window;
    }

    show(title, options = {}) {
        if (!this.canNotify()) return null;

        const defaultOptions = {
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico',
            tag: 'academic-tracker',
            ...options
        };

        const notification = new Notification(title, defaultOptions);
        
        // Auto-close after 8 seconds
        setTimeout(() => notification.close(), 8000);
        
        return notification;
    }

    // Study session notifications
    showStudyReminder(message, duration) {
        return this.show(`📚 Study Session - ${duration}`, {
            body: message,
            tag: 'study-session',
            requireInteraction: true
        });
    }

    showStudyComplete(duration) {
        return this.show('🎉 Study Session Complete!', {
            body: `Great work! You studied for ${duration}.`,
            tag: 'study-complete'
        });
    }

    // Deadline notifications
    showDeadlineAlert(project, daysLeft) {
        const urgency = daysLeft <= 1 ? '🚨' : daysLeft <= 3 ? '⚠️' : '📅';
        const dayText = daysLeft === 1 ? 'day' : 'days';
        
        return this.show(`${urgency} Project Deadline`, {
            body: `"${project}" is due in ${daysLeft} ${dayText}!`,
            tag: 'deadline-alert',
            requireInteraction: daysLeft <= 1
        });
    }

    // Task completion notification
    showTaskComplete(taskName) {
        return this.show('✅ Task Completed', {
            body: `Great work! "${taskName}" is now complete.`,
            tag: 'task-complete'
        });
    }

    // Project completion notification
    showProjectComplete(projectName) {
        return this.show('🏆 Project Completed!', {
            body: `Congratulations! "${projectName}" has been completed.`,
            tag: 'project-complete',
            requireInteraction: true
        });
    }

    // Collaboration notifications
    showCollaboratorInvite(projectName, inviterName) {
        return this.show('👥 New Collaboration Invite', {
            body: `${inviterName} invited you to collaborate on "${projectName}"`,
            tag: 'collaboration'
        });
    }

    showNewComment(projectName, commenterName) {
        return this.show('💬 New Comment', {
            body: `${commenterName} commented on "${projectName}"`,
            tag: 'comment'
        });
    }
}

// Study Session Timer with Notifications
class StudySessionNotifier {
    constructor(notificationManager) {
        this.notifications = notificationManager;
        this.sessionTimer = null;
        this.reminderIntervals = [];
        this.sessionStart = null;
        this.projectName = '';
        this.isActive = false;
    }

    startSession(projectName) {
        this.projectName = projectName || 'General Study';
        this.sessionStart = Date.now();
        this.isActive = true;
        this.clearAllTimers();

        // Show start notification
        this.notifications.show('🚀 Study Session Started', {
            body: `Started studying "${this.projectName}". Good luck!`,
            tag: 'session-start'
        });

        // Set up reminders every 25 minutes (Pomodoro technique)
        const pomodoroReminder = setInterval(() => {
            if (!this.isActive) return;
            
            const elapsed = Math.floor((Date.now() - this.sessionStart) / 60000);
            if (elapsed > 0 && elapsed % 25 === 0) {
                this.notifications.showStudyReminder(
                    `You've been studying "${this.projectName}" for ${elapsed} minutes. Consider a 5-minute break!`,
                    `${elapsed} minutes`
                );
            }
        }, 60000); // Check every minute

        // Set up break reminder after 50 minutes
        const breakReminder = setTimeout(() => {
            if (this.isActive) {
                this.notifications.show('☕ Break Time!', {
                    body: `You've been studying for 50 minutes. Time for a longer break!`,
                    tag: 'break-reminder',
                    requireInteraction: true
                });
            }
        }, 50 * 60 * 1000); // 50 minutes

        this.reminderIntervals.push(pomodoroReminder);
        this.reminderIntervals.push(breakReminder);
    }

    stopSession() {
        if (!this.isActive) return;

        this.isActive = false;
        this.clearAllTimers();

        if (this.sessionStart) {
            const duration = Math.floor((Date.now() - this.sessionStart) / 60000);
            const hours = Math.floor(duration / 60);
            const minutes = duration % 60;
            
            let durationText = '';
            if (hours > 0) {
                durationText = `${hours}h ${minutes}m`;
            } else {
                durationText = `${minutes} minutes`;
            }
            
            this.notifications.showStudyComplete(durationText);
        }

        this.sessionStart = null;
        this.projectName = '';
    }

    pauseSession() {
        this.isActive = false;
        this.clearAllTimers();
        
        this.notifications.show('⏸️ Study Session Paused', {
            body: 'Session paused. Resume when you\'re ready!',
            tag: 'session-pause'
        });
    }

    resumeSession() {
        if (!this.sessionStart) return;
        
        this.isActive = true;
        this.notifications.show('▶️ Study Session Resumed', {
            body: `Back to studying "${this.projectName}"!`,
            tag: 'session-resume'
        });
    }

    clearAllTimers() {
        this.reminderIntervals.forEach(timer => {
            if (typeof timer === 'number') {
                clearInterval(timer);
                clearTimeout(timer);
            }
        });
        this.reminderIntervals = [];
    }
}

// Deadline Monitor
class DeadlineMonitor {
    constructor(notificationManager) {
        this.notifications = notificationManager;
        this.checkInterval = null;
    }

    startMonitoring() {
        // Check deadlines every hour
        this.checkInterval = setInterval(() => {
            this.checkUpcomingDeadlines();
        }, 60 * 60 * 1000);

        // Initial check after 5 seconds to not overwhelm on page load
        setTimeout(() => this.checkUpcomingDeadlines(), 5000);
    }

    stopMonitoring() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    checkUpcomingDeadlines() {
        const deadlineElements = document.querySelectorAll('[data-deadline]');
        const now = new Date();
        
        deadlineElements.forEach(element => {
            const deadline = new Date(element.dataset.deadline);
            const projectName = element.dataset.projectName || 'Project';
            const status = element.dataset.status || '';
            
            // Skip completed projects
            if (status.toLowerCase() === 'completed') return;
            
            const timeDiff = deadline - now;
            const daysLeft = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
            
            // Alert for projects due in 3 days or less, but not overdue
            if (daysLeft <= 3 && daysLeft > 0) {
                this.notifications.showDeadlineAlert(projectName, daysLeft);
            }
        });
    }
}

// Initialize notification system
let notificationManager;
let studyNotifier;
let deadlineMonitor;

// Test notification function for debugging
function testNotification() {
    if (Notification.permission === 'granted') {
        new Notification('🧪 Test Notification', {
            body: 'Desktop notifications are working correctly!',
            icon: '/static/favicon.ico'
        });
    } else {
        console.log('Notifications not enabled. Permission:', Notification.permission);
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize notification system
    notificationManager = new NotificationManager();
    studyNotifier = new StudySessionNotifier(notificationManager);
    deadlineMonitor = new DeadlineMonitor(notificationManager);
    
    // Wait for initialization to complete
    await notificationManager.init();
    
    // Start deadline monitoring
    deadlineMonitor.startMonitoring();
    
    // Show permission prompt for new users after page loads
    setTimeout(() => {
        if (Notification.permission === 'default') {
            showNotificationPermissionPrompt();
        }
    }, 2000);
    
    // Add notification integration to existing functionality
    integrateWithExistingFeatures();
});

// User-friendly notification permission prompt
function showNotificationPermissionPrompt() {
    // Don't show if already shown or dismissed
    if (document.querySelector('.notification-prompt') || localStorage.getItem('notifications_dismissed')) {
        return;
    }
    
    const promptHtml = `
        <div class="alert alert-primary alert-dismissible fade show notification-prompt position-fixed" 
             style="top: 20px; left: 50%; transform: translateX(-50%); z-index: 1050; max-width: 500px;" role="alert">
            <div class="d-flex align-items-start">
                <i data-feather="bell" class="me-2 mt-1" style="width: 20px; height: 20px;"></i>
                <div class="flex-grow-1">
                    <h6 class="alert-heading mb-2">🔔 Enable Desktop Notifications</h6>
                    <p class="mb-2 small">Stay on top of your studies with notifications for:</p>
                    <ul class="mb-3 small">
                        <li>Study session reminders every 25 minutes</li>
                        <li>Project deadlines (3 days before due)</li>
                        <li>Task completion celebrations</li>
                        <li>Break reminders after long study sessions</li>
                    </ul>
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-primary btn-sm" onclick="enableNotifications()">
                            <i data-feather="check" style="width: 14px; height: 14px;" class="me-1"></i>
                            Enable Notifications
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="dismissNotificationPrompt()">
                            Maybe Later
                        </button>
                    </div>
                </div>
                <button type="button" class="btn-close btn-sm" onclick="dismissNotificationPrompt()"></button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('afterbegin', promptHtml);
    
    // Replace feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    console.log('Notification permission prompt shown');
}

async function enableNotifications() {
    console.log('Enabling notifications...');
    
    try {
        // Request permission
        const permission = await Notification.requestPermission();
        console.log('Permission result:', permission);
        
        if (permission === 'granted') {
            // Update notification manager
            notificationManager.permission = permission;
            notificationManager.enabled = true;
            
            // Show success notification
            const notification = new Notification('🔔 Notifications Enabled!', {
                body: 'You\'ll now receive study reminders and deadline alerts.',
                icon: '/static/favicon.ico'
            });
            
            setTimeout(() => notification.close(), 5000);
            
            console.log('Notifications enabled successfully');
        } else {
            console.log('Notification permission denied');
        }
    } catch (error) {
        console.error('Error enabling notifications:', error);
    }
    
    dismissNotificationPrompt();
}

function dismissNotificationPrompt() {
    const prompt = document.querySelector('.notification-prompt');
    if (prompt) {
        prompt.remove();
    }
    
    // Remember dismissal for this session
    localStorage.setItem('notifications_dismissed', 'true');
    console.log('Notification prompt dismissed');
}

// Integrate notifications with existing features
function integrateWithExistingFeatures() {
    // Override existing task completion handler
    const originalUpdateTaskStatus = window.updateTaskStatus;
    if (typeof originalUpdateTaskStatus === 'function') {
        window.updateTaskStatus = function(taskId, taskName, isCompleted) {
            // Call original function
            originalUpdateTaskStatus(taskId, taskName, isCompleted);
            
            // Add notification
            if (isCompleted && notificationManager.canNotify()) {
                notificationManager.showTaskComplete(taskName);
            }
        };
    }
    
    // Add notifications to study timer if it exists
    if (window.studyNotifier) {
        const originalStart = window.studyNotifier.startSession;
        const originalStop = window.studyNotifier.stopSession;
        
        if (originalStart) {
            window.studyNotifier.startSession = function(projectName) {
                originalStart.call(this, projectName);
                studyNotifier.startSession(projectName);
            };
        }
        
        if (originalStop) {
            window.studyNotifier.stopSession = function() {
                originalStop.call(this);
                studyNotifier.stopSession();
            };
        }
    }
}

// Export to global scope
window.notificationManager = notificationManager;
window.studyNotifier = studyNotifier;
window.deadlineMonitor = deadlineMonitor;
window.enableNotifications = enableNotifications;
window.dismissNotificationPrompt = dismissNotificationPrompt;
window.testNotification = testNotification;

console.log('Desktop notifications system loaded');