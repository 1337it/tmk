$(document).ready(function() {
    
    const ensureSidebar = () => {
        // If we are on workspace page, standard Frappe logic handles it.
        // But we need to ensure the persistent container exists for non-workspace pages.
        const workspaceRoute = 'Workspaces';
        if (frappe.get_route()[0] === workspaceRoute) return;

        let pageWorkspaces = $('#page-Workspaces');
        
        if (pageWorkspaces.length === 0) {
            console.log("TMK: creating #page-Workspaces container");
            // Create container attached to body to ensure it exists globally
            // We use display:none, but the custom CSS forces it visible via !important
            pageWorkspaces = $('<div id="page-Workspaces" style="display:none;" data-page-route="Workspaces"></div>');
            pageWorkspaces.appendTo('body');
            
            // Create sidebar wrapper inside it
            $('<div class="layout-side-section"></div>').appendTo(pageWorkspaces);
        }
        
        const sidebar = pageWorkspaces.find('.layout-side-section');
        
        // If sidebar is empty, populate it
        if (sidebar.length > 0 && sidebar.is(':empty')) {
            console.log("TMK: rendering custom sidebar items");
            renderCustomSidebar(sidebar);
        }
    };

    const renderCustomSidebar = (container) => {
        frappe.call('frappe.desk.desktop.get_workspace_sidebar_items').then(r => {
            if (!r.message || !r.message.pages) return;
            
            const items = r.message.pages;
            // Matches standard structure classes for CSS compatibility
            let html = '<div class="desk-sidebar list-unstyled sidebar-menu standard-sidebar-section">';
            
            items.forEach(item => {
                if (!item.public) return;
                
                const label = item.title || item.label || item.name;
                const name = item.name;
                const route = name; 
                
                // Determine if active based on current route
                // For non-workspace pages, nothing in sidebar should be "selected" usually, 
                // or we can select based on some logic if needed.
                const isActive = frappe.get_route()[0] === 'Workspaces' && frappe.get_route()[1] === name;
                
                html += `
                    <div class="sidebar-item-container ${isActive ? 'selected' : ''}" data-item-label="${label}">
                        <a href="/app/${route.toLowerCase().replace(/ /g, '-')}" class="item-anchor" title="${label}">
                            <span class="sidebar-item-icon" item-icon="${item.icon || 'folder'}"></span>
                            <span class="sidebar-item-label">${label}</span>
                        </a>
                    </div>
                `;
            });
            html += '</div>';
            container.html(html);
            
            // Bind click events to use Frappe router
            container.find('a').on('click', function(e) {
                e.preventDefault();
                const href = $(this).attr('href');
                // Extract route part
                const route = href.split('/app/')[1];
                frappe.set_route(route);
                
                // Visual update
                container.find('.sidebar-item-container').removeClass('selected');
                $(this).closest('.sidebar-item-container').addClass('selected');
            });
        });
    };

    // Run immediately
    ensureSidebar();
    
    // Run on route changes to re-check
    frappe.router.on('change', ensureSidebar);
});