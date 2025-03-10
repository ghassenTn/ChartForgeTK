
        class ChartBridge {
            constructor() {
                this.chart = null;
                this.ctx = document.querySelector('.chart-canvas').getContext('2d');
            }
            
            update(config) {
                if (this.chart) {
                    this.chart.destroy();
                }
                
                this.chart = new Chart(this.ctx, config);
            }
        }

        // Initialize bridge
        window.chartBridge = new ChartBridge();
        