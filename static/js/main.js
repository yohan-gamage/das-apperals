// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function(flash) {
        setTimeout(function() {
            flash.style.transition = 'opacity 0.5s';
            flash.style.opacity = '0';
            setTimeout(function() { flash.remove(); }, 500);
        }, 4000);
    });

    // Animate stat numbers
    document.querySelectorAll('.stat-value').forEach(function(el) {
        const target = parseInt(el.textContent);
        if (isNaN(target)) return;
        let current = 0;
        const step = Math.ceil(target / 20);
        const timer = setInterval(function() {
            current = Math.min(current + step, target);
            el.textContent = current;
            if (current >= target) clearInterval(timer);
        }, 40);
    });

    // Animate report bars
    document.querySelectorAll('.report-bar').forEach(function(bar) {
        const targetWidth = bar.style.width;
        bar.style.width = '0';
        setTimeout(function() {
            bar.style.transition = 'width 0.8s ease';
            bar.style.width = targetWidth;
        }, 200);
    });
});
