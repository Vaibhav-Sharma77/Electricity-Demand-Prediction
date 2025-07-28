"""
Data Processor - Enhanced data processing and visualization utilities
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from datetime import datetime
import seaborn as sns

class DataProcessor:
    """Enhanced data processing for better visualizations and exports"""
    
    def __init__(self):
        self.colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
        plt.style.use('seaborn-v0_8')
        
    def create_enhanced_plot(self, hourly_predictions, selected_regions, selected_date):
        """Create enhanced visualization plot"""
        try:
            # Set up the figure with better styling
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Plot each region with different colors and styles
            for i, region in enumerate(selected_regions):
                hours = list(range(24))
                demands = [hourly_predictions[region][hour]['predicted_demand'] for hour in hours]
                
                color = self.colors[i % len(self.colors)]
                ax.plot(hours, demands, 
                       marker='o', 
                       label=region, 
                       linewidth=3,
                       color=color,
                       markersize=6,
                       markerfacecolor='white',
                       markeredgecolor=color,
                       markeredgewidth=2)
                
                # Add peak and minimum markers
                max_demand = max(demands)
                min_demand = min(demands)
                max_hour = demands.index(max_demand)
                min_hour = demands.index(min_demand)
                
                ax.annotate(f'Peak: {max_demand:.1f} MW', 
                           xy=(max_hour, max_demand), 
                           xytext=(max_hour, max_demand + 100),
                           arrowprops=dict(arrowstyle='->', color=color, alpha=0.7),
                           fontsize=9, 
                           ha='center',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.2))
            
            # Enhance the plot appearance
            ax.set_title(f'Electricity Demand Forecast - {selected_date}', 
                        fontsize=18, fontweight='bold', pad=20)
            ax.set_xlabel('Hour of Day', fontsize=14, fontweight='bold')
            ax.set_ylabel('Demand (MW)', fontsize=14, fontweight='bold')
            
            # Customize grid and ticks
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xticks(hours)
            ax.set_xticklabels([f'{h:02d}:00' for h in hours], rotation=45)
            
            # Add legend with better positioning
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                     frameon=True, fancybox=True, shadow=True)
            
            # Add background color
            ax.set_facecolor('#f8f9fa')
            
            # Improve layout
            plt.tight_layout()
            
            # Save the plot
            plot_filename = 'static/predicted_demand_plot.png'
            os.makedirs('static', exist_ok=True)
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            plt.close()
            
            return plot_filename
            
        except Exception as e:
            print(f"Error creating plot: {e}")
            return None
    
    def create_comparison_plot(self, predictions_data, regions):
        """Create comparison plot for multiple regions"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # Plot 1: Line chart
            for i, region in enumerate(regions):
                hours = list(range(24))
                demands = [predictions_data[region][hour] for hour in hours]
                color = self.colors[i % len(self.colors)]
                
                ax1.plot(hours, demands, marker='o', label=region, 
                        linewidth=2, color=color)
            
            ax1.set_title('Hourly Demand Comparison', fontsize=16, fontweight='bold')
            ax1.set_xlabel('Hour of Day', fontsize=12)
            ax1.set_ylabel('Demand (MW)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Heatmap
            heatmap_data = []
            for region in regions:
                demands = [predictions_data[region][hour] for hour in range(24)]
                heatmap_data.append(demands)
            
            heatmap_df = pd.DataFrame(heatmap_data, 
                                    columns=[f'{h:02d}:00' for h in range(24)],
                                    index=regions)
            
            sns.heatmap(heatmap_df, ax=ax2, annot=True, fmt='.0f', 
                       cmap='YlOrRd', cbar_kws={'label': 'Demand (MW)'})
            ax2.set_title('Demand Heatmap by Region and Hour', fontsize=16, fontweight='bold')
            
            plt.tight_layout()
            
            plot_filename = 'static/comparison_plot.png'
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            return plot_filename
            
        except Exception as e:
            print(f"Error creating comparison plot: {e}")
            return None
    
    def export_to_excel(self, predictions_data, selected_date, regions):
        """Export predictions to Excel file"""
        try:
            # Create DataFrame
            data = []
            for hour in range(24):
                row = {'Time': f'{hour:02d}:00'}
                for region in regions:
                    row[region] = predictions_data.get(region, {}).get(hour, 0)
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Export to Excel
            filename = f'static/forecast_{selected_date}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            os.makedirs('static', exist_ok=True)
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Hourly_Predictions', index=False)
                
                # Add statistics sheet
                stats_data = []
                for region in regions:
                    demands = [predictions_data.get(region, {}).get(hour, 0) for hour in range(24)]
                    stats_data.append({
                        'Region': region,
                        'Peak_Demand': max(demands),
                        'Min_Demand': min(demands),
                        'Avg_Demand': np.mean(demands),
                        'Total_Daily': sum(demands)
                    })
                
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            return filename
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return None
    
    def generate_summary_report(self, predictions_data, selected_date, regions):
        """Generate a comprehensive summary report"""
        try:
            report = {
                'date': selected_date,
                'regions': regions,
                'total_regions': len(regions),
                'regional_stats': {}
            }
            
            for region in regions:
                demands = [predictions_data.get(region, {}).get(hour, 0) for hour in range(24)]
                
                report['regional_stats'][region] = {
                    'peak_demand': max(demands),
                    'min_demand': min(demands),
                    'avg_demand': np.mean(demands),
                    'total_daily': sum(demands),
                    'peak_hour': demands.index(max(demands)),
                    'min_hour': demands.index(min(demands)),
                    'demand_variation': max(demands) - min(demands)
                }
            
            # Overall statistics
            all_demands = []
            for region in regions:
                demands = [predictions_data.get(region, {}).get(hour, 0) for hour in range(24)]
                all_demands.extend(demands)
            
            report['overall_stats'] = {
                'total_peak': max(all_demands),
                'total_avg': np.mean(all_demands),
                'total_daily': sum(all_demands),
                'regions_count': len(regions)
            }
            
            return report
            
        except Exception as e:
            print(f"Error generating summary report: {e}")
            return None
