/**
 * Dashboard JavaScript - Business analytics and charts
 * Demonstrates Chart.js integration and real-time data visualization
 */

// Dashboard controller
class DashboardController {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    /**
     * Initialize dashboard
     */
    async init() {
        try {
            await this.loadDashboardData();
            this.initializeCharts();
            this.setupEventListeners();
            this.startAutoRefresh();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            Utils.showToast('Failed to load dashboard data', 'error');
        }
    }

    /**
     * Load dashboard data from API
     */
    async loadDashboardData() {
        try {
            const [
                dashboardData,
                salesData,
                ordersData,
                inventoryData
            ] = await Promise.all([
                ApiService.get('/analytics/dashboard'),
                ApiService.get('/analytics/sales'),
                ApiService.get('/analytics/orders'),
                ApiService.get('/analytics/inventory')
            ]);

            this.updateMetricCards(dashboardData);
            this.updateRecentOrders();
            this.updateInventoryAlerts(inventoryData);
            this.updateCharts(salesData, ordersData);
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            throw error;
        }
    }

    /**
     * Update metric cards
     */
    updateMetricCards(data) {
        const elements = {
            totalCustomers: document.getElementById('totalCustomers'),
            totalRevenue: document.getElementById('totalRevenue'),
            totalProducts: document.getElementById('totalProducts'),
            pendingOrders: document.getElementById('pendingOrders')
        };

        elements.totalCustomers.textContent = Utils.formatNumber(data.overview.total_customers);
        elements.totalRevenue.textContent = Utils.formatCurrency(data.revenue.total_revenue);
        elements.totalProducts.textContent = Utils.formatNumber(data.overview.total_products);
        elements.pendingOrders.textContent = Utils.formatNumber(data.overview.pending_orders);
    }

    /**
     * Update recent orders table
     */
    async updateRecentOrders() {
        try {
            const data = await ApiService.get('/orders/recent');
            const tableBody = document.querySelector('#recentOrdersTable tbody');
            
            DOMUtils.clearContent(tableBody);

            if (data.orders.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td colspan="5" class="text-center text-muted">
                        No recent orders found
                    </td>
                `;
                tableBody.appendChild(row);
                return;
            }

            data.orders.forEach(order => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>
                        <a href="/orders/${order.id}" class="text-decoration-none">
                            ${order.order_number}
                        </a>
                    </td>
                    <td>${order.customer_name || 'N/A'}</td>
                    <td>
                        <span class="badge status-${order.status.toLowerCase()}">
                            ${order.status}
                        </span>
                    </td>
                    <td>${Utils.formatCurrency(order.total_amount)}</td>
                    <td>${Utils.formatDate(order.created_at)}</td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            console.error('Failed to load recent orders:', error);
            const tableBody = document.querySelector('#recentOrdersTable tbody');
            DOMUtils.clearContent(tableBody);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        Failed to load recent orders
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Update inventory alerts
     */
    updateInventoryAlerts(data) {
        const alertsContainer = document.getElementById('inventoryAlerts');
        DOMUtils.clearContent(alertsContainer);

        if (data.low_stock_alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <p>No inventory alerts</p>
                </div>
            `;
            return;
        }

        data.low_stock_alerts.forEach(product => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-low-stock alert-dismissible fade show';
            alert.innerHTML = `
                <strong>${product.name}</strong> (${product.sku})<br>
                <small>Stock: ${product.current_stock} | Threshold: ${product.threshold}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            alertsContainer.appendChild(alert);
        });
    }

    /**
     * Initialize charts
     */
    initializeCharts() {
        // Sales chart
        const salesCtx = document.getElementById('salesChart').getContext('2d');
        this.charts.sales = new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Revenue',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return Utils.formatCurrency(value);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Order status chart
        const orderStatusCtx = document.getElementById('orderStatusChart').getContext('2d');
        this.charts.orderStatus = new Chart(orderStatusCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#FFC107',
                        '#17A2B8',
                        '#6F42C1',
                        '#28A745',
                        '#DC3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    /**
     * Update charts with new data
     */
    updateCharts(salesData, ordersData) {
        // Update sales chart
        this.charts.sales.data.labels = salesData.sales_trend.map(item => 
            Utils.formatDate(item.period)
        );
        this.charts.sales.data.datasets[0].data = salesData.sales_trend.map(item => 
            item.revenue
        );
        this.charts.sales.update();

        // Update order status chart
        this.charts.orderStatus.data.labels = ordersData.status_distribution.map(item => 
            item.status
        );
        this.charts.orderStatus.data.datasets[0].data = ordersData.status_distribution.map(item => 
            item.count
        );
        this.charts.orderStatus.update();
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Refresh button
        const refreshButton = document.querySelector('[onclick="refreshDashboard()"]');
        if (refreshButton) {
            refreshButton.onclick = () => this.refresh();
        }

        // Export button
        const exportButton = document.querySelector('[onclick="exportData()"]');
        if (exportButton) {
            exportButton.onclick = () => this.exportData();
        }

        // Sales chart period selector
        const salesPeriodLinks = document.querySelectorAll('[onclick^="updateSalesChart"]');
        salesPeriodLinks.forEach(link => {
            link.onclick = (e) => {
                e.preventDefault();
                const period = link.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.updateSalesChart(period);
            };
        });
    }

    /**
     * Update sales chart for different periods
     */
    async updateSalesChart(period) {
        try {
            const salesData = await ApiService.get('/analytics/sales', { period });
            
            this.charts.sales.data.labels = salesData.sales_trend.map(item => 
                Utils.formatDate(item.period)
            );
            this.charts.sales.data.datasets[0].data = salesData.sales_trend.map(item => 
                item.revenue
            );
            this.charts.sales.update();

            // Update dropdown button text
            const dropdownButton = document.getElementById('salesPeriodDropdown');
            dropdownButton.textContent = period.charAt(0).toUpperCase() + period.slice(1);
        } catch (error) {
            console.error('Failed to update sales chart:', error);
            Utils.showToast('Failed to update sales chart', 'error');
        }
    }

    /**
     * Refresh dashboard data
     */
    async refresh() {
        const refreshButton = document.querySelector('[onclick="refreshDashboard()"]');
        const originalText = refreshButton.innerHTML;
        
        try {
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
            refreshButton.disabled = true;
            
            await this.loadDashboardData();
            Utils.showToast('Dashboard refreshed successfully', 'success');
        } catch (error) {
            console.error('Failed to refresh dashboard:', error);
            Utils.showToast('Failed to refresh dashboard', 'error');
        } finally {
            refreshButton.innerHTML = originalText;
            refreshButton.disabled = false;
        }
    }

    /**
     * Export dashboard data
     */
    async exportData() {
        try {
            const data = await ApiService.get('/analytics/dashboard');
            const jsonData = JSON.stringify(data, null, 2);
            
            const blob = new Blob([jsonData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `dashboard-data-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            Utils.showToast('Dashboard data exported successfully', 'success');
        } catch (error) {
            console.error('Failed to export data:', error);
            Utils.showToast('Failed to export data', 'error');
        }
    }

    /**
     * Start auto refresh
     */
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000); // Refresh every 5 minutes
    }

    /**
     * Stop auto refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Global functions for backward compatibility
window.refreshDashboard = () => {
    if (window.dashboardController) {
        window.dashboardController.refresh();
    }
};

window.exportData = () => {
    if (window.dashboardController) {
        window.dashboardController.exportData();
    }
};

window.updateSalesChart = (period) => {
    if (window.dashboardController) {
        window.dashboardController.updateSalesChart(period);
    }
};

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardController = new DashboardController();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboardController) {
        window.dashboardController.stopAutoRefresh();
    }
}); 