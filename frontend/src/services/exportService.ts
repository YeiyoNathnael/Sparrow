// Export service for converting data to various formats

export interface RouteData {
  id: string;
  zone: string;
  driver: string;
  students: number;
  stops: number;
  startTime: string;
  status: string;
}

/**
 * Convert routes to CSV format
 */
export function exportToCSV(routes: RouteData[]): void {
  if (routes.length === 0) {
    alert('No data to export');
    return;
  }

  const headers = ['Route ID', 'Zone', 'Driver', 'Students', 'Stops', 'Start Time', 'Status'];
  const rows = routes.map(route => [
    route.id,
    route.zone,
    route.driver,
    route.students,
    route.stops,
    route.startTime,
    route.status
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  downloadFile(csvContent, `routes_${new Date().toISOString().split('T')[0]}.csv`, 'text/csv');
}

/**
 * Convert routes to JSON format
 */
export function exportToJSON(data: any): void {
  const jsonContent = JSON.stringify(data, null, 2);
  downloadFile(jsonContent, `data_${new Date().toISOString().split('T')[0]}.json`, 'application/json');
}

/**
 * Trigger browser print dialog
 */
export function printContent(element: HTMLElement | null, title: string = 'Document'): void {
  if (!element) {
    alert('No content to print');
    return;
  }

  const printWindow = window.open('', '_blank');
  if (!printWindow) {
    alert('Please allow popups to print');
    return;
  }

  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
      <head>
        <title>${title}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            color: #333;
            line-height: 1.6;
            margin: 20px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
          }
          th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
          }
          th {
            background-color: #d22030;
            color: white;
          }
          h1 {
            color: #d22030;
            border-bottom: 2px solid #d22030;
            padding-bottom: 10px;
          }
          .status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
          }
          .status.active {
            background-color: #10b981;
            color: white;
          }
          .status.pending {
            background-color: #f59e0b;
            color: white;
          }
          .status.delayed {
            background-color: #d22030;
            color: white;
          }
          .status.completed {
            background-color: #6b7280;
            color: white;
          }
          @media print {
            body {
              margin: 0;
            }
          }
        </style>
      </head>
      <body>
        <h1>${title}</h1>
        <p>Generated: ${new Date().toLocaleString()}</p>
        ${element.innerHTML}
      </body>
    </html>
  `);
  
  printWindow.document.close();
  printWindow.print();
}

/**
 * Create and trigger download of text file
 */
function downloadFile(content: string, filename: string, mimeType: string): void {
  const element = document.createElement('a');
  element.setAttribute('href', `data:${mimeType};charset=utf-8,${encodeURIComponent(content)}`);
  element.setAttribute('download', filename);
  element.style.display = 'none';
  
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

/**
 * Format coordinates as human readable
 */
export function formatCoordinates(lat: number, lng: number): string {
  return `${lat.toFixed(4)}°, ${lng.toFixed(4)}°`;
}

/**
 * Calculate distance between two coordinates (Haversine formula)
 */
export function calculateDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}
