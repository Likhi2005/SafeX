import React, { useEffect, useRef } from 'react';

const ThreatMap = ({ threats = [], className = '' }) => {
    const mapRef = useRef(null);
    const mapInstanceRef = useRef(null);
    const markersRef = useRef([]);

    useEffect(() => {
        // Initialize map when component mounts
        initializeMap();

        // Cleanup on unmount
        return () => {
            if (mapInstanceRef.current) {
                mapInstanceRef.current.remove();
            }
        };
    }, []);

    useEffect(() => {
        // Update markers when threats change
        if (mapInstanceRef.current) {
            updateThreatMarkers();
        }
    }, [threats]);

    const initializeMap = () => {
        // Check if Leaflet is available
        if (typeof window === 'undefined' || !window.L) {
            // Fallback to simple threat visualization
            return renderFallbackMap();
        }

        try {
            const L = window.L;
            
            // Initialize map
            const map = L.map(mapRef.current, {
                center: [40.7128, -74.0060], // NYC
                zoom: 2,
                zoomControl: true,
                scrollWheelZoom: false
            });

            // Add tile layer
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18
            }).addTo(map);

            mapInstanceRef.current = map;
            updateThreatMarkers();

        } catch (error) {
            console.warn('Failed to initialize Leaflet map:', error);
            renderFallbackMap();
        }
    };

    const updateThreatMarkers = () => {
        if (!mapInstanceRef.current || !window.L) return;

        const L = window.L;
        const map = mapInstanceRef.current;

        // Clear existing markers
        markersRef.current.forEach(marker => map.removeLayer(marker));
        markersRef.current = [];

        // Add new markers
        threats.forEach(threat => {
            if (threat.location && threat.location.lat && threat.location.lng) {
                const color = getSeverityColor(threat.severity);
                
                const marker = L.circleMarker([threat.location.lat, threat.location.lng], {
                    radius: Math.max(4, threat.risk_score * 12),
                    fillColor: color,
                    color: color,
                    weight: 2,
                    opacity: 0.8,
                    fillOpacity: 0.6
                });

                // Add popup with threat details
                const popupContent = `
                    <div class="text-sm">
                        <div class="font-semibold">${threat.attack_type || 'Unknown'}</div>
                        <div>Risk: ${(threat.risk_score * 100).toFixed(1)}%</div>
                        <div>Status: ${threat.blocked ? 'Blocked' : 'Allowed'}</div>
                        <div>Location: ${threat.country || 'Unknown'}</div>
                        <div class="text-xs text-gray-500">${new Date(threat.timestamp).toLocaleString()}</div>
                    </div>
                `;

                marker.bindPopup(popupContent);
                marker.addTo(map);
                markersRef.current.push(marker);
            }
        });
    };

    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical': return '#ef4444';
            case 'high': return '#f97316';
            case 'medium': return '#eab308';
            case 'low': return '#22c55e';
            default: return '#6b7280';
        }
    };

    const renderFallbackMap = () => {
        return (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-lg border border-border-color">
                <div className="text-center">
                    <div className="grid grid-cols-6 gap-2 max-w-md mx-auto mb-4">
                        {threats.slice(0, 18).map((threat, index) => (
                            <div
                                key={index}
                                className={`w-4 h-4 rounded-full animate-pulse`}
                                style={{
                                    backgroundColor: getSeverityColor(threat.severity),
                                    animationDelay: `${index * 0.1}s`
                                }}
                                title={`${threat.attack_type} - ${threat.country}`}
                            />
                        ))}
                    </div>
                    <p className="text-text-muted text-sm">
                        {threats.length} Global Threats Detected
                    </p>
                    <div className="mt-4 flex justify-center gap-4 text-xs">
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-red-500"></div>
                            <span>Critical</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                            <span>High</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                            <span>Medium</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                            <span>Low</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    // If Leaflet is not available, render fallback immediately
    if (typeof window !== 'undefined' && !window.L) {
        return (
            <div className={className}>
                {renderFallbackMap()}
            </div>
        );
    }

    return (
        <div className={`relative ${className}`}>
            <div 
                ref={mapRef} 
                className="w-full h-full rounded-lg"
                style={{ minHeight: '300px' }}
            />
            
            {/* Threat count overlay */}
            <div className="absolute top-4 left-4 bg-card-bg/90 backdrop-blur-sm rounded-lg px-3 py-2 border border-border-color">
                <div className="text-sm font-medium text-text-primary">
                    {threats.length} Active Threats
                </div>
                <div className="text-xs text-text-muted">
                    {threats.filter(t => t.blocked).length} Blocked
                </div>
            </div>

            {/* Legend */}
            <div className="absolute bottom-4 right-4 bg-card-bg/90 backdrop-blur-sm rounded-lg px-3 py-2 border border-border-color">
                <div className="text-xs font-medium text-text-primary mb-2">Threat Severity</div>
                <div className="space-y-1">
                    {[
                        { label: 'Critical', color: '#ef4444' },
                        { label: 'High', color: '#f97316' },
                        { label: 'Medium', color: '#eab308' },
                        { label: 'Low', color: '#22c55e' }
                    ].map(item => (
                        <div key={item.label} className="flex items-center gap-2 text-xs">
                            <div 
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: item.color }}
                            />
                            <span className="text-text-muted">{item.label}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ThreatMap;